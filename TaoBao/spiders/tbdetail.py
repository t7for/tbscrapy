import scrapy
from TaoBao.items import ProductReviewItem

class TbdetailSpider(scrapy.Spider):
    name = "tbdetail"
    allowed_domains = ["www.taobao.com"]

    def start_requests(self):
        # 接收来自 tb 爬虫的请求
        while True:
            try:
                request = self.crawler.engine.slot.inprogress.pop(0)
                if request.url.startswith('tbdetail://'):
                    product_id = request.url.split('://')[1].split('?')[0]
                    detail_url = request.url.split('?url=')[1]
                    item = request.meta['item']
                    yield scrapy.Request(
                        detail_url,
                        callback=self.parse,
                        meta={'item': item, 'product_id': product_id}
                    )
            except IndexError:
                break

    def parse(self, response):
        item = response.meta['item']
        product_id = response.meta['product_id']

        # 解析详情页数据
        item['brand'] = response.css('.brand::text').get()
        item['category'] = ' > '.join(response.css('.breadcrumb a::text').getall()[1:])
        item['rating'] = float(response.css('.rating::text').get())
        item['review_count'] = int(response.css('.review-count::text').re_first(r'(\d+)'))

        # 解析评论数据
        reviews = response.css('.review-item')
        for review in reviews:
            review_item = ProductReviewItem()
            review_item['product_id'] = product_id
            review_item['review_id'] = review.css('::attr(data-review-id)').get()
            review_item['user_id'] = review.css('.user-id::text').get()
            review_item['user_name'] = review.css('.user-name::text').get()
            review_item['content'] = review.css('.review-content::text').get()
            review_item['rating'] = float(review.css('.review-rating::text').get())
            review_item['review_time'] = review.css('.review-time::text').get()
            review_item['helpful_count'] = int(review.css('.helpful-count::text').re_first(r'(\d+)'))
            review_item['crawl_time'] = self.get_current_time()
            yield review_item

        yield item

    def get_current_time(self):
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")