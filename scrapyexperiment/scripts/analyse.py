# coding=utf-8
import heapq
import json
import os

from decimal import Decimal

__author__ = "rakiru"


def analyse_command(args):
    files = {}
    # Load all files in folder into files dict
    with os.scandir(args.data_dir) as it:
        for entry in it:
            if not entry.is_file():
                continue

            items = []
            with open(os.path.join(args.data_dir, entry.name), "r") as fp:
                for line in fp:
                    if not line:
                        continue
                    item = json.loads(line)
                    # Just strip commas, since we know the locale
                    item["price"] = Decimal(
                        item["price"].strip("$").replace(",", "")
                    )
                    items.append(item)

            files[entry.name] = items

    # Strip common end from filenames to get prettier strings, since we don't
    # actually store the website name anywhere in the file.
    pos = -1
    while len(set(name[pos] for name in files)) == 1:
        pos -= 1
    pos += 1
    files = {k[:pos]: v for k, v in files.items()}

    # Create dict of albums
    albums = {}
    for website, items in files.items():
        for item in items:
            albums.setdefault(
                (item["title"], item["artist"]),
                {},
            )[website] = item["price"]

    # Filter out albums that only one website has
    for title in list(albums):
        if len(albums[title]) == 1:
            del albums[title]

    # Find the items with the biggest price difference between two websites...
    def max_price_difference(item):
        prices = sorted(item[1].values())
        return max(prices) - min(prices)

    biggest_diff = heapq.nlargest(10, albums.items(), key=max_price_difference)

    # ...and print them out
    print("== Biggest deals ==")
    for title, prices in biggest_diff:
        lowest = min(prices.items(), key=lambda x: x[1])
        highest = max(prices.items(), key=lambda x: x[1])
        diff = highest[1] - lowest[1]
        percentage = diff / highest[1] * 100
        print("%-20s - %-30s - %d%% ($%s) saving at %s ($%s) compared to %s ($%s)" % (title[1], title[0], percentage, diff, lowest[0], lowest[1], highest[0], highest[1]))
