import requests
import random
from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class ProxyPoolMiddleware:
    def __init__(self, proxy_api):
        self.proxy_api = proxy_api
        self.proxies = self._get_proxies()
        
    @classmethod
    def from_crawler(cls, crawler):
        proxy_api = crawler.settings.get('PROXY_API')
        if not proxy_api:
            raise NotConfigured
        return cls(proxy_api)
        
    def _get_proxies(self):
         try:
            # 从代理服务商 API 获取 IP 列表
            response = requests.get(self.proxy_api)
            return response.json()['proxies']
         except Exception as e:
            print(f"获取代理 IP 失败: {e}")
            return []
        
    def process_request(self, request, spider):
        # 随机选择代理
        proxy = random.choice(self.proxies)
        request.meta['proxy'] = f'http://{proxy}'

class SeleniumMiddleware:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=chrome_options)
        
    def process_request(self, request, spider):
        try:
            self.driver.get(request.url)
            # 等待商品列表加载完成
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.product-list'))
            )
            body = self.driver.page_source
            return HtmlResponse(self.driver.current_url, body=body, 
                               encoding='utf-8', request=request)
        except Exception as e:
            print(f"使用 Selenium 加载页面失败: {e}")
            return None

    def __del__(self):
        if self.driver:
            self.driver.quit()