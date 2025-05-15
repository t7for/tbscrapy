import scrapy
from TaoBao.items import ProductItem

class TbSpider(scrapy.Spider):
    name = "tb"
    allowed_domains = ["www.taobao.com"]
    start_urls = ["https://www.taobao.com/"]

    def parse(self, response):
        # 解析商品列表
        for product in response.css('.product-item'):
            item = ProductItem()
            item['platform'] = 'Taobao'
            item['product_id'] = product.css('::attr(data-id)').get()
            item['title'] = product.css('.title::text').get().strip()
            item['price'] = float(product.css('.price::text').get().replace('¥', ''))
            item['sales_volume'] = int(product.css('.sales::text').re_first(r'(\d+)'))

            # 请求商品详情页
            detail_url = response.urljoin(product.css('a::attr(href)').get())
            yield scrapy.Request(
                detail_url,
                callback=self.parse_detail_url,
                meta={'item': item}
            )

        # 处理分页
        next_page = response.css('.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_detail_url(self, response):
        item = response.meta['item']
        # 可以在这里添加一些对详情页URL的预处理逻辑
        # 比如处理重定向、拼接参数等
        yield scrapy.Request(
            response.url,
            callback=self.send_to_tbdetail,
            meta={'item': item}
        )

    def send_to_tbdetail(self, response):
        item = response.meta['item']
        # 将商品ID和详情页URL传递给 tbdetail 爬虫
        tbdetail_url = f"tbdetail://{item['product_id']}?url={response.url}"
        yield scrapy.Request(
            tbdetail_url,
            callback=None,  # 这里不需要回调函数，因为 tbdetail 爬虫会处理
            meta={'item': item}
        )