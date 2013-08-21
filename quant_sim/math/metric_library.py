import math
from copy import deepcopy

from numpy import mean

from quant_sim.math.metric import Metric

class CountIf(Metric):
    def process_data(self, x):
        if x:
            return self.val + 1
        else:
            return 0

class MA(Metric):
    def initialize(self, *args, **kwargs):
        self.sum = 0.0

    def process_data(self, x):
        self.sum += (x - self.popped)
        return self.sum / float(min(self.n, self.window))

class Stdev(Metric):
    def initialize(self, *args, **kwargs):
        self.sum_x = 0.0
        self.sum_x2 = 0.0
        self.func = kwargs.get('func', None)

    def process_data(self, env, trade):
        self.sum_x += self.func(trade)
        self.sum_x2 += (self.func(trade) * self.func(trade))
        mean = self.sum_x / self.n
        return math.sqrt((self.sum_x2 / self.n) - (mean * mean))

class Max(Metric):
    def process_data(self, x):
        if self.history == []:
            return x
        else:
            return max(self.history)

class Min(Metric):
    def process_data(self, x):
        if self.history == []:
            return x
        else:
            return min(self.history)

class ATR(Metric):
    def initialize(self, *args, **kwargs):
        self.sum = 0.0

    def process_data(self, eod):
        tr = max((eod.h - eod.l), abs(eod.h - eod[1].c), abs(eod.l - eod[1].c))
        self.sum += (tr - self.popped)
        return self.sum / float(min(self.n, self.window))

class Mon_Seas(Metric):
    def initialize(self, start, end, *args, **kwargs):
        #self.trading_days = get_trading_days(start, end)
        self.normalized = {}
        ordered_days = []
        for i in range(21):
            ordered_days += [i+1]
        for i in range(21):
            self.normalized[i+1] = {'n':0, 'sum':0.0, 'raw':[], 'vals':0.0, 'norm':None}
        self.normalized['norm'] = 1
        self.normalized['ordered'] = ordered_days
        self.day_n = 0

    def process_data(self, eod):
        popped = 0.0
        self.day_n += 1
        if eod.d.month != eod[1].d.month:
            self.day_n = 1
        x = len([d for d in self.trading_days if d.year == eod.d.year and d.month == eod.d.month])
        norm = int(round((self.day_n / float(x)) * 20.0))
        if norm > 20:
            norm = 20
        self.normalized['norm'] = norm
        if self.normalized[norm]['n'] >= 12*10:
            popped = self.normalized[norm]['raw'].pop(0)
        if self.normalized[norm]['n'] < 12*10:
            self.normalized[norm]['n'] += 1
        self.normalized[norm]['raw'] += [eod.c / eod[1].c - 1.0]
        self.normalized[norm]['sum'] = (self.normalized[norm]['sum'] - popped + (eod.c / eod[1].c - 1.0))
        val = self.normalized[norm]['sum'] / self.normalized[norm]['n']
        self.normalized[norm]['vals'] = mean(self.normalized[norm]['raw'])
        self.normalized['ordered'].sort(key=lambda x: self.normalized[x]['vals'])
        return deepcopy(self.normalized)

all_metrics = [MA(id='sma',val=0.0,window=10,func="env['SPY'].c"),
               Max(id='max',val=0.0,func="env['SPY'].c"),
               MA(id='abs_night_gap',val=0.0, func="abs(env['SPY'].o / env.get('SPY',1).c - 1.0)"),
               ATR(id='atr', val=0.0, func="env['SPY']")
              ]
