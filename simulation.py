class simulation():
    default_neural_params = {'c': 1, "gk": 36.004631953926285, "gna": 119.91561331101256, "gleak": 0.2997385592373893, "ek": -82.03623253390188, "ena": 45.028284147345595, "eleak": -59.35717906013866, "c": 0.9998470285990088, "vrest": -59.35717564093531, "vthresh": 15.119047441363206}
    #holders for neuron data

    #{"gaba": {"tau_recovery": [0.5, 2], "tau_facilitation": [0.05, 0.2],"u_max":[0.05, 0.3], "u":[0.1], "e":[-70, -75], "alpha": [0.01, 0.05], "beta": [0.05, 0.5], "g_max": [0.1, 1]},
    # "ampa": {"tau_recovery": [0.2, 1], "tau_facilitation": [0.05, 0.5], "u_max": [0.1, 0.7], "u":[0.1], "e": [0, 0], "alpha": [0.01, 0.1], "beta": [0.1, 1], "g_max": [0.1, 1]}}
    ampa_synapse_params = {"tau_recovery": [0.2, 1], "tau_facilitation": [0.05, 0.5], "u_max": [0.7, 0.1], "u":[0.1], "e": [0, 0], "g_max": [0.3, 1]}
    gaba_synapse_params = {"tau_recovery": [0.5, 2], "tau_facilitation": [0.05, 0.2],"u_max":[0.3, 0.5], "u":[0.1], "e":[-75, -70], "g_max": [0.3, 1]}
    
    def __init__(self, num_neurons:int, dt:float):
        self.setup_sim(num_neurons, dt)
    def setup_sim(self, num_neurons, dt):
        self.num_neurons = num_neurons

        self.neuron_models, self.synapses, self.input_currents, self.membrane_potentials = [], [], [], []
        self.t = 0

        self.inputs = []
        self.times = []
        self.synapse_gs = []
        self.largest_synapse_size = 0

        
        self.vs = [[] for i in range(num_neurons)]
        self.dt = dt

        self.input_current_functions = []
        self.input_currents = []

        self.setup_models()


        #create each synapse


    def interpolate(self, variable, min_val, max_val):
        return (variable * (max_val-min_val)) + min_val
    def __generate_activity_params(self, type:str, activation_modifier=1.0):
        synapse_param_ranges = self.ampa_synapse_params
        synapse_params = {}

        if type == "gaba":
            synapse_params = self.gaba_synapse_params


        #tauf is proportional to tau r, but inversely to umax
        for param_name in synapse_param_ranges.keys():
            param_range = synapse_param_ranges[param_name]
            
            synapse_params[param_name] = self.interpolate(activation_modifier, param_range[0], param_range[1])


    def create_synapse(self, pre_synaptic_neuron_indexes:list, post_synaptic_neuron_indexes:list, synapse_params = {}):
        from synapse_models.synapse import tsodyks_markram_synapse
        #activation multiplier should proportional to (number of in and out connections)/(largest synapse size)
        activation_modifier = (len(pre_synaptic_neuron_indexes) + len(post_synaptic_neuron_indexes)) / self.num_neurons
        if not synapse_params.keys():
            synapse_params = self.ampa_synapse_params

        size = len(pre_synaptic_neuron_indexes) + len(post_synaptic_neuron_indexes)
        if size > self.largest_synapse_size:
            self.largest_synapse_size = size

        

        #synapse models require neuron object
        pre_synaptic_neurons = []
        post_synaptic_neurons = []

        for i in pre_synaptic_neuron_indexes:
            pre_synaptic_neurons.append(self.neuron_models[i])
    
        for i in post_synaptic_neuron_indexes:
            post_synaptic_neurons.append(self.neuron_models[i])

        syn = tsodyks_markram_synapse(pre_synaptic_neurons, post_synaptic_neurons, synapse_params, self.dt)

        self.synapse_gs.append([])
        self.synapses.append(syn)
        
    def create_neuron(self, params = {}):
        from neuron_models import hodgkin_huxley

        model = hodgkin_huxley(params, self.dt)

        model.set_no_current()

        self.neuron_models.append(model)
        self.input_currents.append([])

    def setup_models(self, params=[]):
        from neuron_models import hodgkin_huxley
        
        if self.num_neurons == 0:
            raise Warning("Unregistered datapoint \'num_neurons\': {}". format(self.num_neurons))
        
        if params == []:
            params.append(self.default_neural_params)

        print(params)
        for i in range(self.num_neurons):
            
            curr_params_dict = params[i % len(params)]

            self.create_neuron(curr_params_dict)
        

    def iterate(self, num_steps = 1):
        for i in range(num_steps):
            for j in range(len(self.neuron_models)):
                self.neuron_models[j].update()
            
                self.input_currents[j].append(self.neuron_models[j].input_current)
                
                self.vs[j].append(self.neuron_models[j].v)

            for j in range(len(self.synapses)):
                self.synapses[j].update()
                self.synapse_gs[j].append(self.synapses[j].g_syn)

            
            self.times.append(self.dt + self.t)
            self.t+=self.dt

    def clear(self, num_steps):
        #clear each neuron of any current for a fixed num steps
        for i in self.neuron_models:
            past_current_func = i.input_current_func
            
            i.set_no_current()
            self.iterate(num_steps)
            i.input_current_func = past_current_func


    def __setup_old_neuron(self, states, params, position, input_current_func, t, dt):
                 
        from neuron_models import hodgkin_huxley
            #standard setup
        neuron = hodgkin_huxley(params, dt)

        

        #load existing states
        neuron.t = t

        neuron.v = states["v"]
        
        n, alpha_n, beta_n = states["n"]
        m, alpha_m, beta_m = states["m"]
        h, alpha_h, beta_h = states["h"]

        x, y = position

        neuron.n_gate.state = n
        neuron.n_gate.alpha = alpha_n
        neuron.n_gate.beta = beta_n

        neuron.m_gate.state = m
        neuron.m_gate.alpha = alpha_m
        neuron.m_gate.beta = beta_m

        neuron.h_gate.state = h
        neuron.h_gate.alpha = alpha_h
        neuron.h_gate.beta = beta_h

        neuron.input_current_func = input_current_func
        
        neuron.x, neuron.y = x, y

        self.neurons_models.append(neuron)
        self.vs.append([])


    def setup_old_instance(self, neuron_models_params:list, neuron_model_states:list, neuron_models_positions:list, input_currents:list, synapses_params, synapses_states, synapses_postions, t, dt):
        #create each neuron

        self.setup_sim(0, dt)

        for i in range(len(neuron_models_params)):
           
            self.__setup_old_neuron(neuron_model_states[i], neuron_models_params[i], neuron_models_positions[i], t, dt)
        

