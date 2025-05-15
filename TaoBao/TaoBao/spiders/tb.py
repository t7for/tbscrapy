import scrapy
from TaoBao.items import ProductReviewItem,ProductItem

class TbSpider(scrapy.Spider):
    name = "tb"
    allowed_domains = ["www.taobao.com"]
    start_urls = ["https://www.taobao.com/"]

    def parse(self, response):
        # 使用XPath选择商品列表项
        for product in response.xpath('//div[contains(@class, "product-item")]'):
            item = ProductItem()
            item['platform'] = 'Taobao'
            item['product_id'] = product.xpath('@data-id').get()
            item['title'] = product.xpath('.//div[contains(@class, "title")]/text()').get().strip()
            item['price'] = float(product.xpath('.//div[contains(@class, "price")]/text()').get().replace('¥', ''))
            item['sales_volume'] = int(product.xpath('.//div[contains(@class, "sales")]/text()').re_first(r'(\d+)'))
            
            # 请求商品详情页
            detail_url = response.urljoin(product.xpath('.//a/@href').get())
            yield scrapy.Request(
                detail_url,
                callback=self.parse_detail,
                meta={'item': item}
            )
            
        # 处理分页
        next_page = response.xpath('//a[contains(@class, "next-page")]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_detail(self, response):
        item = response.meta['item']
        
        # 使用XPath解析详情页数据
        item['brand'] = response.xpath('//div[contains(@class, "brand")]/text()').get()
        item['category'] = ' > '.join(response.xpath('//div[contains(@class, "breadcrumb")]//a/text()').getall()[1:])
        item['rating'] = float(response.xpath('//div[contains(@class, "rating")]/text()').get())
        item['review_count'] = int(response.xpath('//div[contains(@class, "review-count")]/text()').re_first(r'(\d+)'))
        
        # 请求评论API
        review_api = f"https://example.com/api/reviews?product_id={item['product_id']}"
        yield scrapy.Request(
            review_api,
            callback=self.parse_reviews,
            meta={'item': item}
        )

    def parse_reviews(self, response):
        item = response.meta['item']
        # 解析评论数据（保持原逻辑不变）
        reviews = response.json().get('reviews', [])
        for review in reviews:
            review_item = ProductReviewItem()
            review_item['product_id'] = item['product_id']
            review_item['review_id'] = review.get('review_id')
            review_item['user_id'] = review.get('user_id')
            review_item['user_name'] = review.get('user_name')
            review_item['content'] = review.get('content')
            review_item['rating'] = review.get('rating')
            review_item['review_time'] = review.get('review_time')
            review_item['helpful_count'] = review.get('helpful_count')
            review_item['crawl_time'] = self.get_current_time()
            yield review_item

    def get_current_time(self):
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")