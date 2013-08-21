import urllib
import re
import datetime as dt
import quant.sources.data_source as ds
from quant.utils import date_utils as dtools

class News_Data(object):
    def __init__(self,id,date,summary,start,end,network,reporters,anchors,title,desc,brtype,segtype):
        self.id = id
        self.date = date
        self.summary = summary
        self.start = start
        self.end = end
        self.network = network
        self.reporters = reporters
        self.anchors = anchors
        self.title = title
        self.desc = desc
        self.brtype = brtype
        self.segtype = segtype
        self.next = None
        self.prev = None
    def __repr__(self):
        out = [str(self.id)]
        out += ['None' if self.date == None else self.date.strftime('%Y-%m-%d')]
        out += ['None' if self.start == None else self.start.strftime('%H:%M:%S')]
        out += ['None' if self.end == None else self.end.strftime('%H:%M:%S')]
        out += ['None' if self.network == None else self.network]
        out += ['None' if self.brtype == None else self.brtype]
        out += ['None' if self.segtype == None else self.segtype]
        out += ['None' if self.title == None else self.title]
        out += ['None' if self.desc == None else self.desc]
        out += ['None' if self.reporters == None else self.reporters]
        out += ['None' if self.anchors == None else self.anchors]
        out += ['None' if self.summary == None else self.summary]
        return '(;:;)'.join(out)
        

class News_Source(ds.Data_Source):
    def finalize(self,start,stop):
        self.data = self.data_dict.get(start)
        self.now = start
        
    def next(self):
        return None
    
    def get(self,id):
        
        def get_date(news):
            date_m = re.search('<input type="hidden" name="getmonth" value="(\d\d\d\d-\d\d-\d\d)" />',news)
            if date_m != None:
                return dt.datetime.strptime(date_m.groups()[0],'%Y-%m-%d')
            date_m = re.search('<tr><th>Date:</th><td><strong>(.*)</strong>',news)
            if date_m != None:
                return dt.datetime.strptime(date_m.groups()[0],'%b %d, %Y')
            day_m = re.search('<input type="hidden" name="getdate" value="(.*)" />',news)
            month_m = re.search('<input type="hidden" name="getmonth" value="(.*)" />',news)
            year_m = re.search('<input type="hidden" name="getyear" value="(.*)" />',news)
            if day_m != None:
                return dt.datetime(int(year_m.groups()[0]),int(month_m.groups()[0]),int(day_m.groups()[0]))
            else: return None
            
        def get_summary(news):
            summary_m = re.search('<tr><th>Summary:</th><td>(.*)</td></tr>',news)
            if summary_m == None: return None
            return summary_m.groups()[0]
        
        def get_time(news):
            time_m = re.search('<tr><th>Program Time:</th><td>(.*)m.',news)
            if time_m == None: return None,None
            start = re.search('(\d\d:\d\d:\d\d&nbsp;[a|p]m -)',time_m.groups()[0])
            end = re.search('(\d\d:\d\d:\d\d&nbsp;[a|p]m.)',time_m.groups()[0])
            try: 
                start = dt.datetime.strptime(start.groups()[0],'%I:%M:%S&nbsp;%p -')
                end = dt.datetime.strptime(end.groups()[0],'%I:%M:%S&nbsp;%p ')
            except: 
                try:
                    start = dt.datetime.strptime(start.groups()[0],'%H:%M:%S&nbsp;%p -')
                    end = dt.datetime.strptime(end.groups()[0],'%H:%M:%S&nbsp;%p ')
                except:
                    return None,None
            return start,end
        
        def get_network(news):
            ntw_m = re.search('<input type="hidden" name="Network" value="(.*)"',news)
            if ntw_m != None:
                return ntw_m.groups()[0]
            ntw_m = re.search('<tr><th>Network:</th><td>(.*)</td></tr>',news)
            if ntw_m != None:
                return ntw_m.groups()[0]
            else: return None

        def get_reporters(news):
            reps_m = re.search('<tr><th>Reporters:</th><td>(.*)</td></tr>',news)
            if reps_m != None:
                return reps_m.groups()[0]
            else: return None
            
        def get_anchors(news):
            anc_m = re.search('<tr><th>Anchors: </th><td>(.*)</td></tr>',news)
            if anc_m != None:
                return anc_m.groups()[0]
            else: return None          

        def get_title(news):
            title_m = re.search('<title>(.*)</title>',news)
            if title_m != None:
                return title_m.groups()[0]
            else: return None            

        def get_desc(news):
            desc_m = re.search('<meta name="description" content="(.*)"',news)
            if desc_m != None:
                return desc_m.groups()[0]
            else: return None              

        def get_brtype(news):
            brtype_m = re.search('<tr><th>Broadcast Type:</th><td><strong>(.*)</strong>',news)
            if brtype_m != None:
                return brtype_m.groups()[0]
            else: return None

        def get_segtype(news):
            segtype_m = re.search('<span class="label"> Segment Type: </span> <strong>(.*)</strong>',news)
            if segtype_m != None:
                return segtype_m.groups()[0]
            else: return None
            
        url_str = 'http://tvnews.vanderbilt.edu/program.pl?ID=%d'%(id)
        try: news_file = urllib.urlopen(url_str)
        except:
            raise IOError('Failed load on: %d'%(id))           
        news_raw = news_file.read()
        date = get_date(news_raw)
        summary = get_summary(news_raw)
        start,end = get_time(news_raw)
        network = get_network(news_raw)
        reporters = get_reporters(news_raw)
        anchors = get_anchors(news_raw)
        title = get_title(news_raw)
        desc = get_desc(news_raw)
        brtype = get_brtype(news_raw)
        segtype = get_segtype(news_raw)
        news_obj = News_Data(id,date,summary,start,end,network,reporters,anchors,title,desc,brtype,segtype)
        if news_obj.date != None:
            f = open('%s/news_%d_%02d.txt'%(self.source_dir,news_obj.date.year,news_obj.date.month),'a')
            f.write(str(news_obj)+'\n')
            f.close()
	
    def update(self):
        raise NotImplementedError
        
    def load(self,start_d,end_d):
        news_dict = {}
        for date in dtools.daterange(start_d,end_d,resolution='M'):
            f = open('%s/news_%d_%02d.txt'%(self.source_dir,date.year,date.month),'r')
            for line in f:
                id,date,start,end,network,brtype,segtype,title,desc,reporters,anchors,summary = line.rstrip().split('(;:;)')
                date = dt.datetime.strptime(date,'%Y-%m-%d')
                if start_d > date or date > end_d: continue
                news_obj = News_Data(id,date,summary,dt.datetime.strptime(start,'%H:%M:%S'),dt.datetime.strptime(end,'%H:%M:%S'),network,reporters,anchors,title,desc,brtype,segtype)
                if date not in news_dict: news_dict[date] = []
                else:
                    news_dict[date] += [news_obj]
        return news_dict
        
if __name__ == '__main__':
    n = News_Source('C:/Python27/Lib/site-packages/quant/data/news_data','news')
    # latest = 1037101
    for id in range(50000,00000,-1):
        print id
        n.get(id)
    
    #s = dt.datetime(2012,12,20)
    #e = dt.datetime(2013,1,10)
    #t = dt.datetime(2012,12,25)
    #news_dict = n.load(s,e)
    #print news_dict[t][1].network
    #print news_dict[t][4].network