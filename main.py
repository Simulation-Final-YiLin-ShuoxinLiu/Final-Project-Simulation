import random

import numpy as np
from queue import PriorityQueue
import math
import streets

'''
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
        self.currently_parked += 1
        if self.currently_parked == self.max_spot:
            self.is_full = True

        self.is_empty = False

    def leave_car(self):
        self.available_spot += 1
        if self.currently_parked == 0:
            self.is_empty = True

        self.is_full = False
'''


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

        self.streets, self.adj_streets = streets.generate_streets(32)

        self.entry_pt = self.generate_entry_pt()

        '''
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
        '''
        self.cars_list = []
        self.cars = PriorityQueue()  # cars in the system stores in a priority Queue
        self.num_cars = 0

        self.clock = 0.0  # simulation clock
        self.last_arrival= self.clock

        self.num_empty_spot = 0  # number of empty spot
        self.num_car_finding = 0  # current number finding parking

    def get_car(self, id):
        for car in self.cars_list:
            if car.id == id:
                return car

    def run(self):
        self.time_adv()

    def get_street(self, id):
        for str in self.streets:
            if str.id == id:
                return str

    # time routine
    # get and do next event
    def time_adv(self):
        print("-------------------------------------------T={}".format(self.clock))
        if self.clock >= self.max_clock:
            self.end()
        self.t_arrival = self.t_arrival_list[0] + self.last_arrival
        self.t_departure = float("inf")
        self.t_change_street = float("inf")

        if not self.cars.empty():
            test = self.cars.get()
            if self.get_car(test[1]).status==1:
                print("Next Event in the queue is Leave at T={} Car={}".format(test[0],test[1]))
            else:
                print("Next Event in the queue is Change street at T={} Car={}".format(test[0], test[1]))
            self.cars.put(test)

            tmp = self.cars.get()
            t = tmp[0]
            car_id = tmp[1]
            car = self.get_car(car_id)
            if car.status == 0:
                self.t_change_street = t

            if car.status == 1:
                self.t_departure = t

            self.cars.put(tmp)

        t_next_event = min(self.t_arrival, self.t_change_street, self.t_departure)

        self.clock = t_next_event
        if t_next_event == self.t_arrival:
            print("Next Event is Arrival at T={}".format(t_next_event))
            self.t_arrival_list.pop(0)
            self.last_arrival = self.clock
            self.arrival()
        else:
            if t_next_event == self.t_departure:
                self.departure()

            else:
                if t_next_event == self.t_change_street:
                    self.change_street(car, self.get_street(car.location))
        self.time_adv()

    def change_street(self, car, current_street):
        available_street = [index for index, i in enumerate(self.adj_streets[current_street.id]) if i == 1] # a list of ids of turnable streets
        if current_street.id > len(self.streets) / 2:  # add id of the street for U turn
            available_street.append(current_street.id + len(self.streets) / 2)
        else:
            available_street.append(current_street.id - len(self.streets) / 2)
        target_street_id = random.choice(available_street)
        target_street = self.get_street(target_street_id)
        car.change_street(current_street, target_street.id)
        if not target_street.is_full:
            self.park(car, target_street)

        else:
            self.cars.get()
            self.cars.put((self.clock + target_street.t_pass_street, car.id))

    def park(self, car, street):
        car.park(street, self.clock)
        street.park_car()
        print(self.clock, car.t_leaving, type(car))
        self.cars.put((car.t_leaving, car.id))

    def generate_entry_pt(self):
        entry_pts = []
        m1 = self.adj_streets.sum(axis=0)
        for id, i in enumerate(m1):
            if i <= 1:
                entry_pts.append(id)
        print("All possible entry points {}".format(entry_pts))
        return entry_pts

    def get_entry_pt(self):
        return random.choice(self.entry_pt)

    # arrival event
    def arrival(self):
        entry_pt = self.get_entry_pt()  # self.get_entry_pt() # get the entry point
        print("entry point " + str(entry_pt) + " is choosen")
        self.t_parking = self.t_parking_list.pop(0)
        c = Car(self.num_cars, entry_pt, self.t_arrival, self.t_parking)
        self.cars_list.append(c)
        self.num_cars+=1
        c.status = 0
        s = self.get_street(c.location)
        if not s.is_full:
            self.park(c, s)

        else:
            self.cars.put((c.t_arrival + s.t_pass_street, c.id))

    def departure(self):
        car_id = self.cars.get()[1]
        car = self.get_car(car_id)
        car.leave(self.get_street(car.location))

    def end(self):
        pass


# inverse transform
def gen_exp_rv_list(lam, n):
    l = list()
    for i in range(1, n):
        l.append((-np.log(1 - (np.random.uniform(low=0.0, high=1.0))) / lam))
    return l


def main():
    t_interarrival_list = [5, 6, 8, 2, 1, 6]
    t_parking_list = [5, 15, 15, 6, 4, 8]

    # t_parking_list = gen_exp_rv_list(1/60, 10)

    sim = ParkingSimulation(t_interarrival_list, t_parking_list)
    sim.run()

main()
