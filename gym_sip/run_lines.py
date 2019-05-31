import lines as ll
import matplotlib.pyplot as plt 
import threading
import time

class Start:
    def __init__(self, fn='mlb2', game_type='mlb', run=1, verbosity=False):
        self.fn = fn
        self.gt = game_type

        self.sip = ll.Sippy(fn=self.fn, league=self.gt, verbosity=verbosity)
        self.sip.step()
        
        if len(self.sip.games) > 0:
            self.game = self.sip.games[0]
        if run != 0:
            self.run()

    def run(self):
        self.sip.run()
