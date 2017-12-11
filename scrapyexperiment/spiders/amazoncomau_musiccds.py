# coding=utf-8
from urllib.parse import urlparse, parse_qs, urlencode

import scrapy

from scrapyexperiment.items import MusicCDItem


class AmazonAUMusicCDsSpider(scrapy.Spider):
    name = "amazonau-musiccds"
    allowed_domains = ["amazon.com.au"]

    def start_requests(self):
        # rh                                      - search options
        #   n:4852330051                          - CDs & Vinyl
        #   p_n_binding_browse-bin:5260922051     - CD filter
        #   p_n_availability:4910512051           - Availability: In stock
        #   p_n_free_shipping_eligible:5363790051 - Free shipping
        # lo=popular                              - Grid layout (60 per page)
        #                                           but it doesn't list artist
        url = (
            "https://www.amazon.com.au/gp/search/"
            "?rh=n%3A4852330051"
            "%2Cp_n_binding_browse-bin%3A5260922051"
            "%2Cp_n_availability%3A4910512051"
            "%2Cp_n_free_shipping_eligible%3A5363790051"
        )
        yield scrapy.Request(
            url,
            callback=self._parse_initial,
            dont_filter=True,
        )

    def _parse_initial(self, response):
        # Schedule the requests for all the pages up front to allow scrapy to
        # parallelise them. Otherwise, each page would depend on the previous
        # one's "Next page" link, which means only one request can be happening
        # at once. This would probably be acceptable if we were also making
        # requests for each item, but we're just pulling the data from the
        # listing.

        # Find the last page
        last_page = response.css("#pagn .pagnDisabled::text").extract()[0]
        last_page = int(last_page)

        # Get the URL for the next page to use as a basis for all pages
        next_page_url = response.css("#pagnNextLink::attr(href)").extract()[0]
        url = urlparse(next_page_url)
        query = parse_qs(url.query, keep_blank_values=True)

        # Request each page
        for page in range(2, last_page):
            query["page"] = page
            url = url._replace(query=urlencode(query, doseq=True))
            yield response.follow(url.geturl(), callback=self.parse)

        # Call the regular parse method to actually scrape this page's data
        yield from self.parse(response)

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
