from itemadapter import ItemAdapter
import pymongo
from datetime import datetime
from TaoBao.items import ProductItem
from TaoBao.items import ProductReviewItem

class MongoDBPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'ecommerce')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        # 创建索引
        self.db['products'].create_index([('product_id', pymongo.ASCENDING)], unique=True)
        self.db['reviews'].create_index([('review_id', pymongo.ASCENDING)], unique=True)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, ProductItem):
            # 更新或插入商品数据
            self.db['products'].update_one(
                {'product_id': item['product_id']},
                {'$set': dict(item), '$setOnInsert': {'first_crawl_time': datetime.now()}},
                upsert=True
            )
        elif isinstance(item, ProductReviewItem):
            # 插入评论数据（存在则跳过）
            try:
                self.db['reviews'].insert_one(dict(item))
            except pymongo.errors.DuplicateKeyError:
                pass  # 已存在的评论跳过
        return item