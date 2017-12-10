# coding=utf-8
import scrapy

from scrapyexperiment.items import MusicCDItem


class AmazonAUMusicCDsSpider(scrapy.Spider):
    name = "amazonau-musiccds"
    allowed_domains = ["amazon.com.au"]
    start_urls = [
        # rh                                      - search options
        #   n:4852330051                          - CDs & Vinyl
        #   p_n_binding_browse-bin:5260922051     - CD filter
        #   p_n_availability:4910512051           - Availability: In stock
        #   p_n_free_shipping_eligible:5363790051 - Free shipping
        # lo=popular                              - Grid layout (60 per page)
        #                                           but it doesn't list artist
        (
            "https://www.amazon.com.au/gp/search/"
            "?rh=n%3A4852330051"
            "%2Cp_n_binding_browse-bin%3A5260922051"
            "%2Cp_n_availability%3A4910512051"
            "%2Cp_n_free_shipping_eligible%3A5363790051"
        ),
    ]

    def parse(self, response):
        for result in response.css(".s-result-list > li"):
            cd = MusicCDItem()
            try:
                cd["title"] = result.css(
                    "h2.s-access-title::attr(data-attribute)"
                ).extract()[0]

                # There's no specific identifier for the artist, and it moves
                # depending on other optional fields, but there's always an
                # identical span before it with the text "by ", so use that.
                nodes = result.css(
                    ".a-size-small.a-color-secondary::text"
                ).extract()
                for x, item in enumerate(nodes):
                    if item == "by ":
                        cd["artist"] = nodes[x + 1]
                        break
                else:
                    self.logger.error("No artist found; has the HTML changed?")
                    continue

                cd["price"] = result.css(".s-price::text").extract()[0]
            except IndexError:
                self.logger.error("Error parsing item: %s", result)
                continue
            yield cd

        # Go to the next page, if it exists
        for link in response.css("#pagnNextLink"):
            yield response.follow(link)
