import requests
from requests.exceptions import HTTPError
import json
from enum import Enum
import time
from random import randint
from typing import Dict, Literal


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
                url=self.url, headers=self.headers, data=payload, timeout=2
            )
            r.raise_for_status()
            # note that's only for http error, i.e. when wrong query, wzranked still return an object with "errors" in it
        except HTTPError as err:
            print(f"error, request:{err.request}, error:{err.response}")
        return r.json()

    def getPlayerMatches(self, uuid: str, session: int):
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
        query = Wzranked.Queries.PSTATS.value
        variables = {"f_uuid": uuid}
        payload = self._buildPayload(query, variables)
        try:
            r = requests.post(
                url=self.url, headers=self.headers, data=payload, timeout=2
            )
            r.raise_for_status()
        except HTTPError as err:
            print(f"error, request:{err.request}, error:{err.response}")
        return r.json()

    def uuidsFromMatchIds(self, matchIds: list[str]):
        """Get a list of uuids, parsed from a list of matchIds"""

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
        match_type: Literal["resurgence", "battle"],
        n_sessions: int,
    ):
        """Get a list of uuids, parsed from a list of matchIds"""

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
            print(f"getting matchIds from profile {uuid} ({idx+1}/{len(uuids)})")
            time.sleep(randint(1, 3))
            try:
                for idx_session in range(n_sessions):
                    print(f"session: {idx_session}")
                    time.sleep(randint(1, 2))
                    try:
                        profile = self.getPlayerMatches(uuid, idx_session)
                        matchIds = parse_matchIds(profile, match_type)
                        self.matchIds.extend(matchIds)
                        self.matchIds = list(set(self.matchIds))
                    except:
                        continue
            except:
                continue

    def parseMatchInfo(self, result: Dict):
        """Extract Match general info (game type) and avg kd"""

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
