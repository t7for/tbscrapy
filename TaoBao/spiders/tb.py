import scrapy
from TaoBao.items import ProductItem
from TaoBao.items import ProductReviewItem



# product_spider.py
class TbSpider(scrapy.Spider):
    name = "tb"
    allowed_domains = ["www.taobao.com"]
    start_urls = ["https://www.taobao.com/"]

    def parse(self, response):
        # 解析商品列表
        for product in response.css('.product-item'):
            item = ProductItem()
            item['platform'] = 'example'
            item['product_id'] = product.css('::attr(data-id)').get()
            item['title'] = product.css('.title::text').get().strip()
            item['price'] = float(product.css('.price::text').get().replace('¥', ''))
            item['sales_volume'] = int(product.css('.sales::text').re_first(r'(\d+)'))
            
            # 请求商品详情页
            detail_url = response.urljoin(product.css('a::attr(href)').get())
            yield scrapy.Request(
                detail_url,
                callback=self.parse_detail,
                meta={'item': item}
            )
            
        # 处理分页
        next_page = response.css('.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

# detail_spider.py
class DetailSpider(scrapy.Spider):
    name = "details"
    
    def parse(self, response):
        item = response.meta['item']
        detail_item = ProductReviewItem(item)
        
        # 解析详情页数据
        detail_item['brand'] = response.css('.brand::text').get()
        detail_item['category'] = ' > '.join(response.css('.breadcrumb a::text').getall()[1:])
        detail_item['rating'] = float(response.css('.rating::text').get())
        detail_item['review_count'] = int(response.css('.review-count::text').re_first(r'(\d+)'))
        
        # 请求评论API
        review_api = f"https://example.com/api/reviews?product_id={detail_item['product_id']}"
        yield scrapy.Request(
            review_api,
            callback=self.parse_reviews,
            meta={'detail_item': detail_item}
        )
