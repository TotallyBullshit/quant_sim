from collections import OrderedDict
from copy import deepcopy

from quant_sim.tools.helpers import create_lambda

class Position(object):
    def __init__(self, sid, shares, price, open_dt, **kwargs):
        self.sid = sid
        self.open_dt = open_dt
        self.open_s = shares
        self.open_p = price
        self.min_p = self.open_p
        self.max_p = self.open_p
        self.last_p = self.open_p
        self.open_bal = None
        self.close_dt = None
        self.close_p = None
        self.close_s = None
        self.age = 0
        self.exit_cond = kwargs.get('exit_cond',[])
        self.exit = kwargs.get('exit',None)

    def close(self, d, shares, price, **kwargs):
        self.close_dt = d
        self.open_s = -shares
        self.close_s = shares
        self.close_p = price
        self.theo_ret = (self.open_s / abs(self.open_s)) * (self.close_p / self.open_p - 1.0)
        pnl = (self.close_p - self.open_p if self.open_s > 0 else self.open_p - self.close_p)
        self.real_ret = (abs(self.open_s) * pnl) / self.open_bal

    def auto_exit(self, env):
        """
        will return a price to auto_exit if there is valid exit
        """
        if self.exit != None: 
            return self.exit.test(self, env)
        else: 
            return False

    def update(self,env):
        self.max_p = max(self.max_p, env[self.sid].h)
        self.min_p = min(self.min_p, env[self.sid].l)
        self.last_p = env[self.sid].c
        self.age = (env.now_dt - self.open_dt).days

    def __eq__(self,other):
        if (self.open_dt == other.open_dt and self.close_dt == other.close_dt
            and self.open_p == other.open_p and self.close_p == other.close_p
            and self.open_s == other.open_s):
            return True
        else:
            return False

    def __repr__(self):
        if self.close_dt == None:
            return 'OPEN: %s,%d,%2.2f : %2.2f' % (
                                           self.open_dt.strftime('%Y-%m-%d'),
                                           self.open_s,
                                           self.open_p,
                                           self.last_p
                                                )
        else:
            return 'CLOSED: %s,%d,%2.2f : %2.2f : %s,%d,%2.2f = %2.4f' % (
                                           self.open_dt.strftime('%Y-%m-%d'),
                                           self.open_s,
                                           self.open_p,
                                           self.last_p,
                                           self.close_dt.strftime('%Y-%m-%d'),
                                           self.close_s,
                                           self.close_p,
                                           self.theo_ret
                                                )

def FIFO(sid, shares, price, active_trades):
    resulting_orders = []
    for pid, pos in active_trades[sid]['positions'].items():
        if shares < 0 and pos.open_s > 0 and abs(pos.open_s) >= abs(shares):
            resulting_orders += [(sid, pid, shares)]
            shares = 0
        elif shares > 0 and pos.open_s < 0 and abs(pos.open_s) >= abs(shares):
            resulting_orders += [(sid, pid, shares)]
            shares = 0
        elif shares > 0 and pos.open_s < 0 and abs(pos.open_s) < abs(shares):
            resulting_orders += [(sid, pid, -pos.open_s)]
            shares -= -pos.open_s
        elif shares < 0 and pos.open_s > 0 and abs(pos.open_s) < abs(shares):
            shares += pos.open_s
            resulting_orders += [(sid, pid, -pos.open_s)]
        if shares == 0:
            return resulting_orders
    if abs(shares) > 0:
        resulting_orders += [(sid, 'new', shares)]
    return resulting_orders

class Order_Manager(object):
    def __init__(self, *args, **kwargs):
        self.active_pos = OrderedDict()
        self.closed_pos = []
        self.now_dt = None
        self.cost_basis = FIFO
        self.commission = lambda sid,shares,price:max(shares*0.005,1.0)
        self.last_pid = 0
        self.initialize_position('all')
        self.active_pos['all']['bal'] = 10000

    def initialize_position(self, sid):
        if sid not in self.active_pos:
            self.active_pos[sid] = {}
            self.active_pos[sid]['n'] = 0
            self.active_pos[sid]['shares'] = 0
            self.active_pos[sid]['basis'] = 0.0
            self.active_pos[sid]['bal'] = 0.0
            self.active_pos[sid]['float_bal'] = 0.0
            self.active_pos[sid]['positions'] = OrderedDict()

    def update(self, env):
        # executed at beginning before algorithm is executed
        self.now_dt = env.now_dt
        self.active_pos['all']['float_bal'] = 0.0
        for sid, data in self.active_pos.items():
            self.active_pos[sid]['float_bal'] = 0.0
            for pid, pos in data['positions'].items():
                pos.update(env)
                self.active_pos[sid]['float_bal'] += abs(pos.open_s * pos.open_p) + (pos.open_s * (pos.last_p - pos.open_p))
                self.active_pos['all']['float_bal'] += abs(pos.open_s * pos.open_p) + (pos.open_s * (pos.last_p - pos.open_p))
                exit_p = self.check_exit_cond(pos, env)
                #exit_p = pos.auto_exit(env)
                if exit_p != False:
                    self.order(pos.sid, -pos.open_s, exit_p)

    def check_exit_cond(self, p, env):
        for e in p.exit_cond:
            cond, price =e[0], e[1]
            cond = create_lambda('p, eod, env', cond)
            price = create_lambda('eod, env', price)
            if cond(p, env[p.sid], env):
                return price(env[p.sid], env)
        return False

    def update_pos_stats(self, sid, shares, price, mod_n):
        self.active_pos[sid]['n'] += mod_n
        if self.active_pos[sid]['shares'] + shares == 0:
            self.active_pos[sid]['basis'] = 0.0
        else:
            self.active_pos[sid]['basis'] = ((self.active_pos[sid]['shares'] * self.active_pos[sid]['basis']) + (shares * price)) / (self.active_pos[sid]['shares'] + shares)
        self.active_pos[sid]['shares'] += shares

    def logic_order(self, rule, sid='any', shares=0, price=0):
        if rule == 'close_all':
            for sid,data in self.active_pos.items():
                for pid, pos in data['positions'].items():
                        self.order(sid, -pos.open_s, pos.last_p)
        elif rule == 'open_all':
            pass

    def order(self, sid, shares, price, **kwargs):
        self.initialize_position(sid)
        resulting_orders = self.cost_basis(sid, shares, price, self.active_pos)
        for sid, pid, resulting_shares in resulting_orders:
            if pid not in self.active_pos[sid]['positions']:
                self.open_order(sid, shares, price, **kwargs)
            elif abs(self.active_pos[sid]['positions'][pid].open_s) == abs(resulting_shares):
                self.close_order(sid, pid, resulting_shares, price)
            elif abs(self.active_pos[sid]['positions'][pid].open_s) > abs(resulting_shares):
                self.close_order(sid, pid, resulting_shares, price)

    def open_order(self, sid, shares, price, **kwargs):
        new_pid = self.last_pid + 1
        self.last_pid += 1
        self.active_pos[sid]['positions'][new_pid] = Position(sid, shares, price, self.now_dt, **kwargs)
        self.active_pos[sid]['positions'][new_pid].open_bal = self.active_pos['all']['bal']
        # change position stats
        self.update_pos_stats(sid, shares, price, 1)
        self.update_pos_stats('all', shares, price, 1)
        self.active_pos[sid]['bal'] -= abs(shares * price)
        self.active_pos[sid]['float_bal'] += abs(shares * price)
        self.active_pos['all']['bal'] -= abs(shares * price)
        self.active_pos['all']['float_bal'] += abs(shares * price)

    def close_order(self, sid, pid, shares, price):
        # all shares are closed
        if abs(self.active_pos[sid]['positions'][pid].open_s) == abs(shares):
            self.closed_pos += [self.active_pos[sid]['positions'].pop(pid)]
            self.closed_pos[-1].close(self.now_dt, shares, price)
        # shares are left over
        elif abs(self.active_pos[sid]['positions'][pid].open_s) > abs(shares):
            self.closed_pos += [deepcopy(self.active_pos[sid]['positions'][pid])]
            self.closed_pos[-1].close(self.now_dt, shares, price)
            self.active_pos[sid]['positions'][pid].open_s += shares
        # change position stats
        self.update_pos_stats(sid, shares, self.closed_pos[-1].open_p, -1)
        self.update_pos_stats('all', shares, self.closed_pos[-1].open_p, -1)
        self.active_pos[sid]['bal'] += (abs(shares * self.closed_pos[-1].open_p) + (-shares * (price - self.closed_pos[-1].open_p)))
        self.active_pos[sid]['float_bal'] -= abs(shares * self.closed_pos[-1].open_p) + (-shares * (price - self.closed_pos[-1].open_p))
        self.active_pos['all']['bal'] += abs(shares * self.closed_pos[-1].open_p) + (-shares * (price - self.closed_pos[-1].open_p))
        self.active_pos['all']['float_bal'] -= abs(shares * self.closed_pos[-1].open_p) + (-shares * (price - self.closed_pos[-1].open_p))


if __name__ == '__main__':
    order_mngr = Order_Manager()
    order_mngr.order('SPY', 10, 159.3)
    order_mngr.order('SPY', -10, 165.25)
