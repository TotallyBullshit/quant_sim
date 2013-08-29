import datetime as dt
from collections import OrderedDict

from quant_sim.errors import Date_Not_In_History_Error, SID_Error

class Environment(object):
    """
    Simulator for backtesting

    Parameters
    ---------- 
    start_dt : dt.datetime, required
    end_dt : dt.datetime, optional, default now
    calendar : str (data_source.id) or iterable, optioanl, default 'eod'
               this determines the dates to run the simulation on.
               If a type(str) is used it should exist as a data_source.
               It will use the dates that exist for the data_source.
               
    Returns
    -------
    n/a
    
    See Also
    --------
    n/a

    Notes
    -----
    n/a
    
    Examples
    --------
    n/a

    """
    def __init__(self, *args, **kwargs):
        self.data = OrderedDict()
        self.calendar = []
        self.now_dt = None
        self.now_int = 0
        
    def set_calendar(self, calendar):
        self.calendar = calendar
    
    def add_data(self, sid, data):
        """
        adds data to environment
        
        Parameters
        ---------- 
        sid : string, required
            key to be used in self.data
        data : OrderedDict, required
            data = OrderedDict([(dt.datetime(2013,3,15), 23.5), dt.datetime(2013,3,16), 24.23)])
            
        Returns
        -------
        sets self.data[sid] = data
        
        See Also
        --------
        n/a
    
        Notes
        -----
        all data must be an OrderedDict keyed by dt.datetime
        There is no specification for the value at each dt.datetime key.
        Each sid in the environment must be unique or else it will override previous data
        
        Examples
        --------
        n/a
    
        """
        self.data[sid] = data
        
    def update(self, now):
        self.now_dt = now
        if now not in self.calendar:
            self.calendar += [now]
        self.now_int = self.calendar.index(now)

    def raise_error(self, error, msg, default):
        if default == 'nan':
            raise error(msg)
        else:
            return default

    def get(self, sid, left, right=None, default='nan'):
        if sid not in self.data:
            self.raise_error(SID_Error, "'%s' not in data"%(sid), default)
        # Handles left='2012-04-15'
        if type(left) == str:
            left = dt.datetime.strptime(left, '%Y-%m-%d')
        if type(right) == str:
            right = dt.datetime.strptime(right, '%Y-%m-%d')
        # Handles left = 3
        if type(left) == int and right == None:
            left = self.now_int - left
            if left < 0: 
                self.raise_error(Date_Not_In_History_Error, "'[%s]' index not in %s data"%(left, sid), default)
            left = self.calendar[left]
        # Handles left=dt.datetime(2012,4,15)
        if type(left) == dt.datetime and right == None:
            if left not in self.data[sid]:
                self.raise_error(Date_Not_In_History_Error, "'%s' not in %s data"%(left, sid), default)
            elif left > self.now_dt:
                self.raise_error(Date_Not_In_History_Error, "'%s' is in the future"%(left), default)
            else:
                return self.data[sid][left]
        # Handles left=5, right=3
        if type(left) == int and type(right) == int:
            left = self.now_int - left
            right = self.now_int - right
        # Handles left=dt.datetime(2012,4,15), right=3
        if type(left) == dt.datetime and type(right) == int:
            left = self.calendar.index(left)
            right = left + right
        # Handles left=3, right=dt.datetime(2012,4,15)
        if type(left) == int and type(right) == dt.datetime:
            right = self.calendar.index(right)
            left = right - left
        # Handles left=dt.datetime(2012,4,15), right=dt.datetime(2012,5,15)
        if type(left) == dt.datetime and type(right) == dt.datetime:
            left = self.calendar.index(left)
            right = self.calendar.index(right)
        # Handles left=5, right=3
        if type(left) == int and type(right) == int:
            if left > self.now_int or right > self.now_int:
                raise Date_Not_In_History_Error("'%s' is in the future"%(self.calendar[max(left,right)]))
            elif left < 0 or right < 0:
                raise Date_Not_In_History_Error("'%s' not in %s data"%(min(left,right), sid))
            if left > right:
                dates = self.calendar[left:right-1:-1]
                return [self.data[sid].get(d,None) for d in dates]
            if left < right:
                dates = self.calendar[left:right+1]
                return [self.data[sid].get(d,None) for d in dates]
            
    def __getitem__(self, key):
            if key in self.data and self.now_dt in self.data[key]:
                return self.data[key][self.now_dt]
            elif key in self.data and self.now_dt not in self.data[key]:
                raise Date_Not_In_History_Error("'%s' not in %s data"%(self.now_dt.strftime('%Y-%m-%d'), key))
            else:
                raise SID_Error("'%s' not in data"%(key))
            
if __name__ == '__main__':
    from quant_sim.sources.yeod_source import YEOD_Source
    DATA = 'J:/LanahanMain/code_projects/data'
    data_source = YEOD_Source(DATA+'/eod_data/')
    env= Environment()
    env.set_calendar(data_source.load('SPY').keys())
    env.add_data('SPY', data_source.load('SPY'))
    env.update(dt.datetime(2013,8,9))
    print 0,env['SPY']
    print 1,env.get('SPY',1)
    print 2,env.get('SPY',2)
    print 3,env.get('SPY',3)
    print 4,env.get('SPY',4)
    print 5,env.get('SPY',5)
    print env.get('SPY','2013-08-01','2013-07-29')
    env.data['SPY'].pop(dt.datetime(2013,6,19))
    print env.get('SPY','2013-06-17','2013-06-21')
    