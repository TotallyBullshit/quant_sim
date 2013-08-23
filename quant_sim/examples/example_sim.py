import datetime as dt
from quant_sim.simulator import Simulator
from quant_sim.sources.yeod_source import YEOD_Source
from quant_sim.examples.example_algo import Alg_001, Alg_002, Alg_003, Alg_004, Alg_005, Alg_006
from quant_sim.reporting.report_library import CSV_Master_Report,CSV_ByStrat, Cheetah_Report

# Define Constants
start_dt = dt.datetime(1993,2,1)
end_dt = dt.datetime(2013,8,1)
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
              Alg_002(sid='SPY'),
              Alg_002(sid='^GSPC'),
              Alg_003(sid='SPY'),
              Alg_003(sid='^GSPC'),
              Alg_004(sid='SPY'),
              Alg_004(sid='^GSPC'),
              Alg_005(sid='SPY'),
              Alg_005(sid='^GSPC'),
              Alg_006(sid='SPY'),
              Alg_006(sid='^GSPC')
              ])

# Run simulation
sim.run()


# Recursively (BFS) Generate Reports for all accounts
csv_rep = CSV_Master_Report(sim.algos, report_dir=REPORT_DIR)
csv_strat = CSV_ByStrat(sim.algos, report_dir=REPORT_DIR)
ch_rep = Cheetah_Report(sim.algos,report_dir=REPORT_DIR)

# Output reports
csv_rep.write('report.csv')
csv_strat.write('report.csv')
ch_rep.write(temp_fn='J:/LanahanMain/code_projects/quant_sim/quant_sim/reporting/templates/ctemplate.tmpl')
#ch_rep.write(temp_fn='J:/LanahanMain/code_projects/quant/quant/reporting/templates/blog_temp.tmpl', fn='blog_rep.html')
