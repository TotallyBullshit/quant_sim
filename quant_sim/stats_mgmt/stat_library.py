
import math

from quant_sim.stats_mgmt.stat import Stat

class N(Stat):
    def process_data(self, env, stats, fk, trade):
        return self.val + 1.0
    def __repr__(self):
        return '%d'%(self.val)

class Mean(Stat):
    def initialize(self, *args, **kwargs):
        self.sum = 0.0
        self.func = kwargs.get('func', None)

    def process_data(self, env, stats, fk, trade):
        self.sum += self.func(trade)
        return self.sum / float(self.n)

    def __repr__(self):
        return '%2.5f' % (self.val)

class Mean_Tr_Dur(Stat):
    def initialize(self, *args, **kwargs):
        self.sum = 0.0

    def process_data(self, env, stats, fk, trade):
        self.sum += (trade.close_dt - trade.open_dt).days
        return self.sum / float(self.n)

class Mean_Btw_Tr(Stat):
    def initialize(self, *args, **kwargs):
        self.sum = 0.0
        self.last_trade_dt = None

    def process_data(self, env, stats, fk, trade):
        if self.last_trade_dt == None:
            self.last_trade_dt = trade.open_dt
        self.sum += (trade.open_dt - self.last_trade_dt).days
        self.last_trade_dt = trade.close_dt
        return self.sum / float(self.n)

class Stdev(Stat):
    def initialize(self, *args, **kwargs):
        self.sum_x = 0.0
        self.sum_x2 = 0.0
        self.func = kwargs.get('func', None)

    def process_data(self, env, stats, fk, trade):
        self.sum_x += self.func(trade)
        self.sum_x2 += (self.func(trade) * self.func(trade))
        mean = self.sum_x / self.n
        return math.sqrt((self.sum_x2 / self.n) - (mean * mean))

class Max(Stat):
    def initialize(self, *args, **kwargs):
        self.func = kwargs.get('func', None)

    def process_data(self, env, stats, fk, trade):
        return max(self.val, self.func(trade))

class Min(Stat):
    def initialize(self, *args, **kwargs):
        self.func = kwargs.get('func', None)

    def process_data(self, env, stats, fk, trade):
        return min(self.val, self.func(trade))

class Win_Perc(Stat):
    def initialize(self, *args, **kwargs):
        self.up_n = 0.0

    def process_data(self, env, stats, fk, trade):
        if trade.theo_ret > 0.0: self.up_n += 1.0
        return self.up_n / float(self.n)

class Profit_Fact(Stat):
    def initialize(self, *args, **kwargs):
        self.up_n = 0.0
        self.theo_up_sum = 0.0
        self.theo_dn_sum = 0.0

    def process_data(self, env, stats, fk, trade):
        if trade.theo_ret > 0.0: 
                self.up_n += 1.0
                self.theo_up_sum += trade.theo_ret
        else:
            self.theo_dn_sum += trade.theo_ret
        win_perc = self.up_n / float(self.n)
        if win_perc == 1.0 or self.theo_dn_sum == 0.0: 
            return 'inf'
        return ((win_perc * (self.theo_up_sum / self.n)) / 
                 -((1.0 - win_perc) * (self.theo_dn_sum / self.n)))

class Max_DD(Stat):
    def initialize(self, *args, **kwargs):
        self.max_roi = 0.0
        self.roi = 1.0
        self.dd_n = 0
        self.max_dd_n = 0
        self.local_dd = 1.0
        self.dd_list = []

    def process_data(self, env, stats, fk, trade):
        self.roi *= (1.0 + trade.theo_ret)
        if max(self.max_roi, self.roi) != self.roi:
            self.dd_n += 1
        elif self.dd_n > 0:
            self.dd_list += [{'end_dt': env.now_dt, 'dur': self.dd_n, 'dd': min(self.local_dd, self.roi / self.max_roi - 1.0)}]
            self.dd_n = 0
            self.local_dd = 0.0
        self.max_roi = max(self.max_roi, self.roi)
        self.local_dd =  min(self.local_dd, self.roi / self.max_roi - 1.0)
        val =  min(self.val, self.roi / self.max_roi - 1.0)
        return val
    
class Max_NRow(Stat):
    def initialize(self, *args, **kwargs):
        self.temp_val = 0.0
        self.func = kwargs.get('func',None)

    def process_data(self, env, stats, fk, trade):
        if self.func(trade):
            self.temp_val += 1
        else:
            self.temp_val = 0
        return max(self.val, self.temp_val)

class ROI(Stat):
    def process_data(self, env, stats, fk, trade):
        return self.val * (1.0 + trade.theo_ret)

class Date(Stat):
    def initialize(self, *args, **kwargs):
        self.func = kwargs.get('func',lambda a, b: a)
        self.on_bar = True

    def process_data(self, env, stats, fk, trade):
        return self.func(self.val if self.val != None else env.now_dt, env.now_dt)

class Years(Stat):
    def initialize(self, *args, **kwargs):
        self.reqs = ['start_dt', 'end_dt']
        self.on_bar = True
        
    def process_data(self, env, stats, fk, trade):
        return (stats['all']['end_dt'] - stats['all']['start_dt']).days / 365.25

class Generic(Stat):
    def initialize(self, *args, **kwargs):
        self.func = kwargs.get('func', lambda a: a)
        self.ignore_e = kwargs.get('ignore_e',True)
        
    def process_data(self, env, stats, fk, trade):
        try:
            val = self.func(env, stats, fk, trade)
        except:
            if self.ignore_e:
                val = self.val
                pass
            else:
                raise
        return val
    
all_stats = [N(id='n',val=0),
             Mean(id='mean_theo',val=0.0,func=lambda t: t.theo_ret),
             Stdev(id='stdev_theo',val=0.0,func=lambda t: t.theo_ret),
             Max(id='max_theo',val=0.0,func=lambda t: t.theo_ret),
             Min(id='min_theo',val=0.0,func=lambda t: t.theo_ret),
             Win_Perc(id='win_perc',val=0.0),
             Profit_Fact(id='prof_fact',val=0.0),
             Max_DD(id='max_dd',val=0.0),
             Max_NRow(id='max_nup',val=0.0, func=lambda t: t.theo_ret > 0.0),
             Max_NRow(id='max_ndn',val=0.0, func=lambda t: t.theo_ret < 0.0),
             ROI(id='roi',val=1.0),
             Mean_Btw_Tr(id='mean_btw_tr',val=0.0),
             Mean_Tr_Dur(id='mean_tr_dur',val=0.0),
             Date(id='start_dt',func=min),
             Date(id='end_dt',on_bar=True,func=max),
             Generic(id='years', reqs=['start_dt', 'end_dt'], on_bar=True, func=lambda e, s, *args: (s['all']['end_dt'] - s['all']['start_dt']).days / 365.25),
             Generic(id='trades/yr', val=0.0, reqs=['years', 'n'], on_bar=True, func=lambda e, s, fk, t: s[fk]['n'] / s[fk]['years']),
             Generic(id='roi_ann', val=0.0, reqs=['roi', 'years'], func=lambda e, s, fk, t: s[fk]['roi'] ** (1.0 / s[fk]['years'])),
             Generic(id='stdev_ann', val=0.0, reqs=['trades/yr', 'stdev_theo'], func=lambda e, s, fk, t: s[fk]['stdev_theo'] * (s[fk]['trades/yr'] ** 0.5)),
             Generic(id='clamar_ratio', val=0.0, reqs=['roi_ann', 'max_dd'], func=lambda e, s, fk, t: s[fk]['roi_ann'] / -s[fk]['max_dd']),
             Generic(id='sharpe_ratio', val=0.0, reqs=['mean_theo', 'stdev_theo', 'mean_tr_dur'], func=lambda e, s, fk, t: (s[fk]['mean_theo'] - ((0.0186 ** 1 / 252.0))*s[fk]['mean_tr_dur'])/ s[fk]['stdev_theo']),
             ]

# self.avg_runup = np.array([t.run_up for t in self.trades]).mean()
# self.avg_rundn = np.array([t.run_dn for t in self.trades]).mean()
# self.abs_mean = abs(self.mean)
# self.abs_mean_age = self.abs_mean / float(self.avg_age)
# self.log_mon_cum_ret = np.log(self.mon_cum_ret)
# self.gradient, self.intercept, self.r_value, self.p_value, self.std_err = ss.linregress(np.arange(len(self.mon_returns)),self.log_mon_cum_ret)
# self.k_ratio = self.gradient / (len(self.mon_returns) * self.std_err)
# self.non_cmp_roi = sum(self.returns)
# self.ann_ret = (self.roi**(365.0/ float((self.edate - self.sdate).days))) - 1.0
# #self.ann_ret = ((self.roi**self.tr_a_yr) ** (1.0/self.ntrades)) - 1.0
# self.sharpe = self.ann_ret / self.ann_std
# try:self.sortino = self.ann_ret / (self.dn_std*(self.tr_a_yr ** 0.5))
# self.max_dd = self.dd_list[-1].dd
# self.max_dd_sdate = self.dd_list[-1].sdate
# self.max_dd_edate = self.dd_list[-1].edate
# self.max_dd_tr = self.dd_list[-1].num_tr
# self.dd_bl_hf_dd = sum([x.dd > (self.max_dd/2.0) for x in self.dd_list])
# self.avg_dd_days = np.mean(self.avg_dd_days)
# self.max_nloss,self.max_nwins = self.find_max_lw()
# self.norm_boe = boe_norm_dist(self.returns,self.mean,self.std,self.ntrades)
# #self.norm_shapiro_w,self.norm_shapiro_p = ss.shapiro(self.returns)
# #self.norm_ad_t,scrap1,scrap2 = ss.anderson(self.returns,dist='norm')
# self.binom_p = round(ss.binom_test(max(self.up,self.dn),self.ntrades,0.5),3)
# self.ttest_p = round(ss.ttest_1samp([1]*self.up+[0]*(self.ntrades-self.up),[0.5])[1],3)
# self.chisq_p = round(ss.chisquare([self.up,self.ntrades-self.up])[1],3)
# self.var95 = self.mean - (1.96 * self.std)
# self.var99 = self.mean - (2.58 * self.std)
