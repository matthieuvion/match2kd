# match2kd
[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/tterb/atomic-design-ui/blob/master/LICENSEs)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

`match2kd` is a end-to-end data science project (custom dataset -> model -> (light) deployment) applied on top of Call of Duty (COD) API/ecosystem. The core work (model notebook) is also readable in a better format through github.io, [there](https://matthieuvion-wzkd-home-xx.com).<br>

--- 

The model is one of the 3 component of a more global work centered about COD API / metrics intelligence:<br>
- [wzkd](https://github.com/matthieuvion/wzkd) : a Streamlit-based dashboard that collect, aggr. and visualize player's stats from Call of Duty Warzone (1), where we also deploy the model.<br>
- [wzlight](https://github.com/matthieuvion/wzkd) (also on pypi) : a light, asynchronous python wrapper for 'Callof' API that was (also) used to build our dataset / power the dashboard.


## Main objective

Overcome COD API rate limits by estimating a match difficulty ("lobby k/d") from its features (players' metrics in a match : one call to the API) instead of requesting their whole history / performance (a lot of calls).

### Under-the-hood pain points
- Calculation of an accurate "lobby k/d" (the main metric used by players to estimate a match difficulty) isn't possible without some form of special access / partnership with Activision  like cod tracker / wzranked stats tracker websites and/or a continuous matches / players profile data retrieval & storage.
- One of the rate limit of the COD API (public access, not documented) is said to be 200 calls / 30 mn or so.
- Our target, "Lobby KD" or more accuratly "avg players' kills/deaths ratio" is calculated as :<br> `Mean (n players' kills / deaths ratio, their x last recent matches)`
- This metric is not provided by the API and is only retrievable by calling `n` (players) times `x` (matches) the API.
- E.g. for a single match of 40 players (Rebirth mode) with, let's say and history of 30 matches per players, we would need *a minima* 40 (players) * 30 (matches) = **1200 calls** made to the API to calculate that metric
- As a player we can often "feel" what's the difficulty of a match is and the API provide some in-game metrics (incomplete, though) that could be used to model game difficulty from player's metrics this match, without requesting their whole matches history.

## Workflow - things that you might re-use in this repo

### 1. Dataset
- Final custom dataset (`match2kd/dataset_warzone_kd_bigger.parquet.gzip`) with **55k rows** (**1170 unique matches** with +- 40 players), **152 features** (kills, deaths, pct time moving...) and the associated target (game difficulty / "lobby kd"). The data was collected around Sept 2022, from random COD Warzone players/matches (Rebirth mode only, solos to quads)
* Two modules were used to retrive data:
    * `wzranked.py` : custom Cls / wrapper to crawl/parse a --quite accurate, "lobby kd" from wzranked.com (unofficial, graphQL-based) API.
    * `collect_matches_details.py` : an async wrapper to collect detailed match stats, based on my side project `wzlight`

### 2. Model
- Final XGB model available (`match2kd/xgb_model_lobby_kd_2.json`), currently deployed in my streamlit app
- Notebook with the workflow to train our model (`match2kd/model_v3.ipynb`)


## Challenges
- Custom dataset : lot of work (scrapper, API wrapper) to gather our precious data.
- Skewed continuous target + 4 "types" of matches (team of 1,2,3 or 4 players) even if XGB is allegedly ok with that.
- multi-level data : we want to predict "lobby kd" for a match. Picture every match as a table of +- 40 rows (players) with 150+ features (players metrics) and a single unique target (lobby kd). To train our model we will need to compress our data (one row with 150+ features per match -> our target). Will the model retain enough information ?
- Documentation and examples quite scarce when dealing with multi-level data. Also specific models exist but won't extend on the matter :-p.

## Model Performance
- Our model has a mean rmse of +- [0.09 - 0.1] ; FYI "lobby k/d" usually navigates between 0.6 (rare) and 1.5 (rare)
- from post production personal tests, capture quite well lobby kd variations, but not perfectly. We would have wanted our RMSE to be below the 0.1 mark more often as a lot of lobby kd revolve around the "1" threshold.


