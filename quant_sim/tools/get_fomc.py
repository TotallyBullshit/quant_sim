
import urllib
import re
import datetime as dt

def get_date(html):
    date = re.findall('<th class="year" colspan="2"><span class="left">(.*) Meeting</span>',html)
    return date
    
def parse_date(date, year):
    def get_dt(d, year):
        month, day = d.split(' ')
        date_dt = dt.datetime.strptime(month, '%B')
        return dt.datetime(year, date_dt.month, int(day))        
    
    month_span = date.split(' - ')
    day_span = date.split('-')
    if len(month_span) > 1:
        return [get_dt(month_span[0], year), get_dt(month_span[1], year)] 
    elif len(day_span) > 1:
        if len(day_span[1]) > 2:
            return [get_dt(day_span[0], year), get_dt(day_span[1], year)] 
        else:
            d = get_dt(day_span[0], year)
            return [get_dt(day_span[0], year), dt.datetime(year, d.month, int(day_span[1]))] 
    else:
        return [get_dt(date, year), None]

result = []
for year in range(1936,2008):
    url_str = 'http://www.federalreserve.gov/monetarypolicy/fomchistorical%d.htm'%(year)
    try: html_file = urllib.urlopen(url_str)
    except:
        raise IOError('Failed load on: %d'%(id))           
    html_raw = html_file.read()
    date = get_date(html_raw)
    parsed = [parse_date(d, year) for d in date]
    #print '\n'.join([str(p) for p in parsed])
    for p in parsed:
        if p[1] != None:
            result += p
        else:
            result += [p[0]]

f = open('fomc.txt','w')
for r in result:
    f.write('%s\n'%(r.strftime('%Y-%m-%d')))
    
f.close()