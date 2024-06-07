import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Polygon as MplPolygon
from shapely.geometry import Point
from shapely import centroid

fig, ax = plt.subplots()

"""setup for network creation"""
def generate_semicircle_polygon(center, radius, theta1, theta2, num_points=100):
    from shapely.geometry import Polygon
    angles = np.linspace(theta1, theta2, num_points)
    points = [(center[0] + radius * np.cos(angle), center[1] + radius * np.sin(angle)) for angle in angles]
    points.append(center)  # Close the polygon

    return Polygon(points)
def plot_point(point, color, alpha = 1, annotation = ""):
    ax.plot(point.x, point.y, "o", color=color, alpha=alpha)
    ax.annotate(annotation, xy=(point.x, point.y))

def plot_filled_semicircle(polygon, color, alpha=0.5, linestyle = 'solid', annotation="", annotation_color="white"):
    mpl_poly = MplPolygon(list(polygon.exterior.coords), closed=True, color=color, alpha=alpha, linestyle=linestyle)
    ax.add_patch(mpl_poly)
    center = centroid(polygon)
    ax.annotate(annotation, xy=(center.x, center.y), color=annotation_color)

def find_synapses(soma_points, r_dendrite, r_axon, dendrite_thetas, axon_thetas):

    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']
    dendrite_polys = []
    axon_polys = []
    intersection_polys = []
    for i in range(len(soma_points)):
       
        color_index = i % len(colors)
        center = soma_points[i]
        plot_point(Point(center[0],center[1]), color=colors[color_index], alpha = 0.7, annotation=str(i))

        theta1_dendrite, theta2_dendrite = dendrite_thetas[i]
        theta1_axon, theta2_axon = axon_thetas[i]
        
        dendrite_poly = generate_semicircle_polygon(center, r_dendrite, theta1_dendrite, theta2_dendrite)
        axon_poly = generate_semicircle_polygon(center, r_axon, theta1_axon, theta2_axon)

        dendrite_polys.append(dendrite_poly)
        axon_polys.append(axon_poly)

        plot_filled_semicircle(axon_poly, color=colors[color_index], alpha=0.5)
        plot_filled_semicircle(dendrite_poly, color=colors[color_index], alpha=0.5)
        # Generate and plot filled dendrite semicircle

    return find_overlapping_regions(axon_polys, dendrite_polys)


def find_overlapping_regions(axons, dendrites):
    n = len(dendrites)
    synapses = {}
    for i in range(len(axons)):
        axon = axons[i]
        overlapping_regions = []

        
        for j in range(1, n ** 2):

            overlap = axon
            region = []
            for k in range(n):

                if j & (1 << k):
                    #print(i, j)
                    if k != i:
                        overlap = overlap.intersection(dendrites[k])
                        region.append(k)
            if not overlap.is_empty and region != []:
                
                overlapping_regions.append(region)

        unique_overlapping_regions = [list(tup) for tup in set(tuple(region) for region in overlapping_regions)]

        
        synapses[i] = unique_overlapping_regions
    return  synapses

   

def find_overlap_points(x1, y1, x2, y2, threshold=0.1):
    overlap_x = []
    overlap_y = []
    for i in range(len(x1)):
        for j in range(len(x2)):
            if np.sqrt((x1[i] - x2[j])**2 + (y1[i] - y2[j])**2) < threshold:
                overlap_x.append((x1[i] + x2[j]) / 2)
                overlap_y.append((y1[i] + y2[j]) / 2)
    return overlap_x, overlap_y

def generate_synapses(soma_points):

    axon_angle = np.pi/4
    dendrite_angle = np.pi/3

    r_axon = 0.75
    r_dendrite = 0.5

    axon_thetas, dendrite_thetas = [], []

    overall_direction = 0
    direction_variance = np.pi/3


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

    synapses = find_synapses(soma_points, r_dendrite, r_axon, dendrite_thetas, axon_thetas)
    return synapses


if __name__ == '__main__':


    max_size = 1.5
    num_neurons = 30
    soma_points = []

    #modify this to be setting neuron_x, neuron_y values
    soma_x = np.random.rand(num_neurons) * max_size
    soma_y = np.random.rand(num_neurons) * max_size

    soma_points =  [(soma_x[i], soma_y[i]) for i in range(num_neurons)]
    synapses = generate_synapses(soma_points)
