import math

from quant_sim.tools.helpers import create_lambda
from quant_sim.finances.algorithm import Algorithm
from quant_sim.math.metric_library import MA

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
        self.id = 'labor_fri-c_tues-o'
        self.desc = 'Labor Day'
        self.ignore_old = False
        self.sid = kwargs.get('sid', 'SPY')
        self.id += self.sid
        #self.helper = create_lambda('lambda env, metrics:', helper)
        self.initialize_recorder(['c','50sma','co-dir','co-ret','oc-dir','oc-ret'], False, 'J:/LanahanMain/code_projects/quant_sim/quant_sim/reporting/records/'+self.id+'record.csv')
        self.add_metric(MA(id='50sma',val=0.0,window=50,func="env['SPY'].c"))

    def process_data(self, env,  *args, **kwargs):
        sid = self.sid
        eod0 = env.get(sid,0)
        eod1 = env.get(sid,1)
        shares = math.floor(self.order_mngr.active_pos['all']['bal'] / eod0.c)
        if eod0.next.d.month == 9 and eod0.next.dow == 1 and eod0.dow == 4:
            self.record({'c':eod0.c, '50sma':self.metrics['50sma'], 'co-dir':1 if eod0.o > eod1.c else 0, 'co-ret':eod0.o / eod1.c - 1.0,'oc-dir':1 if eod0.c > eod0.o else 0, 'oc-ret':eod0.c / eod0.o - 1.0})
            self.order(sid, shares , eod0.c)
        elif eod0.d.month == 9 and eod0.dow == 1 and 1 < eod0.d.day < 9:
            self.order(sid, -self.order_mngr.active_pos[sid]['shares'], eod0.o)

class Alg_003(Algorithm):
    def initialize(self, *args, **kwargs):
        self.id = 'labor_fri-o_fri-c'
        self.desc = 'Labor Day'
        self.ignore_old = False
        self.sid = kwargs.get('sid', 'SPY')
        self.id += self.sid
        #self.helper = create_lambda('lambda env, metrics:', helper)
        self.initialize_recorder(['c','50sma','co-dir','co-ret','oc-dir','oc-ret'], False, 'J:/LanahanMain/code_projects/quant_sim/quant_sim/reporting/records/'+self.id+'record.csv')
        self.add_metric(MA(id='50sma',val=0.0,window=50,func="env['SPY'].c"))

    def process_data(self, env,  *args, **kwargs):
        sid = self.sid
        eod0 = env.get(sid,0)
        eod1 = env.get(sid,1)
        shares = math.floor(self.order_mngr.active_pos['all']['bal'] / eod0.c)
        if eod0.next.d.month == 9 and eod0.next.dow == 1 and eod0.dow == 4:
            self.record({'c':eod0.c, '50sma':self.metrics['50sma'], 'co-dir':1 if eod0.o > eod1.c else 0, 'co-ret':eod0.o / eod1.c - 1.0,'oc-dir':1 if eod0.c > eod0.o else 0, 'oc-ret':eod0.c / eod0.o - 1.0})
            self.order(sid, shares , eod0.o)
        #elif eod0.d.month == 9 and eod0.dow == 1 and 1 < eod0.d.day < 9:
            self.order(sid, -self.order_mngr.active_pos[sid]['shares'], eod0.c)
            
class Alg_004(Algorithm):
    def initialize(self, *args, **kwargs):
        self.id = 'labor_tues-o_tues-c'
        self.desc = 'Labor Day'
        self.sid = kwargs.get('sid', 'SPY')
        self.id += self.sid
        self.ignore_old = False
        #self.helper = create_lambda('lambda env, metrics:', helper)
        self.initialize_recorder(['c','50sma','co-dir','co-ret','oc-dir','oc-ret'], False, 'J:/LanahanMain/code_projects/quant_sim/quant_sim/reporting/records/'+self.id+'record.csv')
        self.add_metric(MA(id='50sma',val=0.0,window=50,func="env['SPY'].c"))

    def process_data(self, env,  *args, **kwargs):
        sid = self.sid
        eod0 = env.get(sid,0)
        eod1 = env.get(sid,1)
        shares = math.floor(self.order_mngr.active_pos['all']['bal'] / eod0.c)
        if eod0.d.month == 9 and eod0.dow == 1 and 1 < eod0.d.day < 9:
            self.record({'c':eod0.c, '50sma':self.metrics['50sma'], 'co-dir':1 if eod0.o > eod1.c else 0, 'co-ret':eod0.o / eod1.c - 1.0,'oc-dir':1 if eod0.c > eod0.o else 0, 'oc-ret':eod0.c / eod0.o - 1.0})
            self.order(sid, shares , eod0.o)
        #elif eod0.d.month == 9 and eod0.dow == 1 and 1 < eod0.d.day < 9:
            self.order(sid, -self.order_mngr.active_pos[sid]['shares'], eod0.c)

class Alg_005(Algorithm):
    def initialize(self, *args, **kwargs):
        self.id = 'labor_tues-o_fri-c'
        self.desc = 'Labor Day'
        self.sid = kwargs.get('sid', 'SPY')
        self.id += self.sid
        self.ignore_old = False
        #self.helper = create_lambda('lambda env, metrics:', helper)
        self.initialize_recorder(['c','50sma','co-dir','co-ret','oc-dir','oc-ret'], False, 'J:/LanahanMain/code_projects/quant_sim/quant_sim/reporting/records/'+self.id+'record.csv')
        self.add_metric(MA(id='50sma',val=0.0,window=50,func="env['SPY'].c"))

    def process_data(self, env,  *args, **kwargs):
        sid = self.sid
        eod0 = env.get(sid,0)
        eod1 = env.get(sid,1)
        shares = math.floor(self.order_mngr.active_pos['all']['bal'] / eod0.c)
        if eod0.d.month == 9 and eod0.dow == 1 and 1 < eod0.d.day < 9:
            self.record({'c':eod0.c, '50sma':self.metrics['50sma'], 'co-dir':1 if eod0.o > eod1.c else 0, 'co-ret':eod0.o / eod1.c - 1.0,'oc-dir':1 if eod0.c > eod0.o else 0, 'oc-ret':eod0.c / eod0.o - 1.0})
            self.order(sid, shares , eod0.o)
        elif eod0.d.month == 9 and eod0.dow == 4 and self.order_mngr.active_pos['all']['n'] > 0:
            self.order(sid, -self.order_mngr.active_pos[sid]['shares'], eod0.c)

class Alg_006(Algorithm):
    def initialize(self, *args, **kwargs):
        self.id = 'labor_mon-o_fri-c'
        self.desc = 'Labor Day'
        self.sid = kwargs.get('sid', 'SPY')
        self.id += self.sid
        self.ignore_old = False
        #self.helper = create_lambda('lambda env, metrics:', helper)
        self.initialize_recorder(['c','50sma','co-dir','co-ret','oc-dir','oc-ret'], False, 'J:/LanahanMain/code_projects/quant_sim/quant_sim/reporting/records/'+self.id+'record.csv')
        self.add_metric(MA(id='50sma',val=0.0,window=50,func="env['SPY'].c"))

    def process_data(self, env,  *args, **kwargs):
        sid = self.sid
        eod0 = env.get(sid,0)
        eod1 = env.get(sid,1)
        shares = math.floor(self.order_mngr.active_pos['all']['bal'] / eod0.c)
        if eod0.d.month == 8 and eod0.dow == 0 and eod0.d.day > 24:
            self.record({'c':eod0.c, '50sma':self.metrics['50sma'], 'co-dir':1 if eod0.o > eod1.c else 0, 'co-ret':eod0.o / eod1.c - 1.0,'oc-dir':1 if eod0.c > eod0.o else 0, 'oc-ret':eod0.c / eod0.o - 1.0})
            self.order(sid, shares , eod0.o)
        elif eod0.next.d.month == 9 and eod0.next.dow == 1 and eod0.dow == 4 and self.order_mngr.active_pos['all']['n'] > 0:
            self.order(sid, -self.order_mngr.active_pos[sid]['shares'], eod0.c)