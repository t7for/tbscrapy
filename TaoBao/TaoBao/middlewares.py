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
import time

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
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # 如果chromedriver不在PATH中，需要指定路径
        # self.driver = webdriver.Chrome(executable_path='/path/to/chromedriver', options=chrome_options)
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # 设置隐式等待
        self.driver.implicitly_wait(10)

    def process_request(self, request, spider):
        try:
            self.driver.get(request.url)
            
            # 显式等待，根据页面结构调整选择器
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.product-info'))
            )
            
            # 如果需要滚动页面加载更多内容
            scroll_height = self.driver.execute_script("return document.body.scrollHeight")
            for i in range(1, 4):  # 分3次滚动到底部
                self.driver.execute_script(f"window.scrollTo(0, {scroll_height * i / 3});")
                time.sleep(0.5)
            
            # 处理可能的弹窗
            try:
                close_btn = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '.close-btn'))
                )
                close_btn.click()
            except:
                pass  # 没有弹窗则忽略
            
            # 返回渲染后的页面
            body = self.driver.page_source
            return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)
        
        except Exception as e:
            spider.logger.error(f"Selenium处理请求失败: {e}")
            return None

    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()