


class Auto_Exit(object):
    def __init__(self, *args, **kwargs):
        self.func = kwargs.get('func',None)
        self.price = kwargs.get('price', None)
        self.offset = kwargs.get('offset', 1)
        self.initialize(*args, **kwargs)

    def initialize(self, *args, **kwargs):
        pass

    def get_exit_price(self,trade, env):
        if self.price == None:
            return env[trade.sid].c
        elif callable(self.price):
            return self.price(env)
        else:
            return self.price

    def test(self, trade, env):
        #if (env[trade.sid].now_int - trade.open_bar.n) >= self.offset:
        return self.check_exit(trade, env)
        #else:
        #    return False

    def check_exit(self, trade, env):
        if self.func(trade, env):
            return self.get_exit_price(trade, env)
        else:
            return False


class Time_Exact(Auto_Exit):
    def initialize(self, time=1, *args, **kwargs):
        self.time = time

    def check_exit(self, trade, env):
        if (env.now_int - env.calendar.index(trade.open_dt)) >= self.time:
            return self.get_exit_price(trade, env)
        else:
            return False

class Time_Loose(Auto_Exit):
    def initialize(self, time=1, *args, **kwargs):
        self.time = time

    def check_exit(self, trade, env):
        eod = env[trade.sid]
        if (env.now_int - env.calendar.index(trade.open_dt)) >= self.time or \
            ((eod.c / trade.open_p - 1.0) * (trade.shares / abs(trade.shares))) > 0.0:
            return self.get_exit_price(trade, env)
        else:
            return False


class Price(Auto_Exit):
    def initialize(self, *args, **kwargs):
        self.target = kwargs.get('target', 1)

    def check_exit(self, trade, env):
        eod = env['eod'][trade.sid]
        if eod.h >= self.target and eod.l <= self.target:
            return self.get_exit_price(trade, env)
        else:
            return False
