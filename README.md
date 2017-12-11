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
* Randomised User-Agent middleware


## Requirements

* Python 3.6 (3.5+ should work, but untested)


## How to

    # Get available spiders
    $ scrapy list
    amazonau-musiccds
    atlantismusic-musiccds
    sanity-musiccds

    # Run individual spider
    $ scrapy crawl amazonau-musiccds -o results/amazonau-musiccds.jl

    # TODO: Find out the preferred way to do this - the -o argument appears to be global, so this script doesn't actually save results
    # Run all spiders in parallel
    $ python -m scrapyexperiments.scripts crawl results

    # Analyse scraped data
    $ python -m scrapyexperiments.scripts analyse results
    == Biggest deals ==
    Abbath               - Abbath                         - 51% ($23.86) saving at atlantismusic ($22.07) compared to amazonau ($45.93)
    Ed Sheeran           - 5                              - 46% ($23.18) saving at amazonau ($26.59) compared to atlantismusic ($49.77)
    Grateful Dead        - Cornell 5/8/77                 - 47% ($22.87) saving at amazonau ($25.13) compared to atlantismusic ($48.00)
    ...


## TODO

* Make scrapers more parallel
    * Sanity.com.au gives links to the following 4 pages on every 5th
      page, plus a link to the next set of 5 - schedule all 5 at once
    * Proper feed exporter setup. This is needed for the crawl script
      that runs all spiders at once. I have a rough idea how to do this,
      but I'd like to make sure I do it the standard way, so it's not
      implemented yet.

