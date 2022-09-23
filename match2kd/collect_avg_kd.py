import logging

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO)

import random
import pickle
import json
import time

from match2kd import Wzranked


"""
Inside:
-------

Collect detailed match stats from a list of match ids, 
using match2kd/wzranked.py module that 'scrap' (grapql API) wzranked.com website
"""


def main(**kwargs):

    api = Wzranked()
    start = kwargs.get("start", 0)
    end = kwargs.get("end", 0)
    filename = kwargs.get("filename", "matchIds.pickle")

    with open(f"./data/{filename}", "rb") as f:
        matchIds = pickle.load(f)

    for i, matchId in enumerate(matchIds[start:end]):
        time.sleep(random.uniform(1, 2))
        logging.info(f"getting matchInfo from match {matchId} ({i+1})")
        try:
            result = api.getMatch(matchId=str(matchId))
            match_info = api.parseMatchInfo(result)
            with open(f"data/crawled/wzranked/{str(matchId)}.json", "w") as f:
                json.dump(match_info, f)

        except Exception:
            logging.exception(f"failed to parse match {matchId}")
        finally:
            continue


if __name__ == "__main__":
    main(filename="matchIds_batch2.pickle", start=300, end=-1)
