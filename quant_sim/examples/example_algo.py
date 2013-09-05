import math

from collections import OrderedDict

from quant_sim.tools.helpers import create_lambda
from quant_sim.finances.algorithm import Algorithm
from quant_sim.math.metric_library import *


def state_of_market(pod, eod0, eod1):
    nod = OrderedDict()
    nod['dow'] = eod0.dow
    nod['IB'] = pod.get('IB',0) + 1 if eod0.h < eod1.h and eod0.l > eod1.l else 0
    nod['OB'] = pod.get('OB',0) + 1 if eod0.h > eod1.h and eod0.l < eod1.l else 0
    nod['HH'] = pod.get('HH',0) + 1 if eod0.h > eod1.h else 0
    nod['HL'] = pod.get('HL',0) + 1 if eod0.l > eod1.l else 0
    nod['LH'] = pod.get('LH',0) + 1 if eod0.h < eod1.h else 0
    nod['LL'] = pod.get('LL',0) + 1 if eod0.l < eod1.l else 0
    nod['cc-dir'] = 1 if eod0.c > eod1.c else 2 if eod0.c < eod1.c else 0
    nod['co-dir'] = 1 if eod0.o > eod1.c else 2 if eod0.o < eod1.c else 0
    nod['oc-dir'] = 1 if eod0.c > eod0.o else 2 if eod0.c < eod0.o else 0
    nod['cc-dir-consec'] = pod.get('cc-dir-consec',0) + 1 if nod['cc-dir'] == pod.get('cc-dir',0) else 1
    nod['co-dir-consec'] = pod.get('co-dir-consec',0) + 1 if nod['co-dir'] == pod.get('co-dir',0) else 1
    nod['oc-dir-consec'] = pod.get('oc-dir-consec',0) + 1 if nod['oc-dir'] == pod.get('oc-dir',0) else 1
    nod['gap-filled'] = pod.get('gap-filled',0) + 1 if (eod0.o < eod1.c and eod0.h >= eod1.c) or (eod0.o > eod1.c and eod0.l <= eod1.c) else 1
    return nod

class MarketState(Algorithm):
    def initialize(self, *args, **kwargs):
        self.sid = kwargs.get('sid', 'SPY')
        self.id = 'Study for output (%s)' % (self.sid)
        self.desc = 'Output this study'
        self.ignore_old = False
        self.initialize_recorder(['state'], False, 'J:/LanahanMain/code_projects/quant_sim/quant_sim/reporting/records/'+self.id+'record.csv')
        self.add_metric(MA(id='sma10',val=0.0,window=10,func="env['SPY'].c"))
        self.add_metric(MA(id='sma20',val=0.0,window=20,func="env['SPY'].c"))
        self.add_metric(MA(id='sma50',val=0.0,window=50,func="env['SPY'].c"))
        self.add_metric(MA(id='sma200',val=0.0,window=200,func="env['SPY'].c"))
        self.add_metric(Max(id='H10',val=0.0,cache_n=2,window=10,func="env['SPY'].c"))
        self.add_metric(Max(id='H20',val=0.0,cache_n=2,window=20,func="env['SPY'].c"))
        self.add_metric(Max(id='H50',val=0.0,cache_n=2,window=50,func="env['SPY'].c"))
        self.add_metric(Min(id='L10',val=0.0,cache_n=2,window=10,func="env['SPY'].c"))
        self.add_metric(Min(id='L20',val=0.0,cache_n=2,window=20,func="env['SPY'].c"))
        self.add_metric(Min(id='L50',val=0.0,cache_n=2,window=50,func="env['SPY'].c"))
        self.add_metric(Max(id='iH10',val=0.0,cache_n=2,window=10,func="env['SPY'].h"))
        self.add_metric(Max(id='iH20',val=0.0,cache_n=2,window=20,func="env['SPY'].h"))
        self.add_metric(Max(id='iH50',val=0.0,cache_n=2,window=50,func="env['SPY'].h"))
        self.add_metric(Min(id='iL10',val=0.0,cache_n=2,window=10,func="env['SPY'].l"))
        self.add_metric(Min(id='iL20',val=0.0,cache_n=2,window=20,func="env['SPY'].l"))
        self.add_metric(Min(id='iL50',val=0.0,cache_n=2,window=50,func="env['SPY'].l"))
        self.pod = OrderedDict()

    def process_data(self, env, *args, **kwargs):
        eod0 = env.get(self.sid,0)
        eod1 = env.get(self.sid,1)
        nod = state_of_market(self.pod, eod0, eod1)
        nod['H10'] = 1 if eod0.c > self.metrics.funcs['H10'].cache[1] else 0
        nod['H20'] = 1 if eod0.c > self.metrics.funcs['H20'].cache[1] else 0
        nod['H50'] = 1 if eod0.c > self.metrics.funcs['H50'].cache[1] else 0
        nod['L10'] = 1 if eod0.c < self.metrics.funcs['L10'].cache[1] else 0
        nod['L20'] = 1 if eod0.c < self.metrics.funcs['L20'].cache[1] else 0
        nod['L50'] = 1 if eod0.c < self.metrics.funcs['L50'].cache[1] else 0
        nod['iH10'] = 1 if eod0.c > self.metrics.funcs['iH10'].cache[1] else 0
        nod['iH20'] = 1 if eod0.c > self.metrics.funcs['iH20'].cache[1] else 0
        nod['iH50'] = 1 if eod0.c > self.metrics.funcs['iH50'].cache[1] else 0
        nod['iL10'] = 1 if eod0.c < self.metrics.funcs['iL10'].cache[1] else 0
        nod['iL20'] = 1 if eod0.c < self.metrics.funcs['iL20'].cache[1] else 0
        nod['iL50'] = 1 if eod0.c < self.metrics.funcs['iL50'].cache[1] else 0
        nod['sma10'] = 1 if eod0.c > self.metrics['sma10'] else 2
        nod['sma20'] = 1 if eod0.c > self.metrics['sma20'] else 2
        nod['sma50'] = 1 if eod0.c > self.metrics['sma50'] else 2
        nod['sma200'] = 1 if eod0.c > self.metrics['sma200'] else 2
        nod['sma10-consec'] = self.pod.get('sma10-consec',0) + 1 if nod['sma10'] == self.pod.get('sma10',0) else 1
        nod['sma20-consec'] = self.pod.get('sma20-consec',0) + 1 if nod['sma20'] == self.pod.get('sma20',0) else 1
        nod['sma50-consec'] = self.pod.get('sma50-consec',0) + 1 if nod['sma50'] == self.pod.get('sma50',0) else 1
        nod['sma200-consec'] = self.pod.get('sma200-consec',0) + 1 if nod['sma200'] == self.pod.get('sma200',0) else 1
        self.record({'state': '  :  '.join(['%s-%d'%(k,v) for k,v in nod.items() if v > 0])})
        self.pod = nod

class Alg_001(Algorithm):
    def initialize(self, *args, **kwargs):
        self.id = 'test'
        self.desc = 'test algorithm for rare set ups'
        self.ignore_old = False
        self.initialize_recorder(['avg-ret','OB','c','ma','c>o'], False, 'J:/LanahanMain/code_projects/quant_sim/quant_sim/reporting/records/'+self.id+'record.csv')
        self.add_metric(MA(id='sma',val=0.0,window=10,func="env['SPY'].c"))

    def process_data(self, env, *args, **kwargs):
        sid = '^GSPC'
        eod0 = env.get(sid,0)
        eod1 = env.get(sid,1)
        self.record({'ma':self.metrics['sma'],'OB':eod0.h > eod1.h and eod0.l < eod1.l, 'c':eod0.c, 'c>o':eod0.c>eod0.o})
        if eod0.d.month == 3 and eod0.nth_dow == 2 and eod0.dow == 4:
            self.order(sid, 20, eod0.c)
        elif eod0.d.month == 3 and eod0.next.nth_dow == 3 and eod0.next.dow == 4:
            self.order(sid, -20, eod0.c)
        elif eod0.d.month == 3 and eod0.d.day > 27 and self.order_mngr.active_pos[sid]['n'] > 0:
            self.order(sid, -20, eod0.c)

class Alg_002(Algorithm):
    def initialize(self, *args, **kwargs):
        self.ignore_old = True
        self.sid = kwargs.get('sid', 'SPY')
        self.id = 'Labor Day Fri.c - Tue.o (%s)'%self.sid
        self.desc = 'Buy $10,000 %s at the Close, the Friday before Labor Day<br>Sell at the Open, the Tuesday after Labor Day' % self.sid
        #self.helper = create_lambda('lambda env, metrics:', helper)
        #self.initialize_recorder(['c','50sma','co-dir','co-ret','oc-dir','oc-ret'], False, 'J:/LanahanMain/code_projects/quant_sim/quant_sim/reporting/records/'+self.id+'record.csv')
        self.add_metric(MA(id='50sma',val=0.0,window=50,func="env['SPY'].c"))

    def process_data(self, env,  *args, **kwargs):
        sid = self.sid
        eod0 = env.get('SPY',0)
        eod1 = env.get(sid,1)
        shares = math.floor(self.order_mngr.active_pos['all']['bal'] / eod0.c)
        if eod0.next.d.month == 9 and eod0.next.dow == 1 and eod0.dow == 4:
            #self.record({'c':eod0.c, '50sma':self.metrics['50sma'], 'co-dir':1 if eod0.o > eod1.c else 0, 'co-ret':eod0.o / eod1.c - 1.0,'oc-dir':1 if eod0.c > eod0.o else 0, 'oc-ret':eod0.c / eod0.o - 1.0})
            self.order(sid, 10 , eod0.c)
        elif eod0.d.month == 9 and eod0.dow == 1 and 1 < eod0.d.day < 9:
            self.order(sid, -self.order_mngr.active_pos[sid]['shares'], eod0.o)

class Alg_003(Algorithm):
    def initialize(self, *args, **kwargs):
        self.ignore_old = False
        self.sid = kwargs.get('sid', 'SPY')
        self.id = 'Labor Day Fri.o - Fri.c Before (%s)'%self.sid
        self.desc = 'Buy $10,000 %s at the Open, the Friday before Labor Day<br>Sell at the Close' % self.sid
        #self.helper = create_lambda('lambda env, metrics:', helper)
        #self.initialize_recorder(['c','50sma','co-dir','co-ret','oc-dir','oc-ret'], False, 'J:/LanahanMain/code_projects/quant_sim/quant_sim/reporting/records/'+self.id+'record.csv')
        self.add_metric(MA(id='50sma',val=0.0,window=50,func="env['SPY'].c"))

    def process_data(self, env,  *args, **kwargs):
        sid = self.sid
        eod0 = env.get(sid,0)
        eod1 = env.get(sid,1)
        shares = math.floor(self.order_mngr.active_pos['all']['bal'] / eod0.c)
        if eod0.next.d.month == 9 and eod0.next.dow == 1 and eod0.dow == 4:
            #self.record({'c':eod0.c, '50sma':self.metrics['50sma'], 'co-dir':1 if eod0.o > eod1.c else 0, 'co-ret':eod0.o / eod1.c - 1.0,'oc-dir':1 if eod0.c > eod0.o else 0, 'oc-ret':eod0.c / eod0.o - 1.0})
            self.order(sid, shares , eod0.o)
            self.order(sid, -self.order_mngr.active_pos[sid]['shares'], eod0.c)
            
class Alg_004(Algorithm):
    def initialize(self, *args, **kwargs):
        self.sid = kwargs.get('sid', 'SPY')
        self.id = 'Labor Day Tues.o - Tues.c After (%s)'%self.sid
        self.desc = 'Buy $10,000 %s at the Open, the Tuesday after Labor Day<br>Sell at the Close' % self.sid
        self.ignore_old = False
        #self.helper = create_lambda('lambda env, metrics:', helper)
        #self.initialize_recorder(['c','50sma','co-dir','co-ret','oc-dir','oc-ret'], False, 'J:/LanahanMain/code_projects/quant_sim/quant_sim/reporting/records/'+self.id+'record.csv')
        self.add_metric(MA(id='50sma',val=0.0,window=50,func="env['SPY'].c"))

    def process_data(self, env,  *args, **kwargs):
        sid = self.sid
        eod0 = env.get(sid,0)
        eod1 = env.get(sid,1)
        shares = math.floor(self.order_mngr.active_pos['all']['bal'] / eod0.c)
        if eod0.d.month == 9 and eod0.dow == 1 and 1 < eod0.d.day < 9:
            #self.record({'c':eod0.c, '50sma':self.metrics['50sma'], 'co-dir':1 if eod0.o > eod1.c else 0, 'co-ret':eod0.o / eod1.c - 1.0,'oc-dir':1 if eod0.c > eod0.o else 0, 'oc-ret':eod0.c / eod0.o - 1.0})
            self.order(sid, shares , eod0.o)
        #elif eod0.d.month == 9 and eod0.dow == 1 and 1 < eod0.d.day < 9:
            self.order(sid, -self.order_mngr.active_pos[sid]['shares'], eod0.c)

class Alg_005(Algorithm):
    def initialize(self, *args, **kwargs):
        self.sid = kwargs.get('sid', 'SPY')
        self.id = 'Labor Day Tue.o - Fri.c After (%s)'%self.sid
        self.desc = 'Buy $10,000 %s at the Open, the Tuesday after Labor Day<br>Sell at the Close, the Friday after Labor Day' % self.sid
        self.ignore_old = False
        #self.helper = create_lambda('lambda env, metrics:', helper)
        #self.initialize_recorder(['c','50sma','co-dir','co-ret','oc-dir','oc-ret'], False, 'J:/LanahanMain/code_projects/quant_sim/quant_sim/reporting/records/'+self.id+'record.csv')
        self.add_metric(MA(id='50sma',val=0.0,window=50,func="env['SPY'].c"))

    def process_data(self, env,  *args, **kwargs):
        sid = self.sid
        eod0 = env.get(sid,0)
        eod1 = env.get(sid,1)
        shares = math.floor(self.order_mngr.active_pos['all']['bal'] / eod0.c)
        if eod0.d.month == 9 and eod0.dow == 1 and 1 < eod0.d.day < 9:
            #self.record({'c':eod0.c, '50sma':self.metrics['50sma'], 'co-dir':1 if eod0.o > eod1.c else 0, 'co-ret':eod0.o / eod1.c - 1.0,'oc-dir':1 if eod0.c > eod0.o else 0, 'oc-ret':eod0.c / eod0.o - 1.0})
            self.order(sid, shares , eod0.o)
        elif eod0.d.month == 9 and eod0.dow == 4 and self.order_mngr.active_pos['all']['n'] > 0:
            self.order(sid, -self.order_mngr.active_pos[sid]['shares'], eod0.c)

class Alg_006(Algorithm):
    def initialize(self, *args, **kwargs):
        self.sid = kwargs.get('sid', 'SPY')
        self.id = 'Labor Day Mon.o - Fri.c Before (%s)'%self.sid
        self.desc = 'Buy $10,000 %s at the Open, the Monday before Labor Day<br>Sell at the Close, the Friday before Labor Day' % self.sid
        self.ignore_old = False
        #self.helper = create_lambda('lambda env, metrics:', helper)
        #self.initialize_recorder(['c','50sma','co-dir','co-ret','oc-dir','oc-ret'], False, 'J:/LanahanMain/code_projects/quant_sim/quant_sim/reporting/records/'+self.id+'record.csv')
        self.add_metric(MA(id='50sma',val=0.0,window=50,func="env['SPY'].c"))

    def process_data(self, env,  *args, **kwargs):
        sid = self.sid
        eod0 = env.get(sid,0)
        eod1 = env.get(sid,1)
        shares = math.floor(self.order_mngr.active_pos['all']['bal'] / eod0.c)
        if eod0.d.month == 8 and eod0.dow == 0 and eod0.d.day > 24:
            #self.record({'c':eod0.c, '50sma':self.metrics['50sma'], 'co-dir':1 if eod0.o > eod1.c else 0, 'co-ret':eod0.o / eod1.c - 1.0,'oc-dir':1 if eod0.c > eod0.o else 0, 'oc-ret':eod0.c / eod0.o - 1.0})
            self.order(sid, shares , eod0.o)
        elif eod0.next.d.month == 9 and eod0.next.dow == 1 and eod0.dow == 4 and self.order_mngr.active_pos['all']['n'] > 0:
            self.order(sid, -self.order_mngr.active_pos[sid]['shares'], eod0.c)

class Alg_007(Algorithm):
    def initialize(self, *args, **kwargs):
        self.sid = kwargs.get('sid', 'SPY')
        self.id = 'Labor Day Thur.c - Fri.c Before (%s)'%self.sid
        self.desc = 'Buy $10,000 %s at the Close, the Thursday before Labor Day<br>Sell at the Close, the Friday before Labor Day' % self.sid
        self.ignore_old = False
        #self.helper = create_lambda('lambda env, metrics:', helper)
        #self.initialize_recorder(['c','50sma','co-dir','co-ret','oc-dir','oc-ret'], False, 'J:/LanahanMain/code_projects/quant_sim/quant_sim/reporting/records/'+self.id+'record.csv')
        self.add_metric(MA(id='50sma',val=0.0,window=50,func="env['SPY'].c"))

    def process_data(self, env,  *args, **kwargs):
        sid = self.sid
        eod0 = env.get(sid,0)
        eod1 = env.get(sid,1)
        shares = math.floor(self.order_mngr.active_pos['all']['bal'] / eod0.c)
        if eod0.next.d.month == 8 and eod0.next.next.dow == 1 and eod0.dow == 3:
            #self.record({'c':eod0.c, '50sma':self.metrics['50sma'], 'co-dir':1 if eod0.o > eod1.c else 0, 'co-ret':eod0.o / eod1.c - 1.0,'oc-dir':1 if eod0.c > eod0.o else 0, 'oc-ret':eod0.c / eod0.o - 1.0})
            self.order(sid, shares , eod0.o)
        elif eod0.next.d.month == 9 and eod0.next.dow == 1 and eod0.dow == 4 and self.order_mngr.active_pos['all']['n'] > 0:
            self.order(sid, -self.order_mngr.active_pos[sid]['shares'], eod0.c)

class Alg_008(Algorithm):
    def initialize(self, *args, **kwargs):
        self.sid = kwargs.get('sid', 'SPY')
        self.id = '1% Gap Down (%s)'%self.sid
        self.desc = 'Buy $10,000 %s at the Open, when %s Gaps down >= %1<br>Sell at the Close' % (self.sid, self.sid)
        self.ignore_old = False

    def process_data(self, env,  *args, **kwargs):
        sid = self.sid
        eod0 = env.get(sid,0)
        eod1 = env.get(sid,1)
        shares = math.floor(self.order_mngr.active_pos['all']['bal'] / eod0.o)
        if eod0.o / eod1.c - 1.0 > 0.01:
            self.order(sid, shares , eod0.o)
            self.order(sid, -shares , eod0.c)

class Alg_009(Algorithm):
    def initialize(self, x, *args, **kwargs):
        self.x = x
        self.sid = kwargs.get('sid', 'SPY')
        self.id = '3x Lower H-L-C (%s, x=%d' % (self.sid, self.x)
        self.desc = 'Buy $10,000 %s at the Close, when market has made a lower H, L and C for the 3rd day in a row<br>Sell at the Close %d days later' % (self.sid, x)
        self.ignore_old = False
        self.add_metric(CountIf(cache_n=3, id='lh-ll-lc',val=0.0,window=5,func="env['SPY'].c < env.get('SPY',1).c and env['SPY'].h < env.get('SPY',1).h and env['SPY'].l < env.get('SPY',1).l"))
        #self.helper = create_lambda('lambda env, metrics:', helper)
        #self.initialize_recorder(['c','50sma','co-dir','co-ret','oc-dir','oc-ret'], False, 'J:/LanahanMain/code_projects/quant_sim/quant_sim/reporting/records/'+self.id+'record.csv')
        #self.add_metric(MA(id='50sma',val=0.0,window=50,func="env['SPY'].c"))

    def process_data(self, env,  *args, **kwargs):
        sid = self.sid
        eod0 = env.get(sid,0)
        eod1 = env.get(sid,1)
        metric = self.metrics['lh-ll-lc']
        shares = math.floor(self.order_mngr.active_pos['all']['bal'] / eod0.o)
        if metric >= 3 and eod0.dow == 0 and self.order_mngr.active_pos['all']['n'] == 0:
            self.order(sid, 10 , eod0.c)
        if self.order_mngr.active_pos['all']['n'] > 0:
            for pid,pos in self.order_mngr.active_pos[sid]['positions'].items():
                if (env.now_dt - pos.open_dt).days >= self.x:
                    self.order(sid, -10 , eod0.c)

class Alg_010(Algorithm):
    def initialize(self, x, *args, **kwargs):
        self.x = x
        self.sid = kwargs.get('sid', 'SPY')
        self.id = '3x Lower H-L-C (%s, x=%d)' % (self.sid, self.x)
        self.desc = 'Buy $10,000 %s at the Close, when market has made a lower H, L and C for the 3rd day in a row<br>Sell at the Close %d days later' % (self.sid, x)
        self.ignore_old = False
        self.add_metric(MA(id='sma10',val=0.0,window=10,func="env['SPY'].c"))
        self.add_metric(MA(id='sma20',val=0.0,window=20,func="env['SPY'].c"))
        self.add_metric(MA(id='sma50',val=0.0,window=50,func="env['SPY'].c"))
        self.add_metric(MA(id='sma200',val=0.0,window=200,func="env['SPY'].c"))
        self.pod = OrderedDict()
        #self.helper = create_lambda('lambda env, metrics:', helper)
        #self.initialize_recorder(['c','50sma','co-dir','co-ret','oc-dir','oc-ret'], False, 'J:/LanahanMain/code_projects/quant_sim/quant_sim/reporting/records/'+self.id+'record.csv')
        #self.add_metric(MA(id='50sma',val=0.0,window=50,func="env['SPY'].c"))

    def process_data(self, env,  *args, **kwargs):
        sid = self.sid
        eod0 = env.get(sid,0)
        eod1 = env.get(sid,1)
        nod = state_of_market(self.pod, eod0, eod1)
        nod['sma10'] = 1 if eod0.c > self.metrics['sma10'] else 2
        nod['sma20'] = 1 if eod0.c > self.metrics['sma20'] else 2
        nod['sma50'] = 1 if eod0.c > self.metrics['sma50'] else 2
        nod['sma200'] = 1 if eod0.c > self.metrics['sma200'] else 2
        nod['sma10-consec'] = self.pod.get('sma10-consec',0) + 1 if nod['sma10'] == self.pod.get('sma10',0) else 0
        nod['sma20-consec'] = self.pod.get('sma20-consec',0) + 1 if nod['sma20'] == self.pod.get('sma20',0) else 0
        nod['sma50-consec'] = self.pod.get('sma50-consec',0) + 1 if nod['sma50'] == self.pod.get('sma50',0) else 0
        nod['sma200-consec'] = self.pod.get('sma200-consec',0) + 1 if nod['sma200'] == self.pod.get('sma200',0) else 0
        shares = math.floor(self.order_mngr.active_pos['all']['bal'] / eod0.o)
        if nod['HH'] == 2 and nod['HL'] == 2 and self.pod['sma10'] == 2 and nod['sma10'] == 1 and nod['sma200'] == 1:
            self.order(sid, 10 , eod0.c)
        if self.order_mngr.active_pos['all']['n'] > 0:
            for pid,pos in self.order_mngr.active_pos[sid]['positions'].items():
                if (env.now_dt - pos.open_dt).days >= self.x:
                    self.order(sid, -10 , eod0.c)
        self.pod = nod