import numpy as np
import numpy.random as rd

class PacketStation:
    WAIT = 0
    TRANSMIT = 1
    def __init__(self, CW_min, stage_max):
        self.CW_min = CW_min
        self.stage_max = stage_max
        self.state = self.WAIT
        self.backoff_stage = 0
        self.backoff_time = 0
        self.transmit_success = 0
        self.transmit_collision = 0
        self.time_step_ctr = 0
        self.markov_chains = list(np.zeros(CW_min * (2**m), dtype=int) for m in range(self.stage_max + 1))
        self.backoffStageInitialize()

    def backoffTimeCountdown(self, time_step):
        self.markov_chains[self.backoff_stage][(self.backoff_time-time_step):self.backoff_time] += 1
        self.backoff_time -= time_step
        self.time_step_ctr += time_step
        if self.backoff_time == 0:
            self.state = self.TRANSMIT

    def transmitPacket(self, collision):
        if collision:
            self.backoff_stage += 1 if self.backoff_stage != self.stage_max else 0
            self.transmit_collision += 1
        else:
            self.backoff_stage = 0
            self.transmit_success += 1
        self.state = self.WAIT
        self.backoffStageInitialize()

    def backoffStageInitialize(self):
        self.backoff_time = int(self.CW_min * (2**self.backoff_stage) * rd.random_sample())
        self.markov_chains[self.backoff_stage][self.backoff_time] += 1
        self.time_step_ctr += 1

    # def getProbability(self):
    #     probability_dict = {
    #         'tau': np.array()
    #     }
    #     return np.array(list())

if __name__ == "__main__":
    W, m, n = 32, 5, 6
    event_total = 100000
    packet_stations = list(PacketStation(CW_min=W, stage_max=m) for i in range(n))
    event_idx = 0
    transmit_result = np.zeros(n, dtype=int)
    while event_idx < event_total:
        backoff_time_min = min([station.backoff_time for station in packet_stations])
        station_transmit_ctr = 0
        for station_idx, station in enumerate(packet_stations):
            station.backoffTimeCountdown(time_step=backoff_time_min)
            if station.state == PacketStation.TRANSMIT:
                station_transmit_ctr += 1
        for station_idx, station in enumerate(packet_stations):
            if station.state == PacketStation.TRANSMIT:
                station.transmitPacket(collision=True if station_transmit_ctr > 1 else False)
        transmit_result[station_transmit_ctr - 1] += 1
        event_idx += 1
    for station_idx, station in enumerate(packet_stations):
        b_total = np.sum(list(np.sum(chain) for chain in station.markov_chains))
        time_step_total = station.time_step_ctr
        b0_total = np.sum(list(chain[0] for chain in station.markov_chains))
        transmit_total = station.transmit_collision + station.transmit_success
        print(b_total, time_step_total, b0_total, transmit_total)
        print(station.transmit_collision, station.transmit_success)
        print('tau:', b0_total / b_total)
        print('collision p:', station.transmit_collision / transmit_total)
    print(transmit_result)
    print('total collision p:', 1 - transmit_result[0] / np.sum(transmit_result))
        # print(b_total, time_step_total, transmit_total)
        # print(station.markov_chains[0])
