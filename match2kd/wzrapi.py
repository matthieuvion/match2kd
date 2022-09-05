import requests
from requests.exceptions import HTTPError
import json
from enum import Enum


class Wzrapi:

    url = "https://wzranked.hasura.app/v1/graphql"

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
        self.headers = Wzrapi.headers
        self.url = Wzrapi.url

    def _buildPayload(self, query, variables):
        payload = {"query": query, "variables": variables}
        return json.dumps(payload)

    def getMatch(self, matchId: str):
        query = Wzrapi.Queries.MATCH.value
        variables = {"f_matchidstring": matchId}
        payload = self._buildPayload(query, variables)
        try:
            r = requests.post(
                url=self.url, headers=self.headers, data=payload, timeout=2
            )
            r.raise_for_status()
        except HTTPError as err:
            print(f"error, request:{err.request}, error:{err.response}")
        return r.json()

    def getPlayerMatches(self, uuid: str, session: int):
        query = Wzrapi.Queries.PMATCHES.value
        variables = {"f_uuid": uuid, "f_session": session}
        payload = self._buildPayload(query, variables)
        try:
            r = requests.post(
                url=self.url, headers=self.headers, data=payload, timeout=2
            )
            r.raise_for_status()
        except HTTPError as err:
            print(f"error, request:{err.request}, error:{err.response}")
        return r.json()

    def getPlayerStats(self, uuid: str):
        query = Wzrapi.Queries.PSTATS.value
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
