# from scratch max heap
class MaxHeap:
    def __init__(self):
        self.heap = []

    def parent(self, i):
        return (i - 1) // 2

    def left(self, i):
        return 2 * i + 1

    def right(self, i):
        return 2 * i + 2

    def get_max(self):
        if not self.is_empty():
            return self.heap[0]
        return None

    def extract_max(self):
        if self.is_empty():
            return None

        max_item = self.heap[0]
        last_item = self.heap.pop()
        if not self.is_empty():
            self.heap[0] = last_item
            self.max_heapify(0)

        return max_item

    def max_heapify(self, i):
        left_child = self.left(i)
        right_child = self.right(i)
        largest = i

        if left_child < len(self.heap) and self.heap[left_child] > self.heap[largest]:
            largest = left_child

        if right_child < len(self.heap) and self.heap[right_child] > self.heap[largest]:
            largest = right_child

        if largest != i:
            self.heap[i], self.heap[largest] = self.heap[largest], self.heap[i]
            self.max_heapify(largest)

    def insert(self, item):
        self.heap.append(item)
        i = len(self.heap) - 1
        while i > 0 and self.heap[self.parent(i)] < self.heap[i]:
            self.heap[i], self.heap[self.parent(i)] = self.heap[self.parent(i)], self.heap[i]
            i = self.parent(i)

    def is_empty(self):
        return len(self.heap) == 0


class Graph:
    def __init__(self):
        self.vertices = {}
        self.edges = []

    def add_edge(self, source, destination, min_freight_cars_to_move, max_parcel_capacity):
        # creates vertices if they don't exist
        if source not in self.vertices:
            self.vertices[source] =Vertex(source, min_freight_cars_to_move, max_parcel_capacity)
        if destination not in self.vertices:
            self.vertices[destination] = Vertex(destination, min_freight_cars_to_move, max_parcel_capacity)

        # add destination to source's neighbors
        self.vertices[source].add_neighbor(self.vertices[destination])
        # add source to destination's neighbors
        # each vertex should have a min_freight_cars_to_move and max_parcel_capacity data fields (# this is optional, but recommended for ideal solution)
        self.vertices[destination].add_neighbor(self.vertices[source])
        self.edges.append((source,destination))

    def print_graph(self): #optional
        for vertex_name, vertex in self.vertices.items():
            print(f"Vertex: {vertex_name}")
            print(f"Neighbors: {[neighbor.name for neighbor in vertex.neighbors]}")
            print()

    def bfs(self, source, destination):
        # returns a list of vertices in the path from source to destination using BFS
        # actual move might only use next vertex in the path though (careful understanding required)
        visited = set()
        queue = [[self.vertices[source]]]
        while queue:
            path = queue.pop(0)
            vertex = path[-1]
            if vertex.name == destination:
                return [vertex.name for vertex in path]
            if vertex not in visited:
                for neighbor in vertex.neighbors:
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)
                visited.add(vertex)

    def dfs(self, source, destination):
        # returns a list of vertices in the path from source to destination using DFS
        # actual move might only use next vertex in the path though (careful understanding required)
        # ordering of vertices is important, create vertices in the order they are seen in the input file
        visited = set()
        stack = [[self.vertices[source]]]
        while stack:
            path = stack.pop()
            vertex = path[-1]
            if vertex.name == destination:
                return path
            if vertex not in visited:
                for neighbor in vertex.neighbors:
                    new_path = list(path)
                    new_path.append(neighbor)
                    stack.append(new_path)
                visited.add(vertex)

    def groupFreightCars(self):
        # group freight cars at every vertex based on their destination
        for vertex in self.vertices.values():
            vertex.loadFreightCars()

    def moveTrains(self):
        # move trains  (constitutes one time tick)
        # a train should move only if has >= min_freight_cars_to_move freight cars to link (link is a vertex, obtained from bfs or dfs)
        # once train moves from the source vertex, all the freight cars should be sealed and cannot be unloaded (at any intermediate station) until they reach their destination
        for vertex_name, vertex in self.vertices.items():
            if vertex.trains_to_move and len(vertex.trains_to_move) >= vertex.min_freight_cars_to_move:
                for destination, freight_cars in vertex.trains_to_move.items():
                    if all(freight_car.can_move() for freight_car in freight_cars):
                        for freight_car in freight_cars:
                            freight_car.move(destination)
                            vertex.sealed_freight_cars.extend(freight_cars)
                            vertex.trains_to_move.pop(destination)
                        break


class Vertex:
    def __init__(self, name, min_freight_cars_to_move, max_parcel_capacity):


        self.name = name
        self.freight_cars = []
        self.neighbors = []
        self.trains_to_move = None
        self.min_freight_cars_to_move = min_freight_cars_to_move
        self.max_parcel_capacity = max_parcel_capacity
        self.parcel_destination_heaps = {}
        self.sealed_freight_cars = []

        self.all_parcels = []

    def add_neighbor(self, neighbor):
        # add neighbor to self.neighbors
         self.neighbors.append(neighbor)
    
    def get_all_current_parcels(self):
        # return all parcels at the current vertex
        all_parcels = []
        for destination, heap in self.parcel_destination_heaps.items():
            all_parcels.extend(heap.heap)
        return all_parcels
    
    def clean_unmoved_freight_cars(self):
        # remove all freight cars that have not moved from the current vertex
        # add all parcels from these freight cars back to the parcel_destination_heaps accoridingly
        new_freight_cars = []
        for freight_car in self.freight_cars:
            if freight_car.current_location == self.name and len(freight_car.parcels) >= self.min_freight_cars_to_move:
                new_freight_cars.append(freight_car)
            else:
                # Add parcels back to heap if the freight car is not moving
                for parcel in freight_car.parcels:
                    self.parcel_destination_heaps[parcel.destination].insert(parcel)
        self.freight_cars = new_freight_cars

    def loadParcel(self, parcel):
        # load parcel into parcel_destination_heaps based on parcel.destination
        destination = parcel.destination
        if destination not in self.parcel_destination_heaps:
            self.parcel_destination_heaps[destination] = MaxHeap()
        self.parcel_destination_heaps[destination].insert(parcel)


    def loadFreightCars(self):
        # load parcels onto freight cars based on their destination
        # remember a freight car is allowed to move only if it has exactly max_parcel_capacity parcels
        for destination, heap in self.parcel_destination_heaps.items():
            while not heap.is_empty():
                freight_car = FreightCar(self.max_parcel_capacity)
                for _ in range(self.min_freight_cars_to_move):
                    if not heap.is_empty():
                        parcel = heap.extract_max()
                        freight_car.load_parcel(parcel)
                self.freight_cars.append(freight_car)    


    def print_parcels_in_freight_cars(self):
        # optional method to print parcels in freight cars
        for destination, heap in self.parcel_destination_heaps.items():
            for parcel in heap.heap:
                print(f"Parcel ID: {parcel.parcel_id}, Parcel origin: {parcel.origin}, Parcel destination: {parcel.destination}, Parcel priority: {parcel.priority}")
        

class FreightCar:
    def __init__(self, max_parcel_capacity):

        self.max_parcel_capacity = max_parcel_capacity
        self.parcels = []
        self.destination_city = None
        self.next_link = None
        self.current_location = None
        self.sealed = False

    def load_parcel(self, parcel):
        # load parcel into freight car
        self.parcels.append(parcel)

    def can_move(self):
        # return True if freight car can move, False otherwise
        return len(self.parcels) == self.max_parcel_capacity
        
    def move(self, destination):
        # update current_location
        # empty the freight car if destination is reached, set all parcels to delivered
        self.current_location = destination
        self.parcels = []  # Assuming all parcels are delivered once the freight car moves
        self.sealed = True



class Parcel:
    def __init__(self, time_tick, parcel_id, origin, destination, priority):
        self.time_tick = time_tick
        self.parcel_id = parcel_id
        self.origin = origin
        self.destination = destination
        self.priority = priority
        self.delivered = False
        self.current_location = origin

class PRC:
    def __init__(self, min_freight_cars_to_move=5, max_parcel_capacity=5):
        self.graph = Graph()
        self.freight_cars = []
        self.parcels = {}
        self.parcels_with_time_tick = {}
        self.min_freight_cars_to_move = min_freight_cars_to_move
        self.max_parcel_capacity = max_parcel_capacity
        self.time_tick = 1

        self.old_state = None
        self.new_state = None

        self.max_time_tick = 10


    
    def get_state_of_parcels(self):
        return {x.parcel_id:x.current_location for x in self.parcels.values()}
        

    def process_parcels(self, booking_file_path):
        # read bookings.txt and create parcels, populate self.parcels_with_time_tick (dict with key as time_tick and value as list of parcels)
        # and self.parcels (dict with key as parcel_id and value as parcel object)
        with open(booking_file_path, 'r') as file:
            for line in file:
                time_tick, parcel_id, source, destination, priority = line.strip().split()
                time_tick, priority = int(time_tick), int(priority)
                parcel = Parcel(parcel_id, source, destination, priority, time_tick)
                self.parcels[parcel_id] = parcel
                self.parcels_with_time_tick.setdefault(time_tick, []).append(parcel)

    
    def getNewBookingsatTimeTickatVertex(self, time_tick, vertex):
        # return all parcels at time tick and vertex
        return self.parcels_with_time_tick.get(time_tick, [])
        
    def create_graph(self, graph_file_path):
        with open(graph_file_path, 'r') as file:
            for line in file:
                source, destination = line.strip().split()
                self.graph.add_edge(source, destination,self.min_freight_cars_to_move, self.max_parcel_capacity)

    def run_simulation(self, run_till_time_tick=None):
        # run simulation till run_till_time_tick if provided, if not run till max_time_tick
        # if convergence is achieved (before run_till_time_tick or max_time_tick), stop simulation
        # convergence is state of parcels in the system does not change from one time tick to the next, and there are no further incoming parcels in next time ticks
        self.time_tick = self.max_time_tick-1

    def convergence_check(self, previous_state, current_state):
        # return True if convergence achieved, False otherwise
        pass

    def all_parcels_delivered(self):
        return all(parcel.delivered for _,parcel in self.parcels.items())
    
    def get_delivered_parcels(self):
        return [parcel.parcel_id for parcel in self.parcels.values() if parcel.delivered]
    
    def get_stranded_parcels(self):
        return [parcel.parcel_id for parcel in self.parcels.values() if not parcel.delivered]

    def status_of_parcels_at_time_tick(self, time_tick):
        return [(parcel.parcel_id, parcel.current_location, parcel.delivered) for parcel in self.parcels.values() if parcel.time_tick <= time_tick and not parcel.delivered]
    
    def status_of_parcel(self, parcel_id):
        return self.parcels[parcel_id].delivered, self.parcels[parcel_id].current_location

    def get_parcels_delivered_upto_time_tick(self, time_tick):
        return [parcel.parcel_id for parcel in self.parcels.values() if parcel.time_tick <= time_tick and parcel.delivered]



if __name__ == "__main__":
    
    min_freight_cars_to_move = 2
    max_parcel_capacity = 2

    prc = PRC(min_freight_cars_to_move, max_parcel_capacity)

    prc.create_graph('samples/5/graph.txt')
    prc.process_parcels('samples/5/bookings.txt')

    prc.run_simulation()

    print(f'All parcels delivered: {prc.all_parcels_delivered()}')
    print(f'Delivered parcels: {prc.get_delivered_parcels()}')
    print(f'Stranded parcels: {prc.get_stranded_parcels()}')
