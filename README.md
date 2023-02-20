## match2kd
[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/tterb/atomic-design-ui/blob/master/LICENSEs)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

`match2kd` aims at overcoming COD API rate limits by estimating a match difficulty ("lobby k/d") from its features (players' metrics in a match : one call to the API) instead of requesting their whole history (hundreds of calls) <br>
Edit:<br>
February 2023 : this work was made for Warzone 1 / Resurgence mode. Now Warzone 2 is out, things may vary much.


The model is one of the 3 component of a more global personal side project centered about COD API / metrics intelligence:<br>
- [wzkd](https://github.com/matthieuvion/wzkd) : a Streamlit-based dashboard that collect, aggr. and visualize player's stats from Call of Duty Warzone (1), where we also deploy the model.<br>
- [wzlight](https://github.com/matthieuvion/wzlight) (also on pypi) : a light, asynchronous python wrapper for 'Callof' API that was (also) used to build our dataset / power the dashboard.

### Under-the-hood pain points one tries to resolve
---
- Calculation of an accurate "lobby kd" (players' average kills/deaths ratio), the main metric used by players to estimate a match difficulty, isn't possible without some form of special access / partnership with Activision  like cod tracker / wzranked stats tracker websites and/or a continuous matches / players profile data retrieval, caching & storage.
- One of the rate limit of the COD API (not documented) is said to be 200 calls / 30 mn or so.
- Our target, "Lobby KD" or more accurately "avg players' kills/deaths ratio" is calculated as :<br> `Mean (n players' kills / deaths ratio, their x last matches)`
- This metric **is not directly provided** by the API and is only retrievable by querying and aggregating `n` (player) times `x` (player recent matches) the API.
- E.g. for a single match of 40 players with, let's say an history of 30 matches per player, we would need *a minima* 40 (players) * 30 (matches) = **1200 calls** to calculate that metric.
- As a player we can often "feel" what is the difficulty of a match and the API provides post-match metrics (one call with a given match ID), with players performance metrics **this** match, that could be used to model game difficulty without querying all players profiles and performance in their last recent matches.

### Workflow - things that you might re-use in this repo
---

#### 1. Data collection tools
* Two modules were used to retrieve data:
    * `wzranked.py` : custom Cls / wrapper to crawl/parse a --quite accurate, "lobby kd" from wzranked.com (unofficial, graphQL-based) API.
    * `collect_matches_details.py` : an async wrapper to collect detailed match stats, based on my side project `wzlight` <br>

#### 2. Dataset
- Final custom dataset (`match2kd/dataset_warzone_kd_bigger.parquet.gzip`) with **55k rows** (**1170 unique matches** with +- 40 players), **152 features** (kills, deaths, pct time moving...) and the associated target (game difficulty / "lobby kd"). The data was collected around Sept 2022, from random COD Warzone players/matches (Rebirth mode only, solos to quads)

| MatchID | Player | Map | Kills | *feat. 3* | *feat. 4* | *... feat. 152* | Target : "lobby k/d"|
| --- | --- | --- | --- | :---: | :---: | :---: | :---: |
| ***129999***|*1*|Rebirth|1|--|--|--|**1.12**|
| *129999*|*...*|Rebirth|5|--|--|--|1.12|
| *129999*|*40*|Rebirth|2|--|--|--|1.12|
| ***125555***|*1*|FK.|0|--|--|--|**0.97**|
| *125555*|*2*|FK.|8|--|--|--|0.97|
|*x 1 k unique Ids*|...|...|...|...|...|...|...|

#### 2. Model
- Final XGB model available (`match2kd/xgb_model_lobby_kd_2.json`), currently deployed in [Streamlit app](https://github.com/matthieuvion/wzkd)
- Notebook with the workflow to train our model (`match2kd/model_v3.ipynb`)
- Include my findings to improve model accuracy : features selection & engineering, as well as final aggregations made to retain enough information.

### Challenges
---
- Custom dataset : the usual tedious work (scrapper, API wrapper) to gather our precious data.
- Skewed continuous target + 4 "types" of matches (team of 1,2,3 or 4 players) even if XGB is allegedly ok with that.
- multi-level data : we want to predict "lobby kd" for a match. Picture every match as a table of +- 40 rows (players) with 150+ features (players metrics) and a single unique target (lobby kd). To train our model we will need to compress our data (one row with 150+ features per match -> our target). Will the model retain enough information ?
- Documentation and examples quite scarce when dealing with multi-level data. Also specific models exist but won't extend on the matter :-p.

### Model Performance
---
- Our model has a mean rmse of +- 0.1 ; FYI "lobby k/d" usually navigates between 0.6 (rare) and 1.5 (rare).
- From post production personal tests (far from exhaustive), captures quite well lobby kd variations, just using compressed players-in-a-match features.
- Overall feeling (would need further proofing) is that lowest and highest lobby kds could be more accurate. E.g True [.7 - .9] k/d or > 1.1 k/d matches seem less finely predicted that those revolving around 1.
- We would have wanted our RMSE to be below the 0.1 mark more often as a lot of lobby kd revolve around the "1" threshold and we can "feel" the difference between a "0.9 kd" and a 1 or 1.1 kd match.

### Further leads, ideas
---
- A lot of work was puth in back-and-forth tweaking/testing on features; some missing features (not provided/updated by COD api) would have been useful... or more engineering... ;)
- Playing around "ranking" models or the "rank" features (players/team placement in a match).
- Augment and/or add more balance our dataset due to the the inherent skewed nature of Warzone matchmaking systel (a lot of matches revolve around the 1 kd mark).
- Cf. new techniques around synthetic data generation with DL for tabular data.
- Benchmark vs. other models. As of nov 2022 and after some searches, didn't bother to test DL methods (tabnet & Co) for our tabular exercise despite and interesting (small) revival in the domain.
- Prediction power gain is difficult due to the nature of the available data / degree of randomness of players' performances in a battle royale match ?
- 4, 8 or 2 models (solos, duos, trios, quads Resurgence) instead of 1 ? Though, squad size and map type (Fortune Keep vs Rebirth Island) did not seem that important in our model though.


