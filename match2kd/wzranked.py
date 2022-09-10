import requests
from requests.exceptions import HTTPError
import json
from enum import Enum
import time
from random import randint
from typing import Dict, Literal


"""
Inside:
--------

Stuff to crawl/parse wzranked.com (unofficial, graphQL-based) API
We're kindly using it because we find the way it calculates the avg kd for a lobby to be the most relevant & accurate. 
FYI, avg K/D ratio for a lobby = mean(n players seasonal kills/deaths ratio).

We're not totally mean : for detailed stats about each match we could have also relied on wzranked,
but instead we will use our own credentials (SSO token) and COD API wrapper ('wzlight') to do so.
"""


class Wzranked:

    url = "https://wzranked.hasura.app/v1/graphql"
    personal_uuid = (
        "df2b8a05-b479-456c-ab68-4adf00e23189"  # personal profile uuid on wzranked
    )

    headers = {
        "authority": "wzranked.hasura.app",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://www.wzranked.com",
        "referer": "https://www.wzranked.com/",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="104"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.101 Safari/537.36",
    }

    class Queries(Enum):
        MATCH = "query MyQuery($f_matchidstring: String!) {fmatch(args: {f_matchidstring: $f_matchidstring}) {matchidstring utcendtime mode ruleset squad iscomplete playercount totalplayerskd totalplayerswr lobbykd lobbywr teamsleft5min teamsleft10min teamsleft15min teamsleft20min players}}"
        PMATCHES = "query MyQuery($f_uuid: uuid!, $f_session: Int!) {fsessions(args: {f_uuid: $f_uuid, f_session: $f_session}) {sessionid utcendtime players matches} tprofiles(where: {uuid: {_eq: $f_uuid}}) {username updated_at responseminutcendseconds }}"
        PSTATS = "query MyQuery($f_uuid: uuid!) {fstats(args: {f_uuid: $f_uuid}) {mode stats chart} tprofiles(where: {uuid: {_eq: $f_uuid}}) {username updated_at responseminutcendseconds}}"

    def __init__(self):
        self.headers = Wzranked.headers
        self.url = Wzranked.url
        self.personal_uuid = Wzranked.personal_uuid
        self.uuids = []
        self.matchIds = []

    def _buildPayload(self, query, variables):
        payload = {"query": query, "variables": variables}
        return json.dumps(payload)

    def getMatch(self, matchId: str):
        query = Wzranked.Queries.MATCH.value
        variables = {"f_matchidstring": matchId}
        payload = self._buildPayload(query, variables)
        try:
            r = requests.post(
                url=self.url, headers=self.headers, data=payload, timeout=4
            )
            r.raise_for_status()
            # note that's only for http error, i.e. when wrong query, wzranked still return an object with "errors" in it
        except HTTPError as err:
            print(f"error, request:{err.request}, error:{err.response}")
        return r.json()

    def getPlayerMatches(self, uuid: str, session: int):
        """Get player's sessions given a specified wzranked uuid"""
        query = Wzranked.Queries.PMATCHES.value
        variables = {"f_uuid": uuid, "f_session": session}
        payload = self._buildPayload(query, variables)
        try:
            r = requests.post(
                url=self.url, headers=self.headers, data=payload, timeout=4
            )
            r.raise_for_status()
        except HTTPError as err:
            print(f"error, request:{err.request}, error:{err.response}")
        return r.json()

    def getPlayerStats(self, uuid: str):
        """Get player's stats given a specified wzranked uuid"""
        query = Wzranked.Queries.PSTATS.value
        variables = {"f_uuid": uuid}
        payload = self._buildPayload(query, variables)
        try:
            r = requests.post(
                url=self.url, headers=self.headers, data=payload, timeout=4
            )
            r.raise_for_status()
        except HTTPError as err:
            print(f"error, request:{err.request}, error:{err.response}")
        return r.json()

    def uuidsFromMatchIds(self, matchIds: list[str]):
        """Get a list of wzranked uuids, after crawling a list of matchIds"""

        def parse_uuids(match):
            list_players = match["data"]["fmatch"][0]["players"]
            match_uuids = [player["uuid"] for player in list_players if player["uuid"]]
            if self.personal_uuid in match_uuids:
                match_uuids.remove(self.personal_uuid)
            return match_uuids

        # 1st crawl level will usually collect only a few names n matches * 1 or 2 max
        for idx, matchId in enumerate(matchIds):
            print(f"getting uuids from match {matchId} ({idx+1}/{len(matchIds)})")
            time.sleep(randint(1, 3))

            try:
                match = self.getMatch(matchId=matchId)
                match_uuids = parse_uuids(match)
                self.uuids.extend(match_uuids)
                self.uuids = list(set(self.uuids))
            except:
                continue

    def matchIdsFromUuids(
        self,
        uuids: list[str],
        mode: Literal["resurgence", "battle"],
        squad: Literal["solos", "duos", "trios", "quads", "any"],
        n_sessions: int,
    ):
        """Get a list of matchIds, after crawling a list of uuids"""

        def parse_matchIds(profile, mode, squad):
            mode_convert = {"resurgence": "Resurgence", "battle": "BR"}

            list_matches = profile["data"]["fsessions"][0]["matches"]
            matchIds_all = [
                {
                    "matchidstring": match["matchidstring"],
                    "mode": match["mode"],
                    "squad": match["squad"],
                }
                for match in list_matches
            ]
            matchIds_mode = [
                {
                    "matchidstring": match["matchidstring"],
                    "squad": match["squad"],
                }
                for match in matchIds_all
                if match["mode"] == mode_convert[mode]
            ]
            if squad == "any":
                return [match["matchidstring"] for match in matchIds_mode]
            else:
                return [
                    match["matchidstring"]
                    for match in matchIds_mode
                    if match["squad"] == str.capitalize(squad)
                ]

        for idx, uuid in enumerate(uuids):
            print(
                f"getting matchIds from profile (/sessions) {uuid} ({idx+1}/{len(uuids)})"
            )
            time.sleep(randint(1, 3))
            try:
                for idx_session in range(n_sessions):
                    print(f"session: {idx_session}")
                    time.sleep(randint(1, 2))
                    try:
                        profile = self.getPlayerMatches(uuid, idx_session)
                        matchIds = parse_matchIds(profile, mode, squad)
                        self.matchIds.extend(matchIds)
                        self.matchIds = list(set(self.matchIds))
                    except:
                        continue
            except:
                continue

    def parseMatchInfo(self, result: Dict):
        """Parse minimal info : game mode and avg kd from a match result"""

        schema = {
            "matchidstring": str,
            "utcendtime": str,
            "mode": str,
            "ruleset": str,
            "squad": str,
            "playercount": int,
            "totalplayerskd": int,
            "lobbykd": float,
        }
        full_match = result["data"]["fmatch"][0]
        match_info = {}
        for key in schema.keys():
            match_info[key] = full_match.get(key, None)
        return match_info
