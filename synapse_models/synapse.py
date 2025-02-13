class tsodyks_markram_synapse():

    def __init__(self, pre_synaptic_neurons, post_synaptic_neurons, params, dt= 0.01):
        self.r, self.r_past, self.u, self.u_past, self.t = 1, 1, 0, 0, 0
        #
        self.dt = dt
        self.pre_synaptic_neurons = pre_synaptic_neurons
        self.post_synaptic_neurons = post_synaptic_neurons

        self.past_spike_times = [None for i in range(len(self.pre_synaptic_neurons))]
        self.is_active = [False for i in range(len(self.pre_synaptic_neurons))]

        self.setup_activation_params(params)
            

    def setup_activation_params(self, params):


        """
        params = {"gaba": {"tau_recovery": [0.5, 2], "tau_facilitation": [0.05, 0.2],"u_max":[0.05, 0.3], "u":[0.1], "e":[-70, -75], "alpha": [0.01, 0.05], "beta": [0.05, 0.5], "g_max": [0.1, 1]},
                   "ampa": {"tau_recovery": [0.2, 1], "tau_facilitation": [0.05, 0.5], "u_max": [0.1, 0.7], "u":[0.1], "e": [0, 0], "alpha": [0.01, 0.1], "beta": [0.1, 1], "g_max": [0.1, 1]}}
        """
        
        self.action_potential_thresholds = []
        for i in self.pre_synaptic_neurons:
            self.action_potential_thresholds.append(i.action_potential_threshold)

        #params = [tau_recvoery, tau_facilitation, max_utilization, max_conductance]


        self.tau_r = params["tau_recovery"][0]
        self.tau_f = params["tau_facilitation"][1]
        self.u_max = params["u_max"][1]
        self.u = params["u"][0]
        self.reversal_potential = params["e"][1]
        self.g_max = params["g_max"][1]
        self.g_syn = 0
        self.r = 1

        #tau and umax are inversely related 
        #facilitation dominated synapses are generally larger, which mean
        #so the larger the synapse, the more facilitatiion based it is
        #the more active a synapse the lower both tau_facilitate is and the lower tau_recovery
    
    #checks if each of the pre synaptic neurons is active and 
    #updates spike times of each of the pre synaptic neurons to reflect the recent spike.
    def update_spike_times(self):
        for i in range(len(self.pre_synaptic_neurons)):
            neuron = self.pre_synaptic_neurons[i]
            #when the neuron is registered as having a spike and has returned to resting
            #the neuron will undergo a refractory period 
            if self.is_active[i] == True and neuron.v <= neuron.resting_potential:
                self.is_active[i] = False
            #when the neuron is registered as inactive and has achieved
            #a spike set the new past spike time to the current time and
            #re-register the neuron as active
            if neuron.v >= neuron.action_potential_threshold and not self.is_active[i] == True:
                self.is_active[i] = True
                self.past_spike_times[i] = self.t
            
    def update(self):
        self.update_spike_times()
        dirac_sum = 0
        has_past_spike = False
        for i in range(len(self.pre_synaptic_neurons)):
            #if this pre synaptic neuron is active
            if self.is_active[i]:
                if self.t == self.past_spike_times[i]:
                    print("\nspike")
                    has_past_spike = True
                    #for dirac equation estimation
                    self.r = self.r_past - (self.u_past * self.r_past)

                    self.u = self.u_past + self.u_max * (1 - self.u_past)



        if not has_past_spike:
            drdt = (1 - self.r) / self.tau_r
            dudt = (- self.u / self.tau_f) 

            self.r += drdt * self.dt
            self.u += dudt * self.dt


        self.r_past = self.r
        self.u_past = self.u

        self.g_syn = self.g_max * self.r * self.u

        currents = {}
        for i in range(len(self.post_synaptic_neurons)):
            neuron = self.post_synaptic_neurons[i]
            i_syn = self.g_syn * (neuron.v - self.reversal_potential)
            neuron.i_syn += i_syn


        self.t += self.dt


class synapse_hh():
    post_synaptic_neurons = []
    neurotransmitter_release_time= 0
    k = 10
    def __init__(self, pre_synaptic_neuron):
        #0 = inhibitory, 1 = excitory, (gaba/ampa)
        #params[i] = [[min, max synpatic conuctance], decay time constant, rise time constant, reversal potential ]
        #
        synapse_params = [ [(0.1, 1.0), 1.0, 10.0, -70],
                            [(0.1, 1.0), 0.2, 2.0, 0 ]]
        self.pre_synaptic_neruon = pre_synaptic_neuron

        self.tau_decay, self.tau_rise = synapse_params[1], synapse_params[2]
        #for now g_max is just 1, but will eventually be some value in the range given

        self.neurotransmitter_release_time = None
        
        self.g_max = [synapse_params[0][1]]

    def __init__(self, pre_synaptic_neuron):
        self.pre_synaptic_neruon = pre_synaptic_neuron

    def add_post_synaptic_neuron(self, post_synaptic_neuron):
        self.post_synaptic_neurons.append(post_synaptic_neuron)
    
    def add_post_synaptic_neurons(self, post_synaptic_neurons:list):
        for i in post_synaptic_neurons:
            self.add_post_synaptic_neuron(i)

    def check_for_spike(self):
        from numpy import exp
        neuron = self.pre_synaptic_neruon
        #for the time being neurotransmitter release will only happen at the spiking
        #threshold, ***add graded potential neurotransmitter release***

        if self.neurotransmitter_release_time != None:
            self.prev_spike_time = self.neurotransmitter_release_time * (neuron.v <= neuron.action_potential_threshold)

        self.neurotransmitter_release_time += neuron.t * (neuron.v > neuron.action_potential_threshold)
        

    def update(self, t):
        import math

        decay = math.e ** - ((self.neurotransmitter_release_time - t) / self.tau_decay)
        rise = - math.e ** - ((self.neurotransmitter_release_time - t) / self.tau_rise)

        self.g_syn = self.g_max * (decay + rise)

        for i in self.post_synaptic_neurons:
            i.i_syn += self.g_syn * (i.v - self.e)
  

