#
# Copyright 2013 Quantistician, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime as dt

from quant_sim.finances.environment import Environment

class Simulator(object):
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
    def __init__(self, start_dt, end_dt=dt.datetime.now(), *args, **kwargs):
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.algos = []
        self.calendar = kwargs.get('calendar', 'eod')
        self.env = Environment()

    def add_algo(self, algos):
        if type(algos) != list:
            algos = [algos]
        self.algos += algos

    def add_data(self, data_list):
        if type(data_list) != list:
            data_list = [data_list]
        for data_tuple in data_list:
            sid = data_tuple[0]
            data = data_tuple[1]
            self.env.add_data(sid, data)

    def set_calendar(self, calendar=None):
        """
        method to set the master calendar used in the simulation
        This can be any custom calendar: 
            Set trading days, business days, custom days like FOMC meetings, holidays
    
        Parameters
        ---------- 
        calendar : list, required

        Returns
        -------
        sets self.calendar and env.calendar
        
        See Also
        --------
        n/a
    
        Notes
        -----
        n/a
        
        Examples
        --------
        # Restrict calendar to all the days SPY traded
        data_source = YEOD_Source(DATA+'/eod_data/')
        sim = Simulator(start_dt, end_dt)
        sim.set_calendar(data_source.load('SPY').keys())
            
        """
        self.calendar = calendar

    def run(self,driver='eod'):
        for now in self.calendar:
            self.env.update(now)
            for algo in self.algos:
                algo.update_metrics(self.env)
                if self.start_dt <= now <= self.end_dt:
                    algo.update_strat(self.env)

if __name__ == '__main__':
    print 'Simulator Test'
