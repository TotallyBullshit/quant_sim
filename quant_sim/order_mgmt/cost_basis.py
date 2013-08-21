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

"""
A cost_basis method should define how an order is processed and handle
the nitty gritty of opening and closing a trade. The method will have access
to all first class objects that quant.algorithm has access to. Therefore, 
the cost_basis method should use self.open_order and self.close_order

The most common method is the First-in-First-out (FIFO). However for different
tax efficiency purposes, one might want to use a cost_averaging method or
Highest-in-First-out. 

cost_basis methods will directly affect how the end report statistics will appear
for an algorithm. For example; cost_averaging would not generate any closed trades
to pass through to the statistics manager

Parameters
---------- 
self : algorithm object, required
bar : EOD object, required
shares : int, required
price : float, optional, default bar.c


Returns
-------
n/a

See Also
--------
https://personal.vanguard.com/jumppage/costbasis/CostBasisMethod.html 
for different cost_basis methods to implement

Notes
-----
User should be mindful modifying self.positions while iterating through it.
It is not good practice to pop() from self.positions mid loop. This will
cause unstable code behavior. To avoid this, it is recommended to use a helper
function such as iterate_trades() which will do the iterating and return 
necessary info to continue processing and removing closed orders from the 
self.positions[sid]['active'] stack. The helper() should return False if the
iteration is complete.

Examples
--------
see quant.finances.cost_basis.FIFO
"""


def FIFO(self, bar, shares, **kwargs):
    price = kwargs.get('price', bar.c)
    def iterate_trades(shares):
        for i,active_ord in enumerate(self.positions[bar.sid]['active']):
            if active_ord.shares > 0 and shares < 0:
                if active_ord.shares == abs(shares):
                    self.close_order(active_ord, bar, active_ord.shares, price)
                    shares = 0
                    return i, shares
                elif active_ord.shares > abs(shares):
                    self.close_order(active_ord, bar, abs(shares),price)
                    active_ord.shares -= abs(shares)
                    shares = 0
                    break
                elif active_ord.shares < abs(shares):
                    self.close_order(active_ord, bar, active_ord.shares,price)
                    shares += active_ord.shares
                    return i, shares
            elif active_ord.shares < 0 and shares > 0:
                if abs(active_ord.shares) == shares:
                    self.close_order(active_ord, bar, active_ord.shares,price)
                    shares = 0
                    return i, shares
                elif abs(active_ord.shares) > shares:
                    self.close_order(active_ord, bar, -shares,price)
                    active_ord.shares += shares
                    shares = 0
                    break
                elif abs(active_ord.shares) < shares:
                    self.close_order(active_ord, bar, active_ord.shares, price)
                    shares -= abs(active_ord.shares)
                    return i, shares
        return None, shares
    remove = 0
    while remove != None:
        remove,shares = iterate_trades(shares)
        if remove != None:
            self.positions[bar.sid]['active'].pop(remove)
    if abs(shares) > 0:
        self.open_order(bar, shares, price, **kwargs)