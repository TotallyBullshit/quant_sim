
import datetime as dt

class Stat(object):
    """
    Stat object to create statistics on closed trade events
    
    Can be used by inheriting from Stat as below and overriding
    initialize and process_data.
    
    class N(Stat):
        def initialize(self):
            self.id = 'n'
            self.val = 0
            
        def process_data(self, env, trade):
            self.val += 1
            
    or the stat generator can be used as below.
    
    @stat(id='n', val=0)
    def N(self, env, trade):
        self.val += 1
    
    """
    def __init__(self, *args, **kwargs):
        self.val = kwargs.get('val',None)
        self.temp = self.val
        self.on_trade = kwargs.get('on_trade',True)
        self.on_bar = kwargs.get('on_bar',False)
        self.id = kwargs.get('id',None)
        self.history = []
        self.window = kwargs.get('window',0)
        self.reqs = kwargs.get('reqs',set([]))
        if type(self.reqs) != set:
            self.reqs = set(self.reqs)
        self.n = 0
        self.calculate_val = kwargs.get('process_data',None)
        self.initialize(*args, **kwargs)

    def initialize(self, *args, **kwargs):
        pass

    def update(self, env, stats, fk='all', trade=None):
        self.n += 1
        if self.calculate_val == None:
            val = self.process_data(env, stats, fk, trade)
        else:
            val = self.calculate_val(self, env, trade)
        if self.window > 0 and self.n >= self.window:
            self.val = val
            self.history.pop(0)
            self.history.append(val)
        elif self.window > 0:
            self.temp = val
            self.history.append(val)
        else:
            self.val = val
    
    def process_data(self, env, stats, fk='all', trade=None):
        pass

    def __repr__(self):
        if type(self.val) == str: return '%s'%(self.val)
        elif type(self.val) == int: return '%d'%(self.val)
        elif type(self.val) == float: return '%2.4f'%(self.val)
        elif type(self.val) == dt.datetime: return '%s'%(self.val.strftime('%Y-%m-%d'))
        else: return str(self.val)

def stat(*dargs, **dkwargs):
    """Decorator function to use instead of inheriting from Stat.
    For an example on how to use this, see the doc string of Stat.
    """
    def create_stat(func):
        def calculate_val(self, *args, **kwargs):
            # passes the user defined function to Stat which it
            # will call instead of self.get_value()
            return func(self, *args, **kwargs)
        s = Stat(*dargs, process_data = calculate_val, **dkwargs)
        return s
    return create_stat

if __name__ == '__main__':
    
    @stat(id='n', val=0)
    def N(self,env,trade):
        return self.val + 1
    new = N
    print new.val
    new.update(None,None)
    print new.val
    new.update(None,None)
    print new.val
    print new.id

    class N(Stat):
        def process_data(self, env, trade):
            return self.val + 1
            
    new = N(id='n',val=0)
    print new.val
    new.update(None,None)
    print new.val
    new.update(None,None)
    print new.val
    print new.id
