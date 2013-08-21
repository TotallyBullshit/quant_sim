

import re
import urllib
import datetime as dt
from copy import copy
from collections import OrderedDict
from stock_eod import EOD_Data

class YEOD_Source(object):
    def __init__(self, source_dir):
        self.source_dir = source_dir

    def get(self,sids):
        def get_eod(sid):
            now = dt.datetime.now()
            starty, startm, startd = '1950', '01', '01'
            endy, endm, endd = now.year, now.month, now.day
            url_str = 'http://ichart.finance.yahoo.com/table.csv?s=%s&a=%s&b=%s&c=%s&d=%02d&e=%02d&f=%d&g=d&ignore=.csv'%(sid,startm,startd,starty,endm,endd,endy)
            eod_raw = urllib.urlopen(url_str)
            lines = eod_raw.readlines()
            eod_raw.close()
            if not lines or len(lines)<1: return None
            if lines[0][0] == "<": 
                print "Error loading Yahoo / Cannot find %s"%(sid)
                return None
            f = open('%s%s_eod.csv'%(self.source_dir,sid),"w")
            lines.reverse()
            for line in lines[:-1]:
                f.write(line)
            f.close()

        def get_div(sid):
            now = dt.datetime.now()
            starty, startm, startd = '1950', '01', '01'
            endy, endm, endd = now.year, now.month, now.day
            url_str = 'http://ichart.finance.yahoo.com/table.csv?s=%s&a=%s&b=%s&c=%s&d=%02d&e=%02d&f=%d&g=v&ignore=.csv'%(sid,startm,startd,starty,endm,endd,endy)
            div_raw = urllib.urlopen(url_str)
            lines = div_raw.readlines()
            div_raw.close()
            if (not lines) or (len(lines) < 1): return 0
            if lines[0][0] == "<": return ""
            f = open('%s%s_div.csv'%(self.source_dir,sid),"w")
            lines.reverse()
            for line in lines[:-1]:
                f.write(line)
            f.close()

        def get_split(sid):
            url_str = 'http://getsplithistory.com/'+sid
            f = urllib.urlopen(url_str)
            splits_raw = f.read()
            f.close()
            splitpat = re.compile('<tr class="([0-9][0-9]?[0-9]?\.?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?)">')
            datepat = re.compile('<td>([A-z][a-z][a-z] [0-9][0-9], [0-9][0-9][0-9][0-9])</td>')
            splits = splitpat.findall(splits_raw)
            dates = datepat.findall(splits_raw)
            if len(dates) > 0:
                dates = [dt.datetime.strptime(d,'%b %d, %Y') for d in dates]
            f = open('%s%s_split.csv'%(self.source_dir,sid),"w")
            for i,v in enumerate(splits[0:-1]):
                f.write('%s,%s\n'%(dates[i].strftime('%Y-%m-%d'),v))
            f.close()
        get_eod(sid)
        get_div(sid)
        #get_split(sid)


    def load(self,sid):
        def load_div(sid):
            f = open('%s%s_div.csv'%(self.source_dir,sid),"r")
            div_dict = {}
            for line in f:
                d,amt = line.rstrip().split(',')
                div_dict[dt.datetime.strptime(d,'%Y-%m-%d')] = float(amt)
            f.close()
            return div_dict

        def load_split(sid):
            f = open('%s%s_split.csv'%(self.source_dir,sid),"r")
            split_dict = {}
            for line in f:
                d,amt = line.rstrip().split(',')
                split_dict[dt.datetime.strptime(d,'%Y-%m-%d')] = float(amt)
            f.close()
            return split_dict

        def load_eod(eod_dict,sid,div_dict,split_dict):
            f = open('%s%s_eod.csv'%(self.source_dir,sid),"r")
            prev_eod = None
            for line in f:
                d,o,h,l,c,v,ac = line.rstrip().split(',')
                now = dt.datetime.strptime(d,'%Y-%m-%d')
                eod_obj = EOD_Data(sid,d,o,h,l,c,v,ac,div_dict.get(now),split_dict.get(now),prev_eod)
                if prev_eod != None: prev_eod.next = eod_obj
                prev_eod = eod_obj
                if now not in eod_dict:
                    eod_dict[now] = {}
                eod_dict[now] = eod_obj
            f.close()
            return eod_dict

        eod_dict = OrderedDict()
        div_dict = {}
        split_dict = {}
        try: div_dict = load_div(sid)
        except: pass
        try: split_dict = load_split(sid)
        except: pass
        return load_eod(eod_dict,sid,div_dict,split_dict)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 4 or (sys.argv[2] not in ['get','load']):
        print 'Usage: python yeod_source.py dir [get|load] [sid]+'
        print 'Example: python yeod_source.py J:/LanahanMain/code_projects/data get SPY DIA'
        sys.exit()
    sids = sys.argv[3:]
    action = sys.argv[2]
    data_dir = sys.argv[1]
    yeod_source = YEOD_Source(data_dir+'/eod_data/')
    if action == 'get':
        for sid in sids:
            print 'Updating %s' % (sid)
            yeod_source.get(sid)
    elif action == 'load':
        print 'Loading:',sids[0]
        data = yeod_source.load(sids[0]).keys()
        print 'Starts:',data[0]
        print 'Ends:',data[-1]



