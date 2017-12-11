# coding=utf-8
import re
from urllib.parse import urlparse, parse_qs, urlencode

import scrapy

from scrapyexperiment.items import MusicCDItem


class AtlantisMusicMusicCDsSpider(scrapy.Spider):
    name = "atlantismusic-musiccds"
    allowed_domains = ["atlantismusic.com.au"]

    def start_requests(self):
        # path=1_2  - CDs / New
        # limit=200 - Results per page (appears to be unlimited, site uses 100)
        url = (
            "https://atlantismusic.com.au/index.php"
            "?route=product/category"
            "&path=1_2"
            "&limit=200"
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
        pages_info = response.css(".row").xpath(
            "*[starts-with(text(),'Showing')]/text()"
        ).extract()[0]
        match = re.match(
            r"Showing \d+ to \d+ of \d+ \((?P<page_count>\d+) Pages\)",
            pages_info,
        )
        last_page = match.groupdict()["page_count"]
        last_page = int(last_page)

        # Get the URL for the next page to use as a basis for all pages
        page_links = response.css(".pagination li")
        next_page_url = page_links.xpath("*[text()='>']/@href").extract()[0]
        url = urlparse(next_page_url)
        query = parse_qs(url.query, keep_blank_values=True)

        # Request each page
        for page in range(2, last_page + 1):
            query["page"] = page
            url = url._replace(query=urlencode(query, doseq=True))
            yield response.follow(url.geturl(), callback=self.parse)

        # Call the regular parse method to actually scrape this page's data
        yield from self.parse(response)

    def parse(self, response):
        for result in response.css(".product-layout"):
            cd = MusicCDItem()
            try:
                items = result.css(".caption h4 a::text").extract()

                cd["title"] = items[0]

                artist = items[1]
                # Items have their format at the end in parentheses, so we need
                # to strip that. We're only scraping the "CD / New" category,
                # so the only possible format is "CD", but make sure it's there
                # before lopping the end off blindly.
                if artist.endswith(" (CD)"):
                    artist = artist[:-5]
                cd["artist"] = artist

                cd["price"] = result.css(".price::text").extract()[0].strip()
            except IndexError:
                self.logger.error("Error parsing item: %s", result)
                continue
            yield cd
