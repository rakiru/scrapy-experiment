# Scrapy Experiments

A simple scrapy project to get up to speed on the library. Contains
three scapers that grab the prices of music CDs from the newly launched
Amazon.com.au, Sanity.com.au, and AtlantisMusic.com.au. There is also a
script that consumes the scraper outputs and finds the items with the
biggest price differences.


## Features

* Amazon.com.au scraper
* Sanity.com.au scraper
* AtlantisMusic.com.au scraper


## Requirements

* Python 3.6 (3.3+ should work, but untested)


## How to

    # Get available spiders
    $ scrapy list
    amazonau-musiccds
    atlantismusic-musiccds
    sanity-musiccds

    # Run individual spider
    $ scrapy crawl amazonau-musiccds -o results/amazonau-musiccds.jl

    # Run all spiders in parallel
    $ python -m scrapyexperiments.scripts crawl results

    # Analyse scraped data
    $ python -m scrapyexperiments.scripts analyse results


## TODO

* Make scrapers more parallel
    * Sanity.com.au gives links to the following 4 pages on every 5th
      page, plus a link to the next set of 5 - schedule all 5 at once
    * Amazon only links to the next page, but the page is a simple GET
      parameter, and we're told how many pages there are total, so we
      could schedule a bunch at once, perhaps even all of them as soon
      as we get the first response?
    * AtlantisMusic is similar to Amazon.

