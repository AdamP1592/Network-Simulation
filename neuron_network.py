
class neuron_network():
    def __init__(self, num_neurons: int):
        self.__num_neurons = num_neurons

        self.setup_neurons()
        self.setup_synapses()

        print(self.neurons)
        print(self.synapses)

    #synapses should be generated within the groupings by mean
    def iterate(self):
        for i in self.neurons:
            i.update()

        

    def euclid_distance(data0, data1):
        #data0 and data1 have to have matching lengths
        if len(data0) != len(data1):
            raise Exception("Mismatched data lengths")
        
        import math

        distance = 0
        for i in range(len(data0)):
            distance +=  (data0[i] - data1[i])**2 
        distance = math.sqrt(distance)
    
    
    def setup_synapses(self):
        import numpy as np
        import generate_synapses
        from synapse import synapse
        #positions are (x, y)
        max_size = 5

        #modify this to be setting neuron_x, neuron_y values
        soma_x = np.random.rand(self.__num_neurons) * max_size
        soma_y = np.random.rand(self.__num_neurons) * max_size

        soma_points =  [(soma_x[i], soma_y[i]) for i in range(self.__num_neurons)]

        synapse_dict = generate_synapses.create_synapses(soma_points)
        for pre_synaptic_neuron_index in synapse_dict.keys():
            syn = synapse(self.neurons[pre_synaptic_neuron_index])

            

        

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

        dt = 0.01
        self.neurons = []


        for i in range(self.__num_neurons):
            #neuron parameters, currently gk, gna, gleak, ek, ena, eleak, c, vthresh, vrest

            neuron_params_dict = parameters[i]
            resting_potential, action_thresh = neuron_params_dict['vrest'], neuron_params_dict['vthresh']

            neuron = neuron_models.hodgkin_huxley(action_thresh, resting_potential, dt=dt)
            neuron.set_params(neuron_params_dict)

            self.neurons.append(neuron)


    def update(self):
        pass
        #neuron gets updated
        #neuron synapse recieves neuron firing the following step
        #synapse adapts to this new v
        #synaptic conductance changes
        #update synaptic conductance
        #neurons get updates

import numpy as np
    
if __name__ == '__main__':

    network = neuron_network(10)

    #print(synapses)
