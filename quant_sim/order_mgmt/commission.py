
class Commission(object):
    """
    Commission object, which calculates the amount of commission charged for
    each trade based on the price and number of shares purchased

    Can be used 'as is' if the commission method is
    per_share or fixed.
    
    Otherwise, Inherit Commission and override apply_commission
    This is handy for modeling complex broker specific commission schemes
    
    Parameters
    ---------- 
    comm_id : str, optional, default 'fixed'
    ammt : float, optional, default 0.0
    

    Returns
    -------
    n/a
    
    See Also
    --------
    self.apply_commission

    Notes
    -----
    n/a
    
    Examples
    --------
    class AmeriTrade(Commission):
        def initialize(self, *args, **kwargs):
            self.small_amt = 0.05
            self.large_amt = 0.025
        def apply_commission(self, shares, price):
            if price < 10.0:
                return self.small_amt * shares
            else:
                return self.large_amt * shares
    """

    def __init__(self, *args, **kwargs):
        self.id = kwargs.get('comm_id', 'fixed')
        self.ammt = kwargs.get('ammt', 0.0)
        self.initialize(*args, **kwargs)

    def initialize(self, *args, **kwargs):
        pass

    def apply_commission(self, baar, shares, price):
        """
        API
        This method is called directly from quant.algorithm backend
        when an order is processed

        User should override this method if user wants to define a custom 
        commission model that is not per_share or fixed

        Returns
        =======
        float : total amount of commission for the order
        """
        if self.id == 'per_share':
            return self.ammt * abs(shares)
        if self.id == 'fixed':
            return self.ammt
        else:
            return self.calculate(bar, shares, price)
