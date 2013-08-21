from quant_sim.tools.helpers import create_lambda

class Metric(object):
    """
    Metric object to create indicators on sids and other
    calculations used in the trade algorithm heuristics.

    Can be used by inheriting from Metric as below and overriding
    initialize and process_data.

    Parameters
    ---------- 
    id : string, required
         needs to be unique to sid otherwise 
    val : any_type, default None, optional
    window : int, default 0, optional
             This is how long a value is tracked for
    func : function, default None, optional
           used as a helper method to extract values from env
           and transform them to fit the users needs to pass back
           into metric.process_data.
           This allows the user flexibility in designing a single metric,
           but being able to use it for a vast range of tasks
           For example
           Avg(id='avg',func=lambda env: env['eod']['SPY'].c)
               maintains average of closing price
           Avg(id='avg',func=lambda env: env['eod']['SPY'].c / 
                                         env['eod']['SPY'].o + random())
               maintains average of a complex user defined calculation
               so the user does not have to create an entirely new metric 
               
    Returns
    -------
    n/a
    
    See Also
    --------
    n/a

    Notes
    -----
    API vars:
        self.popped : the last value removed from history
        x : the newest calculated value inserted in history
    
    Examples
    --------

    class MA(Metric):
        def initialize(self, *args, **kwargs):
            self.sum = 0.0

        def process_data(self, x):
            self.sum += (x - self.get_history(self.window - 1))
            return self.sum / float(min(self.n, self.window))

    """
    def __init__(self, id, *args, **kwargs):
        self.id = id
        self.val = kwargs.get('val',None)
        self.window = kwargs.get('window',0)
        self.func = create_lambda('env',kwargs.get('func',None))
        self._temp = self.val
        self.history = []
        self.n = 0
        self.popped = 0.0
        self.reqs = None
        self.cache_n = kwargs.get('cache_n',0)
        self.ignore_old = kwargs.get('ignore_old',True)
        self.cache = []
        self.initialize(*args, **kwargs)

    def initialize(self, *args, **kwargs):
        pass

    def update(self, env):
        try:
            x = env
            if self.func(env) != None:
                x = self.func(env)
        except:
            if self.ignore_old:
                return
            else:
                raise
        self.n += 1
        # newest val goes at beginning of list to make get_history
        # work easier when accessing the oldest value
        # see metric_library.MA and self.get_history
        if self.window > 0:
            self.history.insert(0, x)
        if self.window > 0 and self.n > self.window:
            self.popped = self.history.pop(self.window)
        val = self.process_data(x if self.func != None else env)
        if self.window > 0 and self.n >= self.window:
            self.val = val
        elif self.window >  0 and self.n < self.window:
            self._temp = val
        else:
            self.val = val
        if self.cache_n > 0:
            self.cache.insert(0,val)
        if self.n > self.cache_n and self.cache_n > 0:
            self.cache.pop()
        return val

    def get_history(self,index, default=0.0):
        """
        This implements a safe list.get method like dict.get
        it allows the user to easily code metrics without worrying about
        two use cases when self.n < self.window and self.n >= self.window
        this allows for fewer lines of code and cleaner code

        there are many ways around multiple use cases but this seems to be
        easiest. 

        The three primary ways of handling it are:

        # 2 lines and relatively easy to read and understand
        class MA(Metric):
            def process_data(self, x):
                self.sum += (x - self.get_history(self.window - 1))
                return self.sum / float(min(self.n, self.window))

        # 2 lines but in-line if-else is confusing and hard to read
        class MA(Metric):
            def process_data(self, x):
                self.sum += (x - (self.history[-1] if self.n >= self.window else 0))
                return self.sum / float(min(self.n, self.window)) 

        # 5 lines, clean easy to understand
        class MA(Metric):
            def process_data(self, x):
                if self.n >= self.window:
                    self.sum += (x - self.history[-1])
                else:
                    self.sum += x
                return self.sum / float(min(self.n, self.window))
        """
        try:
            return self.history[index]
        except IndexError:
            return default

    def process_data(self, x):
        pass

    def __repr__(self):
        if type(self.val) == str: return '%s'%(self.val)
        elif type(self.val) == int: return '%d'%(self.val)
        elif type(self.val) == float: return '%2.4f'%(self.val)
        else: return str(self.val)
