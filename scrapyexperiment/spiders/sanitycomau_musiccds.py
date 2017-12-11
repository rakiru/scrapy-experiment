# coding=utf-8
import re
import scrapy

from scrapyexperiment.items import MusicCDItem


class SanityMusicCDsSpider(scrapy.Spider):
    name = "sanity-musiccds"
    allowed_domains = ["sanity.com.au"]

    def start_requests(self):
        return [
            # Future requests get their state from the form in the response,
            # but the initial response obviously needs some data.
            scrapy.FormRequest(
                "http://www.sanity.com.au/genre/music",
                formdata={
                    # CD
                    "ctl00$BodyCph$ProductFilterCtrl$FormatRpt$ctl07$ItemCb": "on",
                    # CD Singles
                    "ctl00$BodyCph$ProductFilterCtrl$FormatRpt$ctl08$ItemCb": "on",
                },
                dont_filter=True,
            ),
        ]

    def parse(self, response):
        print(response)
        for result in response.css(".product-list-thumb"):
            cd = MusicCDItem()

            item = result.css(".thumb-text div ::text").extract()
            try:
                cd["title"] = item[0]
                artist = item[1]
                # Sometimes the artist is missing, and the next item is the
                # release date, so check this doesn't look date-y.
                # Just in case the release date can also be missing, check it
                # doesn't look like a format either.
                if re.match(r"(?:\d{1,2} \w{3} \d{4})|(?:CD|Vinyl)", artist):
                    self.logger.warning("Item missing artist; skipping")
                    continue
                cd["artist"] = artist
                # 2 = release date
                # 3 = type (CD)
                # 4 = availability, but doesn't exist if not in stock
                price = item[-1]
                if price != result.css(".thumb-price::text").extract()[0]:
                    self.logger.error("Price mixup; has the HTML changed?")
                    continue
                cd["price"] = price
            except IndexError:
                self.logger.error("Error parsing item: %s", result)
                continue
            yield cd

        # The pagination on this site shows a button group of 5 pages at once.
        # If you're on the last page of the button group, you need to click an
        # arrow to jump to the next group of 5.
        pager = response.css(".pager")
        next_link = pager.css(".pagerLinks .selected + .pagerLinkItem")
        if not next_link:
            # We've reached the end of the page - fetch the arrow instead
            next_link = pager.css(".pagerForwardLinks")

        # Additionally, as this is an ASP.NET site, the whole page is a form
        # with a bunch of state in it. The pager links normally run some JS
        # that sets a couple of form values then submits the form, so we need
        # to parse the href, which will look something along the lines of:
        # javascript:__doPostBack('ctl00$BodyCph$JQPagerControl$ForwardLb','')
        href = next_link.css("::attr(href)")[0].extract()
        args = []
        end = -1
        for x in range(2):
            start = href.find("'", end + 1)
            end = href.find("'", start + 1)
            args.append(href[start + 1:end])

        # Thankfully, scrapy has a utility method for filling POST data from a
        # form, but we still need to set a couple of the fields that get set
        # by __doPostBack, the function called by the links above.
        yield scrapy.FormRequest.from_response(
            response,
            formdata={
                "__EVENTTARGET": args[0],
                "__EVENTARGUMENT": args[1],
                # XXX: Hardcoded - this gets set by JS elsewhere
                "ctl00$GlobalScriptManager": "ctl00$BodyCph$UpdatePanel1|" + args[0],
            },
            dont_click=True,
        )
