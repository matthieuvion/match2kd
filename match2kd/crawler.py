# r_solo = 352397417798558181
# r_duo = 6255125893224897223
# r_trio = 10972479745496905935
# r_quad = 4643524269390348470
# fk_quads = 14159124111841726921

from typing import Literal
import requests
import time
from random import randint

from wzrapi import Wzrapi


class Crawler:
    personal_uuid = "df2b8a05-b479-456c-ab68-4adf00e23189"

    def __init__(self):
        self.uuids = []
        self.visited_uuids = []
        self.matchIds = []
        self.visited_matchIds = []
        self.api = Wzrapi()

    def uuidsFromMatchIds(self, matchIds: list[str]):
        def parse_uuids(match):
            list_players = match["data"]["fmatch"][0]["players"]
            match_uuids = [player["uuid"] for player in list_players if player["uuid"]]
            match_uuids.remove(Crawler.personal_uuid)
            return match_uuids

        # 1st crawl level will usually collect only a few names n matches * 1 or 2 max
        for idx, matchId in enumerate(matchIds):
            if matchId not in self.visited_matchIds:
                self.visited_matchIds.append(matchId)
                print(f"getting match {matchId} ({idx+1}/{len(matchIds)})")
                time.sleep(randint(1, 3))

                try:
                    match = self.api.getMatch(matchId=matchId)
                    match_uuids = parse_uuids(match)
                    self.uuids.extend(match_uuids)
                except:
                    continue

    def matchIdsFromUuids(
        self,
        uuids: list[str],
        match_type: Literal["resurgence", "battle"],
        n_sessions: int,
    ):
        def parse_matchIds(profile, match_type):
            mtype_convert = {"resurgence": "Resurgence", "battle": "BR"}
            list_matches = profile["data"]["fsessions"][0]["matches"]
            profile_matchIds = [
                match["matchidstring"]
                for match in list_matches
                if match["mode"] == mtype_convert[match_type]
            ]
            return profile_matchIds

        for idx, uuid in enumerate(uuids):
            if uuid not in self.visited_uuids:
                self.visited_uuids.append(uuid)
                print(f"getting profile {uuid} ({idx+1}/{len(uuids)})")
                time.sleep(randint(1, 3))
                try:
                    for idx_session in range(n_sessions):
                        print(f"session: {idx_session}")
                        time.sleep(randint(1, 2))
                        try:
                            profile = self.api.getPlayerMatches(uuid, idx_session)
                            matchIds = parse_matchIds(profile, match_type)
                            self.matchIds.extend(matchIds)
                        except:
                            continue
                except:
                    continue
