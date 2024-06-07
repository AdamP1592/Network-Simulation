
class neuron_network():
    def __init__(self, num_neurons: int, num_synapses: int):
        self.__num_neurons = num_neurons

    #synapses should be generated within the groupings by mean

    def euclid_distance(data0, data1):
        #data0 and data1 have to have matching lengths
        if len(data0) != len(data1):
            raise Exception("Mismatched data lengths")
        
        import math

        distance = 0
        for i in range(len(data0)):
            distance +=  (data0[i] - data1[i])**2 
        distance = math.sqrt(distance)
    
    
    def setup_synapses(self, positions):
        import numpy as np
        #positions are (x, y)
        max_groups = 12
        num_groups = 1


        soma_size = 0.2

        max_dendrite_length = 2 * soma_size
        dendrite_radius = np.pi/4 # 45 degrees

        max_axon_length = 4 * soma_size

        axon_radius = np.pi / 6 #30 degrees
        axon_direction = np.pi/4

        axon_angle_1 = axon_direction + (axon_radius / 2)
        axon_angle_2 = axon_direction - (axon_radius / 2)

        m1 = np.tan(axon_angle_1)
        m2 = np.tan(axon_angle_2)

        

    #desired input
    #generate_axon creates a semicircle section that if it overlaps with another semicircle section
    #then a synapse is established.
    

    def setup_neurons(self):
        import numpy as np
        import neuron_models
        import json
        current_max_neurons = 50 #only 50 prepared neurons

        params = []
        #   ena, ek, eleak 
        #   gna, gk, gleak
        #   c, vrest, vthresh
        num_params = 9

        with open('./data/neuron_params.json') as f:
            data = json.load(f)
            #generats list of neuron params from pre_calc data
            [params.append(data[key]) for key in data.keys()]

        #generates list of the neuron paramet


        parameters = np.random.choice(params,self.__num_neurons)

        print(parameters)
        neurons_positions = np.random.rand((self.__num_neurons))
        dt = 0.01
        self.neurons = []


        for i in range(self.__num_neurons):
            
            neuron_params_dict = parameters[i]
            resting, action_thresh = neuron_params_dict['vrest'], neuron_params_dict['vthresh']

            neuron = neuron_models.hodgkin_huxley(action_thresh, resting, dt=dt)
            neuron.set_params(neuron_params_dict)

            self.neurons.append(neuron)

        print(len(self.neurons))
        for i in self.neurons:
            break
        
import numpy as np
    
if __name__ == '__main__':
    import generate_synapses

    network = neuron_network(5, 10)


    network.setup_neurons()


    max_size = 1.5
    num_neurons = 10
    soma_points = []

    #modify this to be setting neuron_x, neuron_y values
    soma_x = np.random.rand(num_neurons) * max_size
    soma_y = np.random.rand(num_neurons) * max_size

    soma_points =  [(soma_x[i], soma_y[i]) for i in range(num_neurons)]

    synapses = generate_synapses.generate_synapses(soma_points)

    print(synapses)
