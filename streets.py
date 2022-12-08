class Street:
    def __init__(self, i, head=None, end=None):  # i to be id s to be spot
        if end is None:
            self.end = [None, None, None]
        else:
            self.end = end  # end, a list of street [left,stright, right]

        if head is None:
            self.head = [None, None, None]
        else:
            self.head = [None, None, None]  # head, a list of street [left,stright, right]

        self.id = i
        self.max_spot = 10
        self.currently_parked = 0
        self.is_full = False
        self.is_empty = True
        self.available_spot = self.max_spot
        self.t_pass_street = 0.3



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

    def __str__(self):
        return str(self.id) + str(self.head) + str(self.end)


def generate_streets(n):
    streets = []
    street_ids = list(range(n))
    streets.append(Street(i=street_ids.pop(0)))
    streets.append(Street(i=street_ids.pop(0)))
    streets.append(Street(i=street_ids.pop(0)))
    streets.append(Street(i=street_ids.pop(0)))
    streets[0].end = [streets[1], streets[2], streets[3]]
    streets[1].end = [streets[0], streets[3], streets[2]]
    streets[2].end = [streets[1], streets[0], streets[3]]
    streets[3].end = [streets[2], streets[1], streets[0]]
    for i in range(n):
        if i >= len(streets) - 1:
            if len(street_ids) < 1:
                break
            current = Street(street_ids.pop(0))
            streets.append(current)
        else:
            current = streets[i]

        pos = 0
        for s in current.head:
            if s is None:
                if len(street_ids) < 1:
                    return streets
                new_street_id = street_ids.pop(0)
                new_street = Street(new_street_id)
                streets.append(new_street)
                new_street.end[pos] = current
                current.head[pos] = new_street
                if current.end[0].head[2] is not None and pos==0:
                    current.head[0].head[0]= current.end[0].head[2]
                    current.end[0].head[2].head[2]=current.head[0]
                if current.end[2].head[0] is not None and pos==2:
                    current.head[2].head[2]= current.end[2].head[0]
                    current.end[2].head[0].head[0]=current.head[2]
            pos += 1
        if current in current.head[0].end:
            current.head[0].end=[current,current.head[2],current.head[1]]
        else:
            current.head[0].head = [current.head[1],current.head[2],current]
        if current in current.head[1].end:
            current.head[1].end = [current.head[0], current, current.head[2]]
        else:
            current.head[1].head = [current.head[2], current, current.head[0]]
        if current in current.head[2].end:
            current.head[2].end = [current.head[1], current.head[0], current]
        else:
            current.head[2].head = [current, current.head[0], current.head[1]]
    return streets


streets = generate_streets(50)
for i in streets:
    print(i.id)
    for v in range(3):
        if i.head[v] is not None:
            print(i.head[v].id)
        else:
            print("x")
    for v in range(3):
        if i.end[v] is not None:
            print(i.end[v].id)
        else:
            print("x")
    print()
