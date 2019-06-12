import numpy as np

class Station:
    def __init__(self, CW_min, stage_max):
        self.CW_min = CW_min
        self.stage_max = stage_max
        self.transmit_ctr = 0