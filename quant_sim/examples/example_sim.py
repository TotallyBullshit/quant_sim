import datetime as dt
from quant_sim.simulator import Simulator
from quant_sim.sources.yeod_source import YEOD_Source
from quant_sim.examples.example_algo import *
from quant_sim.reporting.report_library import CSV_Master_Report,CSV_ByStrat, Cheetah_Report

# Define Constants
start_dt = dt.datetime(1993,2,1)
end_dt = dt.datetime(2013,9,6)
balance = 10000
DATA = '/mnt/share2/LanahanMain/code_projects/data'
DATA = 'J:/LanahanMain/code_projects/data'
REPORT_DIR = 'J:/LanahanMain/code_projects/quant_sim/quant_sim/reporting/reports/'

# Define Data Sources
data_source = YEOD_Source(DATA+'/eod_data/')

# Initialize Simulation
sim = Simulator(start_dt, end_dt)

# Add Data
sim.add_data(('SPY', data_source.load('SPY')))
sim.add_data(('IBM', data_source.load('IBM')))
sim.add_data(('^GSPC', data_source.load('^GSPC')))

# Initialize calendar to simulate one
sim.set_calendar(data_source.load('SPY').keys())

# Add algorithms to simulate
sim.add_algo([
              #Alg_008(x=1,sid='SPY'),
              #Alg_008(x=2,sid='SPY'),
              #Alg_008(x=3,sid='SPY'),
              #Alg_008(x=4,sid='SPY'),
              #Alg_008(x=5,sid='SPY'),
              #Alg_008(x=6,sid='SPY'),
              #Alg_002(sid='SPY'),
              #Alg_003(sid='SPY'),
              #Alg_003(sid='^GSPC'),
              #Alg_004(sid='SPY'),
              #Alg_004(sid='^GSPC'),
              #Alg_005(sid='SPY'),
              #Alg_005(sid='^GSPC'),
              #Alg_006(sid='SPY'),
              #Alg_006(sid='^GSPC'),
              #Alg_007(sid='^GSPC'),
              #Alg_010(x=0, sid='SPY'),
              #Alg_010(x=1, sid='SPY'),
              #Alg_010(x=2, sid='SPY'),
              #Alg_010(x=3, sid='SPY'),
              #Alg_010(x=4, sid='SPY')
              MarketState(sid='SPY')
              ])

# Run simulation
sim.run()


# Recursively (BFS) Generate Reports for all accounts
#csv_rep = CSV_Master_Report(sim.algos, report_dir=REPORT_DIR)
#csv_strat = CSV_ByStrat(sim.algos, report_dir=REPORT_DIR)
#ch_rep = Cheetah_Report(sim.algos,report_dir=REPORT_DIR)
#
## Output reports
#keys = ['all:roi','all:roi_ann','all:prof_fact','all:max_dd','all:n','all:win_perc','all:mean_theo','winners:mean_theo','all:max_theo','losers:mean_theo','all:min_theo']
#csv_rep.write(keys=keys,fn='report_master.csv')
#csv_strat.write(fn='report_bystrat.csv')
#ch_rep.write(temp_fn='J:/LanahanMain/code_projects/quant_sim/quant_sim/reporting/templates/blog_report.tmpl')
###ch_rep.write(temp_fn='J:/LanahanMain/code_projects/quant/quant/reporting/templates/blog_temp.tmpl', fn='blog_rep.html')
