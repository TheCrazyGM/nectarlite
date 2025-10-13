#!/usr/bin/env python

import logging

from nectarlite.api import Api
from nectarlite.stream import Stream

# Configure logging to see the events as they come in
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


def main():
    """Streams new votes from the Hive blockchain and prints them."""
    print("Starting live vote listener... (Press Ctrl+C to stop)")

    try:
        # Initialize with a node that has a good connection
        api = Api(["https://api.hive.blog"])

        # We will listen in 'head' mode to get votes as soon as they are broadcast
        listener = Stream(api=api, blockchain_mode="head")

        # Use the 'on' method to filter for 'vote' operations
        for vote in listener.on("vote"):
            voter = vote.voter
            author = vote.author
            permlink = vote.permlink
            weight = vote.weight

            logging.info(
                f"New Vote! Voter: {voter}, Post: @{author}/{permlink}, Weight: {weight}"
            )

    except KeyboardInterrupt:
        print("\nStopping listener.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
