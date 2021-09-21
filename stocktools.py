# Kirk Sarrine
# kasarrine@gmail.com

import sys
import yfinance as yf
import pandas as pd
import numpy as np
import datetime


def get_stats(symbol, time_frame):
    # now = datetime.now().strftime("%Y-%m-%d")
    # Download instrument price history info
    try:
        history = yf.download(symbol, period=time_frame)
        # Store the daily % changes in a dict
        percent_changes = dict()
        # Export closing dates and prices to a Pandas Series
        closing_prices = history["Close"]
        # Export the date times from price history
        dates = closing_prices.keys()

        # Calculate the daily % changes and $ changes and insert into dictionary
        # with the key: value pairs of date: list(% change, price change)
        for i in range(1, len(dates) - 1):
            percent_change = (closing_prices[i] / closing_prices[i - 1] - 1) * 100
            price_change = closing_prices[i] - closing_prices[i - 1]
            date = dates[i]
            percent_changes[date] = [percent_change, price_change]

        # Initialization for values
        max_gain_percentage, max_gain_amount, max_price = -sys.maxsize - 1, -sys.maxsize - 1, -sys.maxsize - 1
        max_loss_percentage, max_loss_amount, low_price = sys.maxsize, sys.maxsize, sys.maxsize
        max_gain_date, max_loss_date, max_price_date, low_price_date = None, None, None, None

        # Calculate max gain and loss values by iterating through dictionary
        for date, changes in percent_changes.items():
            if changes[0] > max_gain_percentage:
                max_gain_date = date
                max_gain_percentage = changes[0]
                max_gain_amount = changes[1]
            if changes[0] < max_loss_percentage:
                max_loss_date = date
                max_loss_percentage = changes[0]
                max_loss_amount = changes[1]

        # Calculate max and min closing prices by iterating through price history
        for date, price in closing_prices.items():
            if price > max_price:
                max_price = price
                max_price_date = date
            if price < low_price:
                low_price = price
                low_price_date = date

        # Pull the max prices for gains and losses from the Pandas Series
        max_gain_closing_price = closing_prices[max_gain_date]
        max_loss_closing_price = closing_prices[max_loss_date]

        # Calculate the avg % change, % gain and % loss
        gains = [gain for gain, amount in percent_changes.values() if gain > 0]
        avg_gain = sum(gains) / len(gains)
        losses = [loss for loss, amount in percent_changes.values() if loss < 0]
        avg_loss = sum(losses) / len(losses)
        all_changes = [change for change, amount in percent_changes.values()]
        avg_change = sum(all_changes) / len(all_changes)

        # Output formatted data
        print(f'{"Symbol:":20}{symbol}')
        print("\nMax gain")
        print(f'{"Date:":20}{max_gain_date.strftime("%m/%d/%Y")}')
        print(f'{"Closing Price:":20}' + "$ {:,.2f}".format(max_gain_closing_price))
        print(f'{"Change %:":20}' + "{:,.2f}".format(np.round(max_gain_percentage, 3)) + " %")
        print(f'{"Change $:":20}' + "$ {:,.2f}".format(max_gain_amount))
        print("\nMax loss")
        print(f'{"Date:":20}{max_loss_date.strftime("%m/%d/%Y")}')
        print(f'{"Closing Price:":20}' + "$ {:,.2f}".format(max_loss_closing_price))
        print(f'{"Change %:":20}' + "{:,.2f}".format(np.round(max_loss_percentage, 3)) + " %")
        print(f'{"Change $:":20}' + "$ {:,.2f}".format(max_loss_amount))
        print("\nAvg changes")
        print(f'{"Avg change %:":20}' + "{:,.2f}".format(np.round(avg_change, 3)) + " %")
        print(f'{"Avg gain %:":20}' + "{:,.2f}".format(np.round(avg_gain, 3)) + " %")
        print(f'{"Avg loss %:":20}' + "{:,.2f}".format(np.round(avg_loss, 3)) + " %")
        print("\nMax & low closing prices")
        print(f'{"Date:":20}{max_price_date.strftime("%m/%d/%Y")}')
        print(f'{"Max price:":20}' + "$ {:,.2f}".format(max_price))
        print(f'{"Date:":20}{low_price_date.strftime("%m/%d/%Y")}')
        print(f'{"Low price:":20}' + "$ {:,.2f}".format(low_price))
        print(f'{"Spread $:":20}' + "$ {:,.2f}".format(max_price - low_price))
        print()

    except Exception as error:
        print(repr(error))
        print("\n")


def last_day_of_month(any_day):
    # this will never fail
    # get close to the end of the month for any day, and add 4 days 'over'
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    # subtract the number of remaining 'overage' days to get last day of current month, or said programmatically said,
    # the previous day of the first of next month
    return next_month - datetime.timedelta(days=next_month.day)


def monthly_returns_ytd(symbol):
    try:
        today = datetime.datetime.now()
        start = last_day_of_month(datetime.date(datetime.datetime.now().year - 1, 12, 1))
        start -= datetime.timedelta(days=30)
        end = datetime.date(today.year, today.month, today.day)
        eom_business_days = pd.date_range(start, end, freq='BM')

        eom_first_day_previous_year = last_day_of_month(datetime.date(datetime.datetime.now().year - 1, 12, 1))
        eom_first_day_previous_year -= datetime.timedelta(days=30)

        history = yf.download(symbol, start=eom_first_day_previous_year.strftime("%Y-%m-%d"),
                              end=today.strftime("%Y-%m-%d"))

        eom_trading_days = list()
        # Export closing dates and prices to a Pandas Series
        closing_prices = history["Close"]

        # Iterate through calculated eom business days
        for date in eom_business_days:
            curr_date = date
            # If there is no closing price for the calculated eom business day, then continually subtract one day
            # until the last trading day is found. Import to note that the pre-calculated eom business day is not
            # always the last trading day of a given month
            while curr_date not in closing_prices.keys():
                curr_date -= datetime.timedelta(days=1)
            eom_trading_days.append(curr_date)

        print("Monthly gains YTD\n")
        for i in range(1, len(eom_trading_days)):
            if eom_trading_days[i] in closing_prices.keys():
                eom_price = closing_prices[eom_trading_days[i]]
                previous_eom_price = closing_prices[eom_trading_days[i - 1]]
                percent_change = ((eom_price / previous_eom_price) - 1) * 100
                print(f'{"EOM trading day:":30}{eom_trading_days[i].strftime("%m/%d/%Y")}')
                print(f'{"EOM Price:":30}' + "$ {:,.2f}".format(eom_price))
                print(f'{"Previous EOM Price:":30}' + "$ {:,.2f}".format(previous_eom_price))
                print(f'{"Change %:":30}' + "{:,.2f}".format(np.round(percent_change, 3)) + " %\n")
    except Exception as error:
        print(repr(error))
        print("\n")


if __name__ == "__main__":
    while True:
        # Valid periods are: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        ticker = input("Enter a ticker: ").strip()
        period = input("Enter a period: ").strip()
        print()
        get_stats(ticker, period)
        choice = input('Continue (y/n)? ').lower()
        while choice not in ['y', 'n']:
            choice = input('Continue (y/n)? ').lower()
        if choice == 'n':
            print('\n')
            break
