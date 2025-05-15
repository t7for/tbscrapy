import scrapy
from TaoBao.items import ProductItem, ProductReviewItem

class TbdetailSpider(scrapy.Spider):
    name = "tbdetail"
    allowed_domains = ["www.taobao.com"]
    start_urls = ["https://www.taobao.com"]

    def parse(self, response):
        # 使用XPath解析商品详情页
        item = ProductItem()
        item['platform'] = 'Taobao'
        item['product_id'] = response.xpath('//div[contains(@class, "product-info")]/@data-id').get()
        item['title'] = response.xpath('//h1[contains(@class, "title")]/text()').get().strip()
        item['price'] = float(response.xpath('//span[contains(@class, "price")]/text()').get().replace('¥', ''))
        item['sales_volume'] = int(response.xpath('//div[contains(@class, "sales")]/text()').re_first(r'(\d+)'))
        item['brand'] = response.xpath('//div[contains(@class, "brand")]/a/text()').get()
        item['category'] = ' > '.join(response.xpath('//div[contains(@class, "breadcrumb")]//a/text()').getall()[1:])
        item['rating'] = float(response.xpath('//div[contains(@class, "rating")]/text()').get())
        item['review_count'] = int(response.xpath('//div[contains(@class, "review-count")]/text()').re_first(r'(\d+)'))
        item['crawl_time'] = self.get_current_time()
        yield item

        # 使用XPath解析评论数据
        reviews = response.xpath('//div[contains(@class, "review-item")]')
        for review in reviews:
            review_item = ProductReviewItem()
            review_item['product_id'] = item['product_id']
            review_item['review_id'] = review.xpath('@data-review-id').get()
            review_item['user_id'] = review.xpath('.//div[contains(@class, "user-id")]/text()').get()
            review_item['user_name'] = review.xpath('.//div[contains(@class, "user-name")]/text()').get()
            review_item['content'] = review.xpath('.//div[contains(@class, "review-content")]/text()').get()
            review_item['rating'] = float(review.xpath('.//div[contains(@class, "review-rating")]/text()').get())
            review_item['review_time'] = review.xpath('.//div[contains(@class, "review-time")]/text()').get()
            review_item['helpful_count'] = int(review.xpath('.//div[contains(@class, "helpful-count")]/text()').re_first(r'(\d+)'))
            review_item['crawl_time'] = self.get_current_time()
            yield review_item

    def get_current_time(self):
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")