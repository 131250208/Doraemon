# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
import requests
import threading, time
import random


class WeiboBlogCommentsPipeline:

    def open_spider(self, spider):
        self.comment_file = open('comment_items.jl', 'w', encoding="utf-8")
        self.blog_file = open('blog_items.jl', 'w', encoding="utf-8")

    def close_spider(self, spider):
        self.comment_file.close()
        self.blog_file.close()

    def process_item(self, item, spider):
        item_dict = ItemAdapter(item).asdict()
        line = json.dumps(item_dict, ensure_ascii=False) + "\n"
        if item_dict["item_type"] == "comm":
            self.comment_file.write(line)
        elif item_dict["item_type"] == "blog":
            self.blog_file.write(line)
        return item
