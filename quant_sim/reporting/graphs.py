import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook


class simple_plot(object):
    def __init__(self, trades, fn):
        if len(trades) == 0:  
            plt.savefig(fn+'.png', edgecolor='b')
            return
        years    = mdates.YearLocator()   # every year
        months   = mdates.MonthLocator()  # every month
        yearsFmt = mdates.DateFormatter('%Y')
        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        dates = [t.open_dt for t in trades]
        roi = [1.0]
        for t in trades:
            roi += [roi[-1] * (t.theo_ret + 1.0)]
        roi.pop(0)
        ax.plot(dates, roi)

        # format the ticks
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(yearsFmt)
        ax.xaxis.set_minor_locator(months)

        datemin = datetime.date(dates[0].year, 1, 1)
        datemax = datetime.date(dates[-1].year+1, 1, 1)
        ax.set_xlim(dates[0], dates[-1])

        # format the coords message box
        def price(x): return '$%1.2f'%x
        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        ax.format_ydata = price
        ax.grid(True)

        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()

        plt.savefig(fn+'.png', edgecolor='b')