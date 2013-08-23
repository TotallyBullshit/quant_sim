
import datetime as dt
from copy import deepcopy


from quant_sim.stats_mgmt.filter_library import default_filters
from quant_sim.stats_mgmt.stat_library import all_stats
from quant_sim.tools.helpers import toposort2


class Statistics_New(object):
    def __init__(self, *args, **kwargs):
        """
        Statistics manager which manages a dict of dicts where 
        self.stats[filter_key][stat_key] = stat value
        and
        self.calc[filter_key][stat_key] = algorithm to compute stat value
        these are kept in separate dict for output purposes. Performance and
        risk metrics are the primary statistics being tracked for all trades
        of a trading algorithm.

        Parameters
        ---------- 
        filters : list of tuples or single tuple, optional
                  tuple is (filter_key, filter_func)
        stats : list of quant.math.stat.Stat objects, optional

        a filter is a tuple of the filter key and the filter function
        the filter function can be a complex named function or simple
        lambda function. The function must only take one input, the
        closed trade. The function will route the trade to respective
        stats the trade applies to.

        stats is a list of instantiated Stat objects as defined in 
        quant.math.stat

        Returns
        -------
        n/a
        
        See Also
        --------
        n/a

        Notes
        -----
        n/a
        
        Examples
        --------
        self.stats = Statistics()
        self.stats.add_filter([('long',lambda t: t.shares > 0)])
        self.stats.add_stat([Mean('mean_theo',attr=lambda t:t.theo_ret)])

        or

        self.stats = Statistics(filters=[('long',lambda t: t.shares >0)],
                        stats=[Mean('mean_theo',attr=lambda t:t.theo_ret)])

        or pass stats and filters into the parent object quant.simulator
        and or quant.algorithm then pass through to quant.math.statistics

        self.stats = Statistics(*args, **kwargs)

        """
        self.n = 0
        self.stats = {'all':{'start_dt':dt.datetime(3000,1,1), 'end_dt':dt.datetime(1900,1,1)}}
        self.calcs = {'all':{}}
        self.filters = []
        self.sorted_stat_keys = []
        self.unsorted_stat_keys = {}
        self.add_filter(default_filters + kwargs.get('filters',[]))
        self.add_stat(kwargs.get('stats',all_stats))
        
    def add_filter(self, filters):
        """
        ---PURPOSE---
        a filter is a tuple of the filter key and the filter function
        the filter function can be a complex named function or simple
        lambda function. The function must only take one input, the
        closed trade. The function will route the trade to respective
        stats the trade applies to.
        
        ---INPUT---
        filter tuple = (filter_key, filter_func)
        
        ---USAGE---
        stat_mngr.add_filter([('monday', lambda x: x.open_dt.weekday() == 0),
                             ('short', lambda x: x.shares < 0)])
        """
        if len(self.stats['all']) > 2:
            raise EnvironmentError('Filters must be added before stats')
        if type(filters) != list:
            filters = [filters]
        for filt in filters:
            self.calcs[filt[0]] = {}
            if filt[0] != 'all': self.stats[filt[0]] = {}
        self.filters += filters
        
    def add_stat(self, stats):
        if type(stats) != list:
            stats = [stats]
        for stat in stats:
            self.unsorted_stat_keys[stat.id] = stat.reqs
            for filter_key, filter_calc in self.filters:
                self.calcs[filter_key][stat.id] = deepcopy(stat)
                self.stats[filter_key][stat.id] = self.calcs[filter_key][stat.id].val
        self.sorted_stat_keys = [item for sublist in toposort2(self.unsorted_stat_keys) for item in sublist]


    def update(self, env, closed=None):
        closed_n = len(closed) if closed != None else 0
        for stat_key in self.sorted_stat_keys:
            if self.calcs['all'][stat_key].on_bar:
                for filter_key, filter_func in self.filters:
                    self.calcs[filter_key][stat_key].update(env, self.stats, filter_key, None)
                    self.stats[filter_key][stat_key] = self.calcs[filter_key][stat_key].val
            elif self.calcs['all'][stat_key].on_trade and closed != None and self.n != closed_n:
                for filter_key, filter_func in self.filters:
                    for trade in closed[self.n:]:
                        if filter_func(trade):
                            self.calcs[filter_key][stat_key].update(env, self.stats, filter_key, trade)
                            self.stats[filter_key][stat_key] = self.calcs[filter_key][stat_key].val

        self.n = closed_n

class Statistics(object):
    def __init__(self, *args, **kwargs):
        """
        Statistics manager which manages a dict of dicts where 
        self.stats[filter_key][stat_key] = stat value
        and
        self.calc[filter_key][stat_key] = algorithm to compute stat value
        these are kept in seperate dict for output purposes. Performance and
        risk metrics are the primary statistics being tracked for all trades
        of a trading algorithm.

        Parameters
        ---------- 
        filters : list of tuples or single tuple, optional
                  tuple is (filter_key, filter_func)
        stats : list of quant.math.stat.Stat objects, optional

        a filter is a tuple of the filter key and the filter function
        the filter function can be a complex named function or simple
        lambda function. The function must only take one input, the
        closed trade. The function will route the trade to respective
        stats the trade applies to.

        stats is a list of instantiated Stat objects as defined in 
        quant.math.stat

        Returns
        -------
        n/a
        
        See Also
        --------
        n/a

        Notes
        -----
        n/a
        
        Examples
        --------
        self.stats = Statistics()
        self.stats.add_filter([('long',lambda t: t.shares > 0)])
        self.stats.add_stat([Mean('mean_theo',attr=lambda t:t.theo_ret)])

        or

        self.stats = Statistics(filters=[('long',lambda t: t.shares >0)],
                        stats=[Mean('mean_theo',attr=lambda t:t.theo_ret)])

        or pass stats and filters into the parent object quant.simulator
        and or quant.algorithm then pass through to quant.math.statistics

        self.stats = Statistics(*args, **kwargs)

        """
        self.n = 0
        self.stats = {'all':{'start_dt':dt.datetime(3000,1,1), 'end_dt':dt.datetime(1900,1,1)}}
        self.calcs = {'all':{}}
        self.filters = []
        self.sorted_stat_keys = []
        self.unsorted_stat_keys = {}
        self.add_filter(default_filters + kwargs.get('filters',[]))
        self.add_stat(kwargs.get('stats',all_stats))
        
    def add_filter(self, filters):
        """
        ---PURPOSE---
        a filter is a tuple of the filter key and the filter function
        the filter function can be a complex named function or simple
        lambda function. The function must only take one input, the
        closed trade. The function will route the trade to respective
        stats the trade applies to.
        
        ---INPUT---
        filter tuple = (filter_key, filter_func)
        
        ---USAGE---
        stat_mngr.add_filter([('monday', lambda x: x.open_dt.weekday() == 0),
                             ('short', lambda x: x.shares < 0)])
        """
        if len(self.stats['all']) > 2:
            raise EnvironmentError('Filters must be added before stats')
        if type(filters) != list:
            filters = [filters]
        for filt in filters:
            self.calcs[filt[0]] = {}
            if filt[0] != 'all': self.stats[filt[0]] = {}
        self.filters += filters
        
    def add_stat(self, stats):
        if type(stats) != list:
            stats = [stats]
        for stat in stats:
            self.unsorted_stat_keys[stat.id] = stat.reqs
            for filter_key, filter_calc in self.filters:
                self.calcs[filter_key][stat.id] = deepcopy(stat)
                self.stats[filter_key][stat.id] = self.calcs[filter_key][stat.id].val
        self.sorted_stat_keys = [item for sublist in toposort2(self.unsorted_stat_keys) for item in sublist]


    def update(self, env, closed=None):
        if type(closed) != list and closed != None:
            closed = [closed]
        closed_n = len(closed) if closed != None else 0
        for stat_key in self.sorted_stat_keys:
            if self.calcs['all'][stat_key].on_bar:
                for filter_key, filter_func in self.filters:
                    self.calcs[filter_key][stat_key].update(env, self.stats, filter_key, None)
                    self.stats[filter_key][stat_key] = self.calcs[filter_key][stat_key].val
            elif self.calcs['all'][stat_key].on_trade and closed != None and closed_n > 0:
                for filter_key, filter_func in self.filters:
                    for trade in closed:
                        if filter_func(trade):
                            self.calcs[filter_key][stat_key].update(env, self.stats, filter_key, trade)
                            self.stats[filter_key][stat_key] = self.calcs[filter_key][stat_key].val
        self.n += closed_n

