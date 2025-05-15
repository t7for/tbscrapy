# tbscrapy
Taobao Crawler Project Based on Scrapy Framework for Personal Learning
代码说明
tb.py：
parse 方法：解析商品列表页，提取商品的基本信息，如平台、商品 ID、标题、价格和销量等。
parse_detail_url 方法：对商品详情页的 URL 进行预处理，确保 URL 的正确性。
send_to_tbdetail 方法：将商品 ID 和详情页 URL 传递给 tbdetail 爬虫。
tbdetail.py：
start_requests 方法：接收来自 tb 爬虫的请求，解析出商品 ID 和详情页 URL，并发起请求。
parse 方法：解析商品详情页，提取商品的详细信息，如品牌、分类、评分和评论数等。同时，解析评论数据，生成 ProductReviewItem 对象并返回。
get_current_time 方法：获取当前时间，用于记录评论的爬取时间。
