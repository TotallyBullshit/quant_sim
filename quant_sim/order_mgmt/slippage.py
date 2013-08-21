
class Slippage(object):
    def __init__(self, spread=0.0, *args, **kwargs):
        self.id = kwargs.get('slip_id', None)
        self.ammt = kwargs.get('ammt', 0.0)
    
    def apply_slippage(self, bar, shares, price):
        if self.id == 'fixed':            
            if shares > 0:
                return shares, price + (self.ammt / 2.0)
            else:
                return shares, price - (self.ammt / 2.0)
        else:
            return self.calculate(bar, shares, price)
            
    def calculate(self, bar, shares, price):
        pass
