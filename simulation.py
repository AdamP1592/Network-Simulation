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

        if not synapse_params.keys():
            synapse_params = self.ampa_synapse_params

        size = len(pre_synaptic_neuron_indexes) + len(post_synaptic_neuron_indexes)
        if size > self.largest_synapse_size:
            self.largest_synapse_size = size

        #synapse models require neuron object
        pre_synaptic_neurons, post_synaptic_neurons = self.synaptic_connection_dict_builder(pre_synaptic_neuron_indexes, post_synaptic_neuron_indexes)

        syn = tsodyks_markram_synapse(pre_synaptic_neurons, post_synaptic_neurons, synapse_params, self.dt)

        self.synapse_gs.append([])
        self.synapses.append(syn)
        
    def create_neuron(self, params = {}):
        from neuron_models.neuron_models import hodgkin_huxley

        model = hodgkin_huxley(params, self.dt)

        model.set_no_current()

        self.neuron_models.append(model)
        self.input_currents.append([])

    def setup_models(self, params=[]):
        import warnings
        if self.num_neurons == 0:
            warnings.warn("Unregistered datapoint \'num_neurons\': {}". format(self.num_neurons))
        
        if params == []:
            params.append(self.default_neural_params)

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
                 
        from neuron_models.neuron_models import hodgkin_huxley
            #standard setup
        neuron = hodgkin_huxley(params, dt)

        #load existing state
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

        self.neuron_models.append(neuron)
        self.vs.append([])

    def generate_model_dict(self):
        neurons = {}
        synapses = {}
        network = {}
        for i in range(len(self.neuron_models)):
            neuron_params = self.neuron_models[i].get_params()
            neurons[i] = neuron_params
        
        for i in range(len(self.synapses)):
            synapses[i] = self.synapses[i].get_params()

        network = {"t": self.t, "dt":self.dt, "num_neurons": self.num_neurons}

        return {"neurons": neurons, "synapses":synapses, "network": network}
    
    def store_model(self):
        import json
        with open("network.json", "w") as f:
            f.write(self.generate_model_dict())

    def __setup_old_neuron_from_dict(self, neuron_params, neuron_gate_params, t, dt):
        from neuron_models.neuron_models import hodgkin_huxley
        #standard setup

        neuron = hodgkin_huxley(neuron_params, dt)

        #load existing states
        neuron.t = t

        neuron.v = neuron_params["v"]

        neuron.n_gate.state = neuron_gate_params["n_state"]
        neuron.n_gate.alpha = neuron_gate_params["n_alpha"]
        neuron.n_gate.beta = neuron_gate_params["n_beta"]

        neuron.m_gate.state = neuron_gate_params["m_state"]
        neuron.m_gate.alpha = neuron_gate_params["m_alpha"]
        neuron.m_gate.beta = neuron_gate_params["m_beta"]

        neuron.h_gate.state = neuron_gate_params["h_state"]
        neuron.h_gate.alpha = neuron_gate_params["h_alpha"]
        neuron.h_gate.beta = neuron_gate_params["h_beta"]
        
        neuron.x, neuron.y = neuron_params["x"], neuron_params["y"]

        neuron.set_no_current()
        self.input_currents.append([])

        self.neuron_models.append(neuron)
        self.vs.append([])

    def synaptic_connection_dict_builder(self, pre_synaptic_indicies, post_synaptic_indicies):
        pre_synaptic_neurons = {}
        post_synaptic_neurons = {}

        for i in pre_synaptic_indicies:
            pre_synaptic_neurons[i] = self.neuron_models[i]
    
        for i in post_synaptic_indicies:
            post_synaptic_neurons[i] = self.neuron_models[i]

        return [pre_synaptic_neurons, post_synaptic_neurons]
    def setup_old_instance_from_dict(self, model_dict):

        neural_params = model_dict["neurons"]
        synapse_params = model_dict["synapses"]
        network_params = model_dict["network"]

        dt = network_params["dt"]
        t = network_params["t"]

        self.t = t
        self.dt = dt

        self.setup_sim(0, dt)
        
        is_json = False
        for i in range(network_params["num_neurons"]):
            #catch potential json where all keys are strings
            selected_params = {}
            try:
                selected_params = neural_params[i]
            except:
                is_json = True

            if(is_json):
                i = str(i)

            selected_params = neural_params[i]

            neuron_params = selected_params["neuron_params"]
            gate_params = selected_params["gating_params"]

            self.__setup_old_neuron_from_dict(neuron_params, gate_params, t, dt)
            self.num_neurons+=1

        for syn_ind in synapse_params:
            current_syn = synapse_params[syn_ind]

            #split syn into each part
            syn_state = current_syn["state"]
            syn_params = current_syn["params"]
            syn_connections = current_syn["connections"]

            #connections setup
            pre_cons = syn_connections["pre"]
            post_cons = syn_connections["post"]

            self.create_synapse(pre_cons, post_cons, syn_params)

            self.synapses[-1].set_state(syn_state)
            
    def __str__(self):
        sim_str = ""

        for i in self.neuron_models:
            sim_str += str(i) + "\n\n"
        for i in self.synapses:
            sim_str += str(i) + "\n\n"
        
        return sim_str
