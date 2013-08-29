
class Quant_Sim_Error(Exception):
    def __init__(self, msg='', *args, **kwargs):
        self.args = [a for a in args]
        self.kwargs = kwargs
        self.msg = msg

class Date_Not_In_History_Error(Quant_Sim_Error):
    def __str__(self):
        date = self.kwargs.get('date',None)
        now = self.kwargs.get('now',None)
        if self.msg == '':
            return 'DateNotInHistory: %s not in History' % (date)
        else: 
            return self.msg
        
class SID_Error(Quant_Sim_Error):
    def __str__(self):
        sid = self.kwargs.get('sid',None)
        if self.msg == '':
            return 'SIDError: %s not in data' % (sid)
        else: 
            return self.msg
