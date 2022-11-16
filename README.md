# match2kd
[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/tterb/atomic-design-ui/blob/master/LICENSEs)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

`match2kd` is a end-to-end data science project (custom dataset -> model -> (light) deployment) applied on top of Call of Duty (COD) API/ecosystem.<br>Our initial goal was to overcome COD API rate limits by estimating a match difficulty ("lobby k/d") from its features (players' performance / various metrics this match : one call to the API) instead of requesting their whole history / performance (a lot of calls).<br>

The core work (model notebook) is also accessible/readable in a better format through github.io, [there](https://matthieuvion-wzkd-home-xx.com).<br>

The model is one of the 3 component of a more global work centered about COD API / metrics intelligence:<br>
- [wzkd](https://github.com/matthieuvion/wzkd) : a Streamlit-based dashboard that collect, aggr. and visualize player's stats from Call of Duty Warzone (1), where I also deploy the model.<br>
- [wzlight](https://github.com/matthieuvion/wzkd) (also on pypi) : a light, asynchronous python wrapper for 'Callof' API that was (also) used to build our dataset / power the dashboard.


## Main objective

-  

## Workflow - things you can find in this repository

-

## (Some) Challenges faced

-


