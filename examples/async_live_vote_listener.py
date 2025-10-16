#!/usr/bin/env python

import asyncio
import logging

from nectarlite.api import AsyncApi
from nectarlite.stream import AsyncStream

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)


async def main():
    api = AsyncApi(["https://api.hive.blog"])
    listener = AsyncStream(api=api, blockchain_mode="head")

    logging.info("Listening for new votes asynchronously... (Ctrl+C to stop)")
    async for vote in listener.on("vote"):
        logging.info(
            "New vote! voter=%s author=%s permlink=%s",
            vote.voter,
            vote.author,
            vote.permlink,
        )


if __name__ == "__main__":
    asyncio.run(main())
