import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from shapely.geometry import Point
from shapely import centroid, area
ax = []

axon_polys = []

dendrite_polys = []
class connection():
    def __init__(self):
        self.hosts, self.connections, self.connection_poly = [], [], None

    def get_center(self):
        center_point = self.connection_poly.centroid
        return [center_point.x, center_point.y]
    def get_area(self):
        return area(self.connection_poly)
    def add_host(self, host):
        self.hosts.append(host)
    def add_connection(self, connection):
        self.connections.append(connection)
    def copy(self):
        new_con = connection()
        new_con.hosts = self.hosts.copy()
        new_con.connections = self.connections.copy()
        new_con.connection_poly = self.connection_poly
        return new_con
    def __str__(self):
        return "[pre_synaptic_neurons: {}, post_synaptic_neurons: {}, poly_area: {}]".format(str(self.hosts),  str(self.connections), str(self.get_area()))


"""setup for network creation"""
def generate_semicircle_polygon(center, radius, theta1, theta2, num_points=100):
    from shapely.geometry import Polygon
    angles = np.linspace(theta1, theta2, num_points)
    points = [(center.x + radius * np.cos(angle), center.y + radius * np.sin(angle)) for angle in angles]
    points.append(center)  # Close the polygon

    return Polygon(points)
def plot_point(ax, point, color, alpha = 1, annotation = ""):
    ax.plot(point.x, point.y, "o", color=color, alpha=alpha)
    ax.annotate(annotation, xy=(point.x, point.y))

def plot_filled_polygon(ax, polygon, color, alpha=0.5, linestyle = 'solid', annotation="", annotation_color="white"):
    mpl_poly = MplPolygon(list(polygon.exterior.coords), closed=True, color=color, alpha=alpha, linestyle=linestyle)
    ax.add_patch(mpl_poly)
    center = centroid(polygon)
    ax.annotate(annotation, xy=(center.x, center.y), color=annotation_color)

def generate_neuron_polys(soma_points, r_dendrite, r_axon, dendrite_thetas, axon_thetas):

    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']
    dendrite_polys = []
    axon_polys = []
    intersection_polys = []
    for i in range(len(soma_points)):
        
        color_index = i % len(colors)
        center = soma_points[i]

        theta1_dendrite, theta2_dendrite = dendrite_thetas[i]
        theta1_axon, theta2_axon = axon_thetas[i]
        
        dendrite_poly = generate_semicircle_polygon(center, r_dendrite, theta1_dendrite, theta2_dendrite)
        axon_poly = generate_semicircle_polygon(center, r_axon, theta1_axon, theta2_axon)

        dendrite_polys.append(dendrite_poly)
        axon_polys.append(axon_poly)

        #plot_filled_polygon(axon_poly, color=colors[color_index], alpha=0.5)
        #plot_filled_polygon(dendrite_poly, color=colors[color_index], alpha=0.5)
        # Generate and plot filled dendrite semicircle

    return [axon_polys, dendrite_polys]

def generate_synapses(axon_polys, dendrite_polys):
    intersections = []
    tmp_storage = []
    print(len(axon_polys), len(dendrite_polys))
    for i in range(len(axon_polys)):
        axon = axon_polys[i]
        #intersections.append([])

        for j in range(len(dendrite_polys)):
            if i == j: 
                continue
            dendrite = dendrite_polys[j]
            
            overlap = axon.intersection(dendrite)

            if not overlap.is_empty:

                con = connection()

                con.hosts = [i]
                con.connection_poly = overlap
                con.connections = [j]

                #intersections[i].append(con)
                tmp_storage.append(con)
                nested_intersections = get_nested_intersections(con, dendrite_polys)

                tmp_storage += nested_intersections
                #intersections[i] += nested_intersections
    return tmp_storage

def get_nested_intersections(intersection, polys, poly_type = "dendrite"):

    pre_synaptic_dirs = intersection.hosts
    post_synaptic_dirs = intersection.connections
    intersection_poly = intersection.connection_poly


    new_intersections = []
    new_connection = False
    #get list of intersections a given axon has
    
    for i in range(len(polys)):
 
        if i in pre_synaptic_dirs or i in post_synaptic_dirs:
            continue

        overlap = intersection_poly.intersection(polys[i])

        if not overlap.is_empty:

            new_connection = intersection.copy()
            new_connection.connection_poly = overlap

            if poly_type == "dendrite":
                new_connection.add_connection(i)
            elif poly_type == "axon":
                new_connection.add_host(i)
            new_intersections.append(new_connection)

            new_intersections += get_nested_intersections(new_connection, polys, poly_type)
        

    
    return new_intersections



def find_overlap_points(x1, y1, x2, y2, threshold=0.1):
    overlap_x = []
    overlap_y = []
    for i in range(len(x1)):
        for j in range(len(x2)):
            if np.sqrt((x1[i] - x2[j])**2 + (y1[i] - y2[j])**2) < threshold:
                overlap_x.append((x1[i] + x2[j]) / 2)
                overlap_y.append((y1[i] + y2[j]) / 2)
    return overlap_x, overlap_y

def create_poly_params(soma_points):

    axon_angle = np.pi/6
    dendrite_angle = np.pi/2.5

    r_axon = 2
    r_dendrite = 1

    axon_thetas, dendrite_thetas = [], []

    overall_direction = 0
    direction_variance = np.pi/4


    #array of the variance from the current direction for each soma
    variances = (np.random.rand(len((soma_points))) * direction_variance) - (direction_variance/2)

    #array 
    axon_directions = overall_direction + (variances)
    for i in range(len(soma_points)):
        axon_direction = axon_directions[i]
        theta1_axon = axon_direction + (axon_angle/2)  
        theta2_axon =  axon_direction - (axon_angle/2)
        axon_thetas.append((theta1_axon, theta2_axon))
        
        dendrite_direction = np.pi + axon_direction
        
        theta1_dendrite = dendrite_direction + (dendrite_angle/2)
        theta2_dendrite =  dendrite_direction - (dendrite_angle/2)
        dendrite_thetas.append((theta1_dendrite, theta2_dendrite))

        
        # 90 degrees in radians

    #synapses = find_synapses(soma_points, r_dendrite, r_axon, dendrite_thetas, axon_thetas)
    return [r_dendrite, r_axon, dendrite_thetas, axon_thetas]


def get_axon_overlap(synapses, axon_polys):
    #check where each axon overlaps with a synapse
    #alternatively:check what axons overlap with the same dendrite 
    new_synapses = []
    for i in range(len(synapses)):
        synapse_connection = synapses[i]
        
        new_synapses += get_nested_intersections(synapse_connection, axon_polys, poly_type="axon")
            

    return remove_duplicate_intersections(new_synapses)

def create_synapses(soma_points):
    global axon_polys
    global dendrite_polys

    if type(soma_points[0]) == tuple:
        soma_points = list(map(Point, soma_points))
    
    r_dendrite, r_axon, dendrite_thetas, axon_thetas = create_poly_params(soma_points)
    print("Creating polygons")
    axon_polys, dendrite_polys = generate_neuron_polys(soma_points, r_dendrite, r_axon, dendrite_thetas, axon_thetas)
    print("Generating synapses")
    no_overlap_synapses = generate_synapses(axon_polys, dendrite_polys)

    print("Removing any duplicate synapses")
    no_overlap_synapses = remove_duplicate_intersections(no_overlap_synapses)
    print("Removed")
    print("Getting axons that overlap existing synapses")
    synapses = get_axon_overlap(no_overlap_synapses, axon_polys)

    print("Found")

    synapses += no_overlap_synapses

    print(len(synapses))
    #check if any synapse overlaps with an axon.
    #if it does add that axon to the pre synaptic axons
    return synapses
def remove_duplicate_intersections(connections):
    unique_connections = {}

    for connection in connections:
        
        sorted_connection = sorted(connection.connections)
        sorted_hosts = sorted(connection.hosts)
        unique_connections["{},  {}".format(str(sorted_hosts),  str(sorted_connection))] = connection

    return [unique_connections[key] for key in unique_connections.keys()]
if __name__ == '__main__':
    fig, ax = plt.subplots()
    max_size = 3
    num_neurons = 5
    soma_points = []

    #modify this to be setting neuron_x, neuron_y values
    soma_x = np.random.rand(num_neurons) * max_size
    soma_y = np.random.rand(num_neurons) * max_size


    soma_points =  [Point(soma_x[i], soma_y[i]) for i in range(num_neurons)]
    
    synapses = create_synapses(soma_points)

    for point_ind in range(len(soma_points)):
        point = soma_points[point_ind]
        plot_point(ax, point, "#fc2803",annotation=str(point_ind))

    for ax_poly in axon_polys:
        plot_filled_polygon(ax, ax_poly, "#03fc6f")

    for den_poly in dendrite_polys:
        plot_filled_polygon(ax, den_poly, "#f003fc")
    
    for syn in synapses:
        print(syn)
        plot_filled_polygon(ax, syn.connection_poly, "#1c1c1c")

    """for key in synapses.keys():
        connections = synapses[key]


        synapses[key] = remove_duplicate_intersections(connections)
        
        [print(connection) for connection in synapses[key]]"""
    ax.set_aspect("equal")
    plt.draw() 
    plt.show()
