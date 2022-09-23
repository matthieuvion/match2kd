import logging

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO)
from typing import AsyncContextManager

import os
from dotenv import load_dotenv

import itertools
import random
import pickle
import json
import time

import asyncio
import aiofiles

import httpx
from async_lru import alru_cache
import backoff

from wzlight import Api

"""
Inside:
-------

Collect detailed match stats for a list of Warzone (resurgence) match ids , 
using 'wzlight' Call of duty Warzone API async wrapper
"""


class EnhancedApi(Api):
    """Inherits wzlight Api Cls, add or enhance default methods"""

    def __init__(self, sso):
        super().__init__(sso)

    @alru_cache(maxsize=128)
    @backoff.on_exception(backoff.expo, httpx.HTTPError, max_time=25, max_tries=5)
    async def GetMatchSafe(
        self,
        httpxClient,
        platform,
        matchId: int,
        sema: AsyncContextManager,
    ):
        """Tweak Api.GetMatch adding caching, backoff, async.Semaphore limit object"""

        async with sema:

            r = await self.GetMatch(httpxClient, platform, matchId)

            logging.info(f"getting match details for match: {matchId}")
            await asyncio.sleep(1)

            if sema.locked():
                print("Concurrency limit reached, waiting ...")
                await asyncio.sleep(0.5)
            return r

    async def GetMatchList(self, httpxClient, platform, matchIds: list[int]):
        """New Api method : run GetMatchSafe (--> Api.GetMatch) async/"concurrently",
        with a limit,  given a list of MatchIds.
        """

        sema = asyncio.Semaphore(2)
        tasks = []
        for matchId in matchIds:
            tasks.append(self.GetMatchSafe(httpxClient, platform, matchId, sema))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return list(itertools.chain(*results))


async def main(matchIds):

    load_dotenv()
    sso = os.environ["SSO"]
    enh_api = EnhancedApi(sso)
    platform = "battle"

    async with httpx.AsyncClient() as httpxClient:
        batch_matches = await enh_api.GetMatchList(httpxClient, platform, matchIds)

    with open(
        f"data/crawled/wzlight/matches_batch2_filtered_{str(start)}_{str(end)}.json",
        "w",
    ) as f:
        json.dump(batch_matches, f)


if __name__ == "__main__":

    filename = "matchIds_batch2_filtered.pickle"
    start = 300
    end = -1
    with open(f"./data/{filename}", "rb") as f:
        matchIds = pickle.load(f)
    matchIds = [int(id) for id in matchIds][start:end]

    asyncio.run(main(matchIds))
