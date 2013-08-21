import datetime as dt




# Stat filters
# Should return boolean True or False

default_filters = [('all',lambda t: True),
                ('long',lambda t: t.shares > 0),
                ('short',lambda t: t.shares < 0),
                ('winners',lambda t: t.theo_ret > 0),
                ('losers',lambda t: t.theo_ret < 0),
                ('last_6mon',lambda t: (dt.datetime.now() - t.open_dt).days < (365*0.5)),
                ('last_12mon',lambda t: (dt.datetime.now() - t.open_dt).days < (365*1.0)),
                ('last_18mon',lambda t: (dt.datetime.now() - t.open_dt).days < (365*1.5)),
                ('wkd00',lambda t: t.open_dt.weekday() == 0),
                ('wkd01',lambda t: t.open_dt.weekday() == 1),
                ('wkd02',lambda t: t.open_dt.weekday() == 2),
                ('wkd03',lambda t: t.open_dt.weekday() == 3),
                ('wkd04',lambda t: t.open_dt.weekday() == 4),
                ('mon01',lambda t: t.open_dt.month == 1),
                ('mon02',lambda t: t.open_dt.month == 2),
                ('mon03',lambda t: t.open_dt.month == 3),
                ('mon04',lambda t: t.open_dt.month == 4),
                ('mon05',lambda t: t.open_dt.month == 5),
                ('mon06',lambda t: t.open_dt.month == 6),
                ('mon07',lambda t: t.open_dt.month == 7),
                ('mon08',lambda t: t.open_dt.month == 8),
                ('mon09',lambda t: t.open_dt.month == 9),
                ('mon10',lambda t: t.open_dt.month == 10),
                ('mon11',lambda t: t.open_dt.month == 11),
                ('mon12',lambda t: t.open_dt.month == 12),
                ]


# Metric filters
# Should return a value


