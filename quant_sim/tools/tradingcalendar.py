#
# Copyright 2012 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import pytz

from datetime import datetime, timedelta
from dateutil import rrule, easter
from quant.utils.date_utils import utcnow



def get_easter(start, end):
    return [datetime(easter.easter(y).year, easter.easter(y).month, easter.easter(y).day) for y in range(start.year, end.year+1)]

def get_opex_friday(start, end):
    rules = []
    opex_day = rrule.rrule(
        rrule.MONTHLY,
        byweekday=(rrule.FR(+3)),
        cache=True,
        dtstart=start,
        until=end
    )
    rules.append(opex_day)
    ruleset = rrule.rruleset()
    for rule in rules:
        ruleset.rrule(rule)
    days = ruleset.between(start, end, inc=True)
    return days

def get_nontrading_days(start,end):
    non_trading_rules = []

    weekends = rrule.rrule(
        rrule.YEARLY,
        byweekday=(rrule.SA, rrule.SU),
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(weekends)

    new_years = rrule.rrule(
        rrule.MONTHLY,
        byyearday=1,
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(new_years)

    new_years_sun = rrule.rrule(
        rrule.MONTHLY,
        byyearday=2,
        byweekday=(rrule.MO),
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(new_years_sun)    
    
    mlk_day = rrule.rrule(
        rrule.MONTHLY,
        bymonth=1,
        byweekday=(rrule.MO(+3)),
        cache=True,
        dtstart=datetime(1998,01,01),
        until=end
    )
    non_trading_rules.append(mlk_day)


    presidents_day = rrule.rrule(
        rrule.MONTHLY,
        bymonth=2,
        bymonthday=22,
        cache=True,
        dtstart=datetime(1950, 01, 01),
        until=datetime(1971,01,01)
    )
    non_trading_rules.append(presidents_day)

    presidents_day_mon = rrule.rrule(
        rrule.MONTHLY,
        bymonth=2,
        byweekday=(rrule.MO(3)),
        cache=True,
        dtstart=datetime(1971,01,01),
        until=end
    )
    non_trading_rules.append(presidents_day_mon)

    good_friday = rrule.rrule(
        rrule.DAILY,
        byeaster=-2,
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(good_friday)

    memorial_day = rrule.rrule(
        rrule.MONTHLY,
        bymonth=5,
        bymonthday=30,
        cache=True,
        dtstart=datetime(1950,01,01),
        until=datetime(1971,01,01)
    )
    
    non_trading_rules.append(memorial_day)

    memorial_mon = rrule.rrule(
        rrule.MONTHLY,
        bymonth=5,
        byweekday=(rrule.MO(-1)),
        cache=True,
        dtstart=datetime(1971,01,01),
        until=end
    )
    
    non_trading_rules.append(memorial_mon)

    paperwork_crisis = rrule.rrule(
        rrule.WEEKLY,
        byweekday=rrule.WE, 
        cache=True,
        dtstart=datetime(1968,6,11),
        until=datetime(1968,12,31)
        )

    non_trading_rules.append(paperwork_crisis)
    
    july_4th_sat = rrule.rrule(
        rrule.MONTHLY,
        bymonth=7,
        byweekday=(rrule.FR),
        bymonthday=3,
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(july_4th_sat)    
    
    july_4th = rrule.rrule(
        rrule.MONTHLY,
        bymonth=7,
        bymonthday=4,
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(july_4th)
   
    july_4th_sun = rrule.rrule(
        rrule.MONTHLY,
        bymonth=7,
        byweekday=(rrule.MO),
        bymonthday=5,
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(july_4th_sun)
    
    labor_day = rrule.rrule(
        rrule.MONTHLY,
        bymonth=9,
        byweekday=(rrule.MO(1)),
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(labor_day)

    thanksgiving = rrule.rrule(
        rrule.MONTHLY,
        bymonth=11,
        byweekday=(rrule.TH(4)),
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(thanksgiving)

    election = rrule.rrule(
        rrule.YEARLY,
        bymonth=11,
        byweekday=rrule.TU,
        bymonthday=(2,3,4,5,6,7,8),
        cache=True,
        dtstart=datetime(1950,01,01),
        until=datetime(1968,12,01)
        )

    non_trading_rules.append(election)


    pres_election = rrule.rrule(
        rrule.YEARLY, 
        interval=4,
        bymonth=11,
        byweekday=rrule.TU, 
        bymonthday=(2,3,4,5,6,7,8),
        cache=True,
        dtstart=datetime(1972,01,01),
        until=datetime(1980,12,01)
        )

    non_trading_rules.append(pres_election)

    christmas_sat = rrule.rrule(
        rrule.MONTHLY,
        bymonth=12,
        byweekday=(rrule.FR),
        bymonthday=24,
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(christmas_sat)    
    
    christmas = rrule.rrule(
        rrule.MONTHLY,
        bymonth=12,
        bymonthday=25,
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(christmas)

    christmas_sun = rrule.rrule(
        rrule.MONTHLY,
        bymonth=12,
        byweekday=(rrule.MO),
        bymonthday=26,
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(christmas_sun)

    non_trading_ruleset = rrule.rruleset()

    for rule in non_trading_rules:
        non_trading_ruleset.rrule(rule)

    non_trading_days = non_trading_ruleset.between(start, end, inc=True)

    # Add September 11th closings
    # http://en.wikipedia.org/wiki/Aftermath_of_the_September_11_attacks
    # Due to the terrorist attacks, the stock market did not open on 9/11/2001
    # It did not open again until 9/17/2001.
    #
    #    September 2001
    # Su Mo Tu We Th Fr Sa
    #                    1
    #  2  3  4  5  6  7  8
    #  9 10 11 12 13 14 15
    # 16 17 18 19 20 21 22
    # 23 24 25 26 27 28 29
    # 30

    for day_num in range(11, 17):
        non_trading_days.append(
            datetime(2001, 9, day_num))

    # Add closings due to Hurricane Sandy in 2012
    # http://en.wikipedia.org/wiki/Hurricane_sandy
    #
    # The stock exchange was closed due to Hurricane Sandy's
    # impact on New York.
    # It closed on 10/29 and 10/30, reopening on 10/31
    #     October 2012
    # Su Mo Tu We Th Fr Sa
    #     1  2  3  4  5  6
    #  7  8  9 10 11 12 13
    # 14 15 16 17 18 19 20
    # 21 22 23 24 25 26 27
    # 28 29 30 31

    for day_num in range(29, 31):
        non_trading_days.append(
            datetime(2012, 10, day_num))

    # Misc closings from NYSE listing.
    # http://www.nyse.com/pdfs/closings.pdf
    #
    #  Day before Decoration Day
    non_trading_days.append(datetime(1961, 5, 29))
    #  Presidents day friday one time close
    non_trading_days.append(datetime(1964, 2, 21))
     #  memorial day friday one time close
    non_trading_days.append(datetime(1964, 5, 29))
    non_trading_days.append(datetime(1965, 5, 31))
    # Lincolns birthday
    non_trading_days.append(datetime(1968, 2, 12))
    # MLK Mounrning
    non_trading_days.append(datetime(1968, 4, 9))

    # National Days of Mourning
    # - President John F. Kennedy
    non_trading_days.append(datetime(1963, 11, 25))
    # - President Richard M. Nixon - April 27, 1994
    non_trading_days.append(datetime(1994, 4, 27))
    # - President Ronald W. Reagan - June 11, 2004
    non_trading_days.append(datetime(2004, 6, 11))
    # - President Gerald R. Ford - Jan 2, 2007
    non_trading_days.append(datetime(2007, 1, 2))
    return non_trading_days

def get_trading_days(start, end):
    non_trading = get_nontrading_days(start,end)
    trading_days = []
    while start <= end:
        start += timedelta(1)
        if start not in non_trading:
            trading_days += [start]
    return trading_days