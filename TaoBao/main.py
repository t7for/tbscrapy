from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def run_spiders():
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    
    # 依次运行 tb 和 tbdetail 爬虫
    process.crawl('tb')
    process.crawl('tbdetail')
    
    process.start()

if __name__ == '__main__':
    run_spiders()