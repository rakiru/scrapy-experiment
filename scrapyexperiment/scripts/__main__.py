# coding=utf-8
import argparse

from scrapyexperiment.scripts.analyse import analyse_command
from scrapyexperiment.scripts.crawl import crawl_command

__author__ = "rakiru"


parser = argparse.ArgumentParser(
    description="Australian music CD website scraper",
)

subparsers = parser.add_subparsers()

crawl_parser = subparsers.add_parser(
    "crawl",
    help="Crawl all available websites",
)
crawl_parser.add_argument("output_dir")
crawl_parser.set_defaults(func=crawl_command)

analyse_parser = subparsers.add_parser(
    "analyse",
    help="Compare the prices in the scraped data",
    aliases=["analyze"],
)
analyse_parser.add_argument(
    "data_dir",
    help="A directory containing scraped data files",
)
analyse_parser.set_defaults(func=analyse_command)


args = parser.parse_args()
args.func(args)
