import numpy as np
from queue import PriorityQueue
import math


class Street:
    def __init__(self, i, s):  # i to be id s to be spot
        self.id = i
        self.location = i  # temporarily
        self.max_spot = s
        self.currently_parked = 0
        self.is_full = False
        self.is_empty = True
        self.available_spot = self.max_spot
        self.t_pass_street = 0.1 * s

    def park_car(self):
        self.available_spot -= 1
        if self.currently_parked == self.max_spot:
            self.is_full = True

        self.is_empty = False

    def leave_car(self):
        self.available_spot += 1
        if self.currently_parked == 0:
            self.is_empty = True

        self.is_full = False


class Car:
    def __init__(self, id, entry_point, t_arrival, t_parking):
        self.id = id
        self.location = entry_point
        self.t_parking = t_parking
        self.t_arrival = t_arrival
        self.t_leaving = 0.0
        self.t_waiting = 0.0
        self.status = 0

    def park(self, street, clock):
        self.location = street.id
        self.status = 1
        self.t_leaving = clock + self.t_parking

    def leave(self, street):
        street.leave_car()
        self.status = 2

    def change_street(self, current, target):
        self.t_waiting += current.t_pass_street
        self.location = target


class ParkingSimulation:
    def __init__(self, t_arrival_list, t_parking_list):
        self.max_clock = 600

        self.num_block_m = 2  # m*n block
        self.num_block_n = 2
        self.size_x = 10  # each block size of x*y
        self.size_y = 20

        self.t_arrival_list = t_arrival_list
        self.t_parking_list = t_parking_list
        self.t_arrival = 0.0  # time of next arrival
        self.t_parking = 0.0  # parking time of next arriving car
        self.t_departure = 0.0  # next departure time
        self.t_change_street = 0.0

        self.streets = list()
        for i in range(0, 2 * 2 * 4 - 1):
            if i % 2 == 0:
                self.streets.append(Street(i, self.size_x))
            else:
                self.streets.append(Street(i, self.size_y))

        # adj matrix for turnable streets
        self.adj_streets = np.matrix([
            [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
            [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0]
        ])

        self.cars = PriorityQueue()  # cars in the system stores in a priority Queue
        self.num_cars = 0

        self.clock = 0.0  # simulation clock

        self.num_empty_spot = 0  # number of empty spot
        self.num_car_finding = 0  # current number finding parking

    def get_street(self, id):
        for str in self.streets:
            if str.id == id:
                return str

    # time routine
    # get and do next event
    def time_adv(self):
        if self.clock >= self.max_clock:
            self.end()
        self.t_arrival = self.t_arrival_list[0] + self.clock
        self.t_departure = float("inf")
        self.t_change_street = float("inf")
        tmp = self.cars.get()
        t = tmp[0]
        car = tmp[1]
        if car.status == 0:
            self.t_change_street = t

        if car.status == 1:
            self.t_departure = t

        t_next_event = min(self.t_arrival, self.t_change_street, self.t_departure)
        self.clock = t_next_event
        if t_next_event == self.t_arrival:
            self.arrival()
        if t_next_event == self.t_departure:
            self.departure()
        if t_next_event == self.t_change_street:
            self.change_street(car, self.get_street(car.location))

    def change_street(self, car, street):
        available_street = list()
        for i in range(0, 15):
            if self.adj_streets[street.id][i] == 1:
                available_street.append(self.get_street(i))

        r = np.random.uniform(low=0.0, high=len(available_street))
        i = math.floor(r)
        target_street = available_street[i]
        car.change_street(street, target_street)
        if not target_street.is_full:
            self.park(car, target_street)

    def park(self, car, street):
        car.park(street, self.clock)
        street.park_car()
        self.cars.get()  # update car in queue
        self.cars.put((car.t_leaving, car))

    # arrival event
    def arrival(self):
        entry_pt = 0  # self.get_entry_pt() # get the entry point
        c = Car(self.num_cars, entry_pt, self.t_arrival, self.t_parking)
        c.status = 0
        s = self.get_street(c.location)

        if not s.is_full:
            self.park(c, s)

        self.cars.put((self.clock + s.t_pass_street, c))
        self.time_adv()

    def departure(self):
        self.clock += self.t_departure
        c = self.cars.get()[1]
        c.leave()

    def end(self):
        pass


# inverse transform
def gen_exp_rv_list(lam, n):
    l = list
    for i in range(1, n):
        l.append(-np.log(1 - (np.random.uniform(low=0.0, high=1.0))) / lam)
    return l
