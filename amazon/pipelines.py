# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pprint import pprint

import pymysql


class AmazonPipeline(object):

    def open_spider(self, spider):
        self.db = pymysql.connect(host='127.0.0.1', user='xxx', password='xxx', database='amazon')
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        pprint(item)
        url = item['url']
        asin = item['asin']
        title = item['title']
        brand = item['brand']
        price = item['price']
        picture = item['picture']
        stars = item['stars']
        reviews = item['reviews']
        rank = item['rank']
        ranks = item['ranks']
        time = item['time']
        keyword = item['keyword']
        sql ='''insert into earbuds(url, asin, title, brand, price, picture, stars, reviews, rank, ranks, keyword, time) value("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s", "%s")'''%(url, asin, title, brand, price, picture, stars, reviews, rank, ranks, keyword, time)
        try:
            self.cursor.execute(sql)
            self.db.commit()
            print(f"{url}上传成功")
        except Exception as e:
            print(e)
            self.db.rollback()
            print(f"{url}上传失败")

    def close_spider(self,spider):
        self.cursor.close()
        self.db.close()
