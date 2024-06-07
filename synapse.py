class synapse():
    post_synaptic_neurons = []
    neurotransmitter_release_time= 0
    def __init__(self, pre_synaptic_neuron):
        #0 = inhibitory, 1 = excitory
        #params[i] = [[min, max synpatic conuctance], decay time constant, rise time constant, reversal potential ]
        #
        synapse_params = [[0.1, 1.0], 1.0, 10.0, -70]
        self.pre_synaptic_neruon = pre_synaptic_neuron

        self.tau_decay, self.tau_rise = synapse_params[1], synapse_params[2]
        #for now g_max is just 1, but will eventually be some value in the range given

        self.neurotransmitter_release_time = None
        
        self.g_max = [synapse_params[0][1]]

    def __init__(self, pre_synaptic_neuron):
        self.pre_synaptic_neruon = pre_synaptic_neuron

    def add_post_synaptic_neuron(self, input_neuron):
        self.post_synaptic_neurons.append(synapse(input_neuron))


    def check_for_spike(self):
        neuron = self.pre_synaptic_neruon

        #for the time being neurotransmitter release will only happen at the spiking
        #threshold, ***add graded potential neurotransmitter release***

        if self.neurotransmitter_release_time != None:
            self.prev_spike_time = self.neurotransmitter_release_time * (neuron.v <= neuron.activation_potential_threshold)
        self.neurotransmitter_release_time += neuron.t * (neuron.v > neuron.activation_potential_threshold)
        

    def update(self, t):
        import math

        decay = math.e ** - ((self.neurotransmitter_release_time - t) / self.tau_decay)
        rise = - math.e ** - ((self.neurotransmitter_release_time - t) / self.tau_rise)

        self.g_syn = self.g_max * (decay + rise)

        for i in self.post_synaptic_neurons:
            i.i_syn += self.g_syn * (i.v - self.e)

