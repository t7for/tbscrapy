# items.py
import scrapy

class ProductItem(scrapy.Item):
    platform = scrapy.Field()
    product_id = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field() 
    original_price = scrapy.Field()   #原价
    sales_volume = scrapy.Field()   #销量
    brand = scrapy.Field()        #品牌
    category = scrapy.Field()  #分类
    rating = scrapy.Field()
    review_count = scrapy.Field() #评论数
    crawl_time = scrapy.Field()

class ProductReviewItem(scrapy.Item):
    product_id = scrapy.Field()
    review_id = scrapy.Field()
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    content = scrapy.Field()
    rating = scrapy.Field()
    review_time = scrapy.Field()
    helpful_count = scrapy.Field()
    crawl_time = scrapy.Field()