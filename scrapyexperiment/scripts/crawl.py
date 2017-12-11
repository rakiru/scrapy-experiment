# coding=utf-8
import os

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

__author__ = "rakiru"


def crawl_command(args):
    os.makedirs(args.output_dir, exist_ok=True)

    process = CrawlerProcess(get_project_settings())

    for spider in process.spider_loader.list():
        process.crawl(spider)

    process.start()
