# stocktools
This is a collection of Python Tools that utilize yfinance.

The example script asks for a ticker symbol and a time period, then pulls the data from Yahoo Finance if available.
The script will then calculate the max gain, max loss, average changes and max/low closing prices.

Ticker symbols supported are any that are available from Yahoo Finance.
Some are tricky, for example for S&P Futures you need to use ES=F.
Valid time periods are: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.
