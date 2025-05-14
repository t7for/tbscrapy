import scrapy


class TbdetailSpider(scrapy.Spider):
    name = "tbdetail"
    allowed_domains = ["www.taobao.com"]
    start_urls = ["https://www.taobao.com"]

    def parse(self, response):
        pass
