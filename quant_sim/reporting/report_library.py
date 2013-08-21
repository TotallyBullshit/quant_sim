
from quant_sim.reporting.report import Report
from Cheetah.Template import Template
from quant_sim.reporting.graphs import simple_plot

class CSV_Master_Report(Report):
    def write(self, fn='report.csv'):
        header = 'algo,'
        for filter_key, stats_dict in self.algos[0].stats_mngr.calcs.items():
            for stat_key, stat_obj in stats_dict.items():
                header += '%s:%s,'%(filter_key,stat_key)
        out = ''
        for algo in self.algos:
            out += '%s,'%(algo.id)
            for filter_key, stats_dict in algo.stats_mngr.calcs.items():
                for stat_key, stat_obj in stats_dict.items():
                    out += '%s,'%(stat_obj)
            out += '\n'
        f = open(self.report_dir+fn, 'w')
        f.write(header+'\n'+out)
        f.close()
        
class Cheetah_Report(Report):
    def write(self, temp_fn, fn='creport.html',):
        plot = simple_plot
        f = open(self.report_dir+fn, 'w')
        f.close()
        f = open(self.report_dir+fn, 'a')
        for algo in self.algos:
            temp = Template(file=temp_fn, searchList=[algo.stats_mngr.calcs, algo.__dict__, locals(), self.__dict__])
            f.write(str(temp))
        f.close()

class CSV_ByStrat(Report):
    def write(self, fn='report.csv'):
        header = list(self.algos[0].stats_mngr.calcs['all'].iterkeys())
        header.sort()
        for algo in self.algos:
            out = ''
            for filter_key, stats_dict in algo.stats_mngr.calcs.items():
                out += '%s,'%(filter_key)
                for stat_key in header:
                    if stat_key in algo.stats_mngr.calcs[filter_key]:
                        out += '%s,'%(algo.stats_mngr.calcs[filter_key][stat_key])
                    else:
                        out += ','
                out += '\n'
            f = open(self.report_dir+algo.id+'_'+fn, 'w')
            f.write('FilterID,'+','.join(header)+'\n'+out)
            f.close()