from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def run_spiders():
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    
    # 依次运行商品爬虫和评论爬虫
    process.crawl('products')
    process.crawl('reviews')
    
    process.start()

if __name__ == '__main__':
    run_spiders()
