import logging

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO)
import random
import pickle
import json
from random import sample
import time
from match2kd import Wzranked


def main(**kwargs):

    api = Wzranked()
    start = kwargs.get("start", 0)
    end = kwargs.get("end", 0)

    with open("./data/matchIds.pickle", "rb") as f:
        matchIds = pickle.load(f)

    for matchId in matchIds[start:end]:
        time.sleep(random.uniform(0.8, 2.5))
        logging.info(f"getting matchInfo from match {matchId}")
        try:
            result = api.getMatch(matchId=str(matchId))
            match_info = api.parseMatchInfo(result)
            with open(f"data/{str(matchId)}.json", "w") as f:
                json.dump(match_info, f)

        except Exception:
            logging.exception(f"failed to parse match {matchId}")
        finally:
            continue


if __name__ == "__main__":
    main(start=0, end=5)
