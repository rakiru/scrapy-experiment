# coding=utf-8
import scrapy

from scrapyexperiment.items import MusicCDItem


class AtlantisMusicMusicCDsSpider(scrapy.Spider):
    name = "atlantismusic-musiccds"
    allowed_domains = ["atlantismusic.com.au"]
    start_urls = [
        # path=1    - CDs
        # limit=200 - Results per page (appears to be unlimited, site uses 100)
        (
            "https://atlantismusic.com.au/index.php"
            "?route=product/category"
            "&path=1"
            "&limit=200"
        ),
    ]

    def parse(self, response):
        for result in response.css(".product-layout"):
            cd = MusicCDItem()
            try:
                items = result.css(".caption h4 a::text").extract()

                cd["title"] = items[0]

                artist = items[1]
                if artist.endswith(" (CD)"):
                    artist = artist[:-5]
                cd["artist"] = artist

                cd["price"] = result.css(".price::text").extract()[0].strip()
            except IndexError:
                self.logger.error("Error parsing item: %s", result)
                continue
            yield cd

        # Go to the next page, if it exists
        for link in response.css(".pagination li").xpath("*[text()='>']"):
            yield response.follow(link)
