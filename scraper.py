"""
This script downloads all the posts from the specified subreddit and year.
"""

import argparse
import csv
from datetime import datetime

from psaw import PushshiftAPI

#used it for parsing default year
x = datetime.now()

#argparse object creation
arg=argparse.ArgumentParser(description="Collets subreddits data")
arg.add_argument("-r", "--r",
                type = str,
                default = "Python",
                help = " takes in name of the subreddit")
arg.add_argument("-yr", "--yr",
                type = int,
                default = x.year,
                help = " takes in required Year")
args=arg.parse_args()

#class variables
SUBREDDIT = args.r
YEAR = args.yr


# These are used to restrict by the year we are interested in.
START_EPOCH = int(datetime(YEAR, 1, 1).timestamp())
END_EPOCH = int(datetime(YEAR, 12, 31).timestamp())

def main():

    # This list will hold all the posts data.
    data_list = [["isodate", "author", "title", "permalink"]]

    # We initialize the Pushshift API and query our data.
    api = PushshiftAPI()

    gen = api.search_submissions(
        subreddit=SUBREDDIT,
        after=START_EPOCH,
        before=END_EPOCH,
        filter=["author", "title", "permalink"]
    )

    # We iterate over each object in the generator.
    for item in gen:

        data = item[-1]

        # We extract the values and prevent crashes for non-existing ones.
        timestamp = data["created_utc"]
        author = data.get("author", "")
        title = data.get("title", "")
        permalink = data.get("permalink", "")

        if permalink != "":
            permalink = "https://www.reddit.com" + permalink

        # We convert he date from a timestamp to ISO format.
        isodate = f"{datetime.fromtimestamp(timestamp):%F %T}"

        data_list.append([isodate, author, title, permalink])

    # We save the data list to a CSV file.
    with open(f"{SUBREDDIT}-{YEAR}.csv", "w", newline="", encoding="utf-8") as csv_file:
        csv.writer(csv_file).writerows(data_list)


if __name__ == "__main__":

    main()
