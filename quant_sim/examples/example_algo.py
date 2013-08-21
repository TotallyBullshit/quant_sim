
from quant_sim.finances.algorithm import Algorithm
from quant_sim.math.metric_library import MA

class Alg_001(Algorithm):
    def initialize(self):
        self.id = 'test'
        self.desc = 'test algorithm for rare set ups'
        self.ignore_old = False
        self.initialize_recorder(['avg-ret','OB','c','ma','c>o'], False, 'J:/LanahanMain/code_projects/quant_sim/quant_sim/reporting/records/'+self.id+'record.csv')
        self.add_metric(MA(id='sma',val=0.0,window=10,func="env['SPY'].c"))

    def process_data(self, env):
        sid = '^GSPC'
        eod0 = env.get(sid,0)
        eod1 = env.get(sid,1)
        self.record({'ma':self.metrics['sma'],'OB':eod0.h > eod1.h and eod0.l < eod1.l, 'c':eod0.c, 'c>o':eod0.c>eod0.o})
        if eod0.d.month == 3 and eod0.nth_dow == 2 and eod0.dow == 4:
            self.order(sid, 20, eod0.c)
            print eod0,'buy',self.order_mngr.active_pos[sid]['shares'],self.order_mngr.active_pos['all']['bal'],self.order_mngr.active_pos['all']['float_bal'],'=',self.stats_mngr.stats['all']['n'],self.stats_mngr.stats['all']['win_perc']
        elif eod0.d.month == 3 and eod0.next.nth_dow == 3 and eod0.next.dow == 4:
            self.order(sid, -20, eod0.c)
            print eod0,'sell',self.order_mngr.active_pos[sid]['shares'],self.order_mngr.active_pos['all']['bal'],self.order_mngr.active_pos['all']['float_bal'],'=',self.stats_mngr.stats['all']['n'],self.stats_mngr.stats['all']['win_perc']
        elif eod0.d.month == 3 and eod0.d.day > 27 and self.order_mngr.active_pos[sid]['n'] > 0:
            self.order(sid, -20, eod0.c)
            print eod0,'sell',self.order_mngr.active_pos[sid]['shares'],self.order_mngr.active_pos['all']['bal'],self.order_mngr.active_pos['all']['float_bal'],'=',self.stats_mngr.stats['all']['n'],self.stats_mngr.stats['all']['win_perc']