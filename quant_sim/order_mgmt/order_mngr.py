from collections import OrderedDict
from copy import deepcopy

class Position(object):
    def __init__(self, sid, shares, price, open_dt, **kwargs):
        self.sid = sid
        self.open_dt = open_dt
        self.shares = shares
        self.open_p = price
        self.min_p = self.open_p
        self.max_p = self.open_p
        self.last_p = self.open_p
        self.open_bal = None
        self.close_dt = None
        self.close_p = None
        self.close_s = None
        self.exit = kwargs.get('exit',None)

    def close(self, d, shares, price, **kwargs):
        self.close_dt = d
        self.close_s = shares
        self.close_p = price
        self.theo_ret = (self.close_s / abs(self.close_s)) * (self.close_p / self.open_p - 1.0)
        pnl = (self.close_p - self.open_p if self.close_s > 0 else self.open_p - self.close_p)
        self.real_ret = (abs(self.close_s) * pnl) / self.open_bal

    def auto_exit(self, env):
        """
        will return a price to auto_exit if there is valid exit
        """
        if self.exit != None: 
            return self.exit.test(self, env)
        else: 
            return False

    def update(self,h,l,c):
        self.max_p = max(self.max_p, h)
        self.min_p = min(self.min_p, h)
        self.last_p = c

    def __eq__(self,other):
        if (self.open_dt == other.open_dt and self.close_dt == other.close_dt
            and self.open_p == other.open_p and self.close_p == other.close_p
            and self.shares == other.shares):
            return True
        else:
            return False

    def __repr__(self):
        if self.close_dt == None:
            return 'OPEN: %s,%d,%2.2f : %2.2f' % (
                                           self.open_dt.strftime('%Y-%m-%d'),
                                           self.shares,
                                           self.open_p,
                                           self.last_p
                                                )
        else:
            return 'CLOSED: %s,%d,%2.2f : %2.2f : %s,%d,%2.2f = %2.4f' % (
                                           self.open_dt.strftime('%Y-%m-%d'),
                                           self.shares,
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
        if shares < 0 and pos.shares > 0 and abs(pos.shares) >= abs(shares):
            resulting_orders += [(sid, pid, shares)]
            shares = 0
        elif shares > 0 and pos.shares < 0 and abs(pos.shares) >= abs(shares):
            resulting_orders += [(sid, pid, shares)]
            shares = 0
        elif shares > 0 and pos.shares < 0 and abs(pos.shares) < abs(shares):
            resulting_orders += [(sid, pid, -pos.shares)]
            shares -= -pos.shares
        elif shares < 0 and pos.shares > 0 and abs(pos.shares) < abs(shares):
            shares += pos.shares
            resulting_orders += [(sid, pid, -pos.shares)]
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
        self.now_dt = env.now_dt
        self.active_pos['all']['float_bal'] = 0.0
        for sid, data in self.active_pos.items():
            self.active_pos[sid]['float_bal'] = 0.0
            for pid, pos in data['positions'].items():
                pos.update(env[sid].h, env[sid].l, env[sid].c)
                self.active_pos[sid]['float_bal'] += abs(pos.shares * pos.open_p) + (pos.shares * (pos.last_p - pos.open_p))
                self.active_pos['all']['float_bal'] += abs(pos.shares * pos.open_p) + (pos.shares * (pos.last_p - pos.open_p))

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
                        self.order(sid, -pos.shares, pos.last_p)
        elif rule == 'open_all':
            pass

    def order(self, sid, shares, price):
        self.initialize_position(sid)
        resulting_orders = self.cost_basis(sid, shares, price, self.active_pos)
        for sid, pid, resulting_shares in resulting_orders:
            if pid not in self.active_pos[sid]['positions']:
                self.open_order(sid, shares, price)
            elif abs(self.active_pos[sid]['positions'][pid].shares) == abs(resulting_shares):
                self.close_order(sid, pid, resulting_shares, price)
            elif abs(self.active_pos[sid]['positions'][pid].shares) > abs(resulting_shares):
                self.close_order(sid, pid, resulting_shares, price)

    def open_order(self, sid, shares, price):
        new_pid = self.last_pid + 1
        self.last_pid += 1
        self.active_pos[sid]['positions'][new_pid] = Position(sid, shares, price, self.now_dt)
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
        if abs(self.active_pos[sid]['positions'][pid].shares) == abs(shares):
            self.closed_pos += [self.active_pos[sid]['positions'].pop(pid)]
            self.closed_pos[-1].close(self.now_dt, -shares, price)
        # shares are left over
        elif abs(self.active_pos[sid]['positions'][pid].shares) > abs(shares):
            self.closed_pos += [deepcopy(self.active_pos[sid]['positions'][pid])]
            self.closed_pos[-1].close(self.now_dt, -shares, price)
            self.active_pos[sid]['positions'][pid].shares += shares
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
