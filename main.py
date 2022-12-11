import random
import time
from math import ceil, floor
from queue import PriorityQueue

import numpy as np
import pandas
from matplotlib import pyplot, pyplot as plt

import graph
import input
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
        print("Car={} left the system".format(self.id))
        self.status = 2

    def change_street(self, current, target):
        self.t_waiting += current.t_pass_street
        self.location = target


class ParkingSimulation:
    def __init__(self, t_arrival_list, t_parking_list, street_num, max_clock, t_pre_parking, parked_spot_each_street):
        self.max_clock = max_clock

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

        self.t_pre_parking = t_pre_parking  # The parking time of cars that has been parking before simulation
        self.num_of_parked_spots_each_street = parked_spot_each_street  # The number of cars that has been parking on each street before simulation
        self.street_num = street_num  # Total number of streets
        self.streets, self.adj_streets = streets.generate_streets(street_num)

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
        self.warmup_car_id = -1
        self.last_arrival = self.clock

        self.utilizaiton = []
        self.num_empty_spot = 0  # number of empty spot
        self.num_car_finding = [[] for i in range(2)]  # current number finding parking

    def get_car(self, id):
        for car in self.cars_list:
            if car.id == id:
                return car

    def warmup(self):
        for s in self.streets:
            for n in range(self.num_of_parked_spots_each_street):
                c = Car(self.num_cars, s, 0, self.t_pre_parking.pop(0))
                self.cars_list.append(c)
                self.num_cars += 1
                self.park(c, s)
        assert self.num_cars == len(self.streets) * self.num_of_parked_spots_each_street
        time.sleep(10)

        while (self.clock < 120):
            self.time_adv(True)
        self.warmup_end_time = self.clock
        self.warmup_car_id = self.num_cars - 1
        print("----------------END WARMUP-----------------------------")
        time.sleep(10)

    def run(self):
        self.warmup()
        result = 1
        while (result != 0):
            result = self.time_adv(False)
        return 0

    def get_street(self, id):
        for str in self.streets:
            if str.id == id:
                return str

    # time routine
    # get and do next event
    def time_adv(self, warmup):
        print("-------------------------------------------T={}".format(self.clock))
        # Statistic
        if warmup==False:
            un_parked = 0
            for car in self.cars_list[self.warmup_car_id + 1:]:
                if car.status == 0:
                    un_parked += 1
            self.num_car_finding[0].append(self.clock)
            self.num_car_finding[1].append(un_parked)
            total_parked = 0
            for street in self.streets:
                total_parked += street.currently_parked
            utilization = total_parked / (self.street_num * self.streets[0].max_spot)
            self.utilizaiton.append(utilization * 100)
        if self.clock >= self.max_clock:
            print("----------------------------------------------------------------------Maximum time reached!")
            self.end()
            return 0
        if self.t_arrival_list:
            self.t_arrival = self.t_arrival_list[0] + self.last_arrival
        else:
            self.t_arrival = float("inf")
        self.t_departure = float("inf")
        self.t_change_street = float("inf")

        if not self.cars.empty():
            tmp = self.cars.get()
            t = tmp[0]
            car_id = tmp[1]
            car = self.get_car(car_id)
            if car.status == 0:
                print("Next Event in the queue is Change street at T={} Car={} at street {}".format(tmp[0], tmp[1],
                                                                                                    self.get_car(tmp[
                                                                                                                     1]).location))
                self.t_change_street = t

            if car.status == 1:
                print("Next Event in the queue is Leave at T={} Car={}".format(tmp[0], tmp[1]))
                self.t_departure = t
            self.cars.put(tmp)
        else:
            if not self.t_arrival_list:  # no event in the queue and no new car arrival
                print("------------------------------------------------------------------------All cars left!")
                self.end()
                return 0
        t_next_event = min(self.t_arrival, self.t_change_street, self.t_departure)
        self.clock = t_next_event
        if t_next_event == self.t_arrival:
            self.t_arrival_list.pop(0)
            self.last_arrival = self.clock
            self.arrival()
        else:
            if t_next_event == self.t_departure:
                self.departure()

            else:
                if t_next_event == self.t_change_street:
                    self.change_street()

    def change_street(self):
        car_id = self.cars.get()[1]
        car = self.get_car(car_id)
        current_street = self.get_street(car.location)
        available_street = [index for index, i in enumerate(self.adj_streets[current_street.id]) if
                            i == 1]  # a list of ids of turnable streets
        if current_street.id >= (len(self.streets) / 2):  # add id of the street for U turn
            available_street.append(int(current_street.id - len(self.streets) / 2))
        else:
            available_street.append(int(current_street.id + len(self.streets) / 2))
        print("----available streets {}".format(available_street))
        target_street_id = random.choice(available_street)
        target_street = self.get_street(target_street_id)
        car.change_street(current_street, target_street.id)
        if not target_street.is_full:
            self.park(car, target_street)

        else:
            self.cars.put((self.clock + target_street.t_pass_street, car.id))

    def park(self, car, street):
        car.park(street, self.clock)
        street.park_car()
        print("Car={} parked at street={} at T={} Parking time = {} Waiting time = {}".format(car.id, street.id,
                                                                                              self.clock, car.t_parking,
                                                                                              car.t_waiting))
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
        self.t_parking = self.t_parking_list.pop(0)
        c = Car(self.num_cars, entry_pt, self.t_arrival, self.t_parking)
        self.cars_list.append(c)
        self.num_cars += 1
        s = self.get_street(c.location)
        print("Next Event is Arrival at T={} Car={}".format(self.clock, self.num_cars - 1))
        print("Entry point " + str(entry_pt) + " is choosen")
        if not s.is_full:
            self.park(c, s)
        else:
            print("put arrival car into queue {} {}".format(c.t_arrival + s.t_pass_street, c.id))
            self.cars.put((c.t_arrival + s.t_pass_street, c.id))

    def departure(self):
        car_id = self.cars.get()[1]
        car = self.get_car(car_id)
        car.leave(self.get_street(car.location))

    def end(self):
        print("---------------Ending program--------------------")
        time.sleep(5)
        statistic_car_id = self.warmup_car_id + 1
        print("First ID" + str(statistic_car_id))
        print("Last ID" + str(self.num_cars - 1))
        for c in self.cars_list[statistic_car_id:]:
            if c.status == 0:
                print("Car={} has not found parking spot".format(c.id, c.status))
        un_parked = 0
        for car in self.cars_list[statistic_car_id:]:
            if car.status == 0:
                un_parked += 1
        print("The number of unparked car={}".format(un_parked))
        spending_time = [car.t_waiting for car in self.cars_list[statistic_car_id:] if car.status != 0]

        plt.hist(spending_time, bins=range(floor(min(spending_time)), ceil(max(spending_time)) + 1, 1))
        plt.savefig('histogram.png')
        plt.close()

        # utilization
        plt.plot(self.num_car_finding[0], self.num_car_finding[1])  # Plot the chart
        plt.savefig('num_car_finding.png')
        plt.close()

        plt.plot(self.num_car_finding[0], self.utilizaiton)  # Plot the chart
        plt.savefig('utilization.png')
        plt.close()
        print("Program end")
        return 0


def main():
    streets_num = 128
    cars_num = 10000
    parked_spot_each_street = 9

    parking = [i * 60 for i in
               [9, 8, 7.5, 7, 10, 12, 8, 9, 9.5, 7, 5.5, 55, 49, 22, 46, 2, 4, 0.5, 0.2, 1, 2, 1.5, 0.5, 7, 3.5, 7.5,
                5.5, 15,
                14.5, 12.5, 16, 40.5]]

    park_lam = input.caculate_lam(parking)
    print(park_lam)
    input.exp_KS_test(parking, park_lam, 0.990)
    parking_rns = input.gen_rn_list(cars_num)
    parking_rvs = input.gen_exp_rv_list(park_lam, parking_rns)

    pre_parking_rns = input.gen_rn_list(parked_spot_each_street * streets_num)
    pre_parking_rvs = input.gen_exp_rv_list(park_lam, pre_parking_rns)
    print(len(pre_parking_rvs))

    interarrval = [i / 60 for i in
                   [30, 1, 10, 2, 50, 40, 20, 60, 50, 0.5, 0.5, 105, 40, 65, 90, 30, 20, 15, 40, 50, 20, 52, 5, 1, 10,
                    2, 15, 20]]

    arrival_lam = input.caculate_lam(interarrval)
    print(arrival_lam)
    input.exp_KS_test(interarrval, arrival_lam, 0.990)
    arrival_lam_rns = input.gen_rn_list(cars_num)
    interarrval_rvs = input.gen_exp_rv_list(arrival_lam, arrival_lam_rns)
    print("ALL RV's generated")
    time.sleep(5)
    sim = ParkingSimulation(interarrval_rvs, parking_rvs, streets_num, 480, pre_parking_rvs, parked_spot_each_street)
    sim.run()


main()
