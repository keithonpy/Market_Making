# market making algorithm
A trading algorithm works on algotrading competition on a proprietary trading platform developed by Optiver. The main file to execute is `algorithm.py`. The market making strategies adopted are cointegration and delta-hedging.
## Cointegration
`cointegration_analysis.py` - analyse the relationship between stocks
## delta-hedging
- `find_sigma.py` - calculate the volatility of the options
- `black_scholes.py`
  - `call_value` - determine the fair call option prices
  - `put_value` - determine the fair put option prices
  - `call_delta` - determine delta of call option (change of option price vs change of stock price)
  -  `put_delta` - determine delta of put option (change of option price vs change of stock price)
  -  `call_vega` -  determine vega of call option (change of option price vs change of volatility)
  -  `put_vega` - determine vega of put option (change of option price vs change of volatility)
