import datetime as dt

class EOD_Data(object):
    def __init__(self,sid,d,o,h,l,c,v,ac,div,split,prev=None):
        self.sid = sid
        self.d = dt.datetime.strptime(d,'%Y-%m-%d')
        self.nth_dow = ((self.d.day - 1) / 7 + 1)
        self.nth_tdom = 0
        if prev != None:
            self.nth_tdom = 1 if self.d.month != prev.d.month else prev.nth_tdom + 1
        else:
            self.nth_tdom = 0
        self.dow = self.d.weekday()
        self.o = float(o)
        self.h = float(h)
        self.l = float(l)
        self.c = float(c)
        self.v = int(v)
        self.n = 0 if prev == None else prev.n+1
        self.oldest_d = self.d if prev == None else prev.oldest_d
        self.ac = float(ac)
        self.div = div
        self.split = split
        self.prev = prev
        self.wo = self.o if self.prev == None or self.prev.d.strftime('%W') != self.d.strftime('%W') else self.prev.wo
        self.wh = self.h if self.prev == None or self.prev.d.strftime('%W') != self.d.strftime('%W') else max(self.prev.wh, self.h)
        self.wl = self.l if self.prev == None or self.prev.d.strftime('%W') != self.d.strftime('%W') else min(self.prev.wl, self.l)
        self.wc = self.c
        self.mo = self.o if self.prev == None or self.prev.d.month != self.d.month else self.prev.mo
        self.mh = self.h if self.prev == None or self.prev.d.month != self.d.month else max(self.prev.mh, self.h)
        self.ml = self.l if self.prev == None or self.prev.d.month != self.d.month else min(self.prev.ml, self.l)
        self.mc = self.c
        self.yo = self.o if self.prev == None or self.prev.d.year != self.d.year else self.prev.yo
        self.yh = self.h if self.prev == None or self.prev.d.year != self.d.year else max(self.prev.yh, self.h)
        self.yl = self.l if self.prev == None or self.prev.d.year != self.d.year else min(self.prev.yl, self.l)
        self.yc = self.c
        self.next = None
        self.metrics = {}
        self.pats = {}
        # self.atr = max(self.atr,abs(self.h-self.prev.c),abs(self.l-self.prev.l)) 

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        elif attr in self.metrics:
            return self.metrics[attr]
        else:
            raise AttributeError("'%s' not in %s[%s] EOD object"%(attr, self.sid,self.d.strftime('%Y-%m-%d')))

    def __setitem__(self,key,value):
        if type(key) == str and key in self.metrics:
            self.indies[key] = value
        else:
            raise KeyError('%s'%key)

    def __getitem__(self,key):
        # Handles eod['2012-04-15']
        if type(key) == str and key in self.metrics:
            return self.metrics[key]
        elif type(key) == str:
            try: key = dt.datetime.strptime(key,'%Y-%m-%d')
            except ValueError:
                pass

        # Clean up slice input
        if type(key) == slice:
            start, stop = key.start, key.stop
            if type(start) == str: start = dt.datetime.strptime(start,'%Y-%m-%d')
            if type(stop) == str: stop = dt.datetime.strptime(stop,'%Y-%m-%d')
            if start == None and type(stop) == int: start = self.n
            if stop == None and type(start) == int: stop = 0
            if start == None and type(stop) == dt.datetime: start = self.oldest_d
            if stop == None and type(start) == dt.datetime: stop = self.d
            if start == None and stop == None: start, stop = self.n, 0
            if start == stop: return []
        # Handles eod[3]
        if type(key) == int:
            def helper(inc,target):
                for i in range(key): 
                    inc = inc.prev
                    if inc == None:
                        print self.n
                        raise IndexError('%s[%d] not in %s data history'%(self.sid, key, self.source_id))
                return inc
            if key < 0: raise IndexError('Date in future',key)
            elif key > self.n: raise IndexError('%s[%d] not in %s data history'%(self.sid, key, self.source_id))
            return helper(self,key)
        # Handles eod[dt.datetime(2012,4,15)]
        if type(key) == dt.datetime:
            def helper(inc,target):
                while inc.d > target:
                    inc = inc.prev
                if inc.d < target: raise IndexError('Date not in history',key)
                else: return inc
            if key > self.d: raise IndexError('Date in future',key)
            elif key < self.oldest_d: raise IndexError('Date not in history',key)
            else: return helper(self,key)
        # Handles eod[dt.datetime(2012,4,15): dt.datetime(2012,5,10)] and  eod[dt.datetime(2012,5,10): dt.datetime(2012,4,15]
        if type(key) == slice and type(stop) == dt.datetime and type(start) == dt.datetime:
            def helper(inc,start,stop):
                result = []
                if start < stop:
                    while inc.d >= start:
                        if inc.d < stop: result += [inc]
                        inc = inc.prev
                if start > stop:
                    while inc.d > stop:
                        if inc.d <= start: result += [inc]
                        inc = inc.prev
                if start < stop: result.reverse()
                return result
            if start > self.d: raise IndexError('Date in future',start)
            elif stop > self.d: raise IndexError('Date in future',stop)
            elif start < self.oldest_d: raise IndexError('Date not in history',start)
            elif stop < self.oldest_d: raise IndexError('Date not in history',stop)
            else: return helper(self,start,stop)
        # Handles eod[dt.datetime(2012,4,15):4]
        if type(key) == slice and type(stop) == int and type(start) == dt.datetime:
            def helper(inc,target):
                while inc.d > target:
                    inc = inc.prev
                if inc.d < target: return inc.next
                else: return inc           
            if start > self.d: raise IndexError('Date in future',start)
            elif start < self.oldest_d: raise IndexError('Date not in history',start)
            start = self.n - helper(self,start).n
            stop = start - stop
        # Handles eod[4:dt.datetime(2012,4,15)]
        elif type(key) == slice and type(stop) == dt.datetime and type(start) == int:
            def helper(inc,target):
                while inc.d > target:
                    inc = inc.prev
                return inc 
            if stop > self.d: raise IndexError('Date in future',stop)
            elif stop < self.oldest_d: raise IndexError('Date not in history',stop)
            stop = self.n - helper(self,stop).n
            start = stop + start
        # Handles eod[1:4] and eod[4:1]
        if type(key) == slice and type(stop) == int and type(start) == int:
            def helper(inc,start,stop):
                result = []
                if start < stop:
                    while inc.n >= start:
                        if inc.n < stop: result += [inc]
                        inc = inc.prev
                if start > stop:
                    while inc.n > stop:
                        if inc.n <= start: result += [inc]
                        inc = inc.prev
                if start < stop: result.reverse()
                return result
            if start < 0 or stop < 0: raise IndexError('Date in future',min(start,stop))
            elif start > self.n: raise IndexError('Date not in history',start)
            elif stop > self.n: raise IndexError('Date not in history',stop)
            else: return helper(self,self.n-start,self.n-stop)

    def __repr__(self):
        return '%s,%s,%2.2f,%2.2f,%2.2f,%2.2f'%(self.sid,self.d.strftime('%Y-%m-%d'),self.o,self.h,self.l,self.c)