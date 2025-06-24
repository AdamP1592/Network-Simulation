from synapse_models.synapse import tsodyks_markram_synapse
import synapse_models.synapse_generator as synapse_generator


class simulation:
    """
    A simulation engine for a network of Hodgkin-Huxley neurons with dynamic synapses.
    
    Attributes:
        default_neural_params (dict): Default parameters for neuron models.
        ampa_synapse_params (dict): Parameter ranges for AMPA synapses.
        gaba_synapse_params (dict): Parameter ranges for GABA synapses.
        synapse_switch (list): List containing AMPA and GABA synapse parameters.
    """
    default_neural_params = {
        "c": 1.0,          # Membrane capacitance (uF/cm^2)
        "gna": 120.0,      # Max sodium conductance (mS/cm^2)
        "gk": 36.0,        # Max potassium conductance (mS/cm^2)
        "gleak": 0.3,      # Leak conductance (mS/cm^2)
        "ena": 50.0,       # Sodium reversal potential (mV)
        "ek": -77.0,       # Potassium reversal potential (mV)
        "eleak": -54.387,  # Leak reversal potential (mV)
        "vrest": -65,      # Resting potential (mV)
        "vthresh": -55     # Threshold potential (mV)
    }
    ## grabbed from excitory pyrimidal neurons rather than corticospinal neurons
    glutamate_synapse_params = {
        "tau_recovery": [0.05, 0.85],
        "tau_facilitation": [0.05, 0.8],
        "u_min": [0.2, 0.5],
        "u": [0],
        "e": [0, 0],
        "g_max": [0.1, 5.0],
        "tau_g": [0.1, 5.0]
    }
    # not used in this simulation
    gaba_synapse_params = {
        "tau_recovery": [0.5, 2],
        "tau_facilitation": [0.05, 0.2],
        "u_min": [0.05, 0.2],
        "u": [0],
        "e": [-75, -70],
        "g_max": [0.3, 1],
        "tau_g": [0.1, 5.0]
    }
    synapse_switch = [glutamate_synapse_params]

    def __init__(self, num_neurons: int, dt: float):
        """
        Initializes the simulation with a specified number of neurons and time step dt.
        
        :param num_neurons: Number of neurons in the simulation.
        :param dt: Time step for simulation updates.
        """
        self.__num_stored_values = int(100 / dt)
        self.setup_sim(num_neurons, dt)
    
    # -------------------------------------------------------------------------
    # Setup Functions
    # -------------------------------------------------------------------------
    def setup_vs(self) -> None:
        """Initializes a voltage history list for a neuron."""
        self.vs.append([0] * self.__num_stored_values)
    
    def setup_input_currents(self) -> None:
        """Initializes an input current history list for a neuron."""
        self.input_currents.append([0] * self.__num_stored_values)
    
    def interpolate(self, variable: float, min_val: float, max_val: float) -> float:
        """
        Performs linear interpolation.
        
        :param variable: The value to interpolate (typically in [0,1]).
        :param min_val: Minimum output value.
        :param max_val: Maximum output value.
        :return: Interpolated value.
        """
        return (variable * (max_val - min_val)) + min_val
    
    def __generate_activity_params(self, syn_type: str, activation_modifier: float = 1.0) -> dict:
        """
        Generates synaptic activity parameters based on an activation modifier.
        
        :param syn_type: Synapse type ('gaba' uses GABA parameters, otherwise AMPA).
        :param activation_modifier: Modifier scaling the activation.
        :return: A dictionary of synaptic parameters.
        """
        # Default to AMPA parameters unless type is 'gaba'
        param_ranges = self.ampa_synapse_params if syn_type != "gaba" else self.gaba_synapse_params
        syn_params = {}
        for param_name, param_range in param_ranges.items():
            syn_params[param_name] = self.interpolate(activation_modifier, param_range[0], param_range[1])
        return syn_params

    def setup_sim(self, num_neurons: int, dt: float) -> None:
        """
        Sets up the simulation environment: initializes neuron models, synapses, and tracking arrays.
        
        :param num_neurons: The number of neurons to create.
        :param dt: The simulation time step.
        """
        self.num_neurons = num_neurons
        self.neuron_models = []
        self.synapses = []
        self.input_currents = []
        self.membrane_potentials = []
        self.t = 0
        self.inputs = []
        self.times = []
        self.synapse_gs = []
        self.largest_synapse_size = 0
        self.vs = []
        self.sim_index = 0
        self.dt = dt
        self.input_current_functions = []
        # Reinitialize input currents if needed.
        self.input_currents = []
        self.setup_models()
    
    def setup_models(self, params: list = []) -> None:
        """
        Initializes neuron models for the simulation.
        
        If no custom parameter list is provided, uses default parameters.
        
        :param params: (Optional) List of parameter dictionaries for neurons.
        """
        import warnings
        if self.num_neurons == 0:
            warnings.warn(f"Unregistered num_neurons: {self.num_neurons}")
        if not params:
            params.append(self.default_neural_params)
        for i in range(self.num_neurons):
            curr_params_dict = params[i % len(params)]
            self.create_neuron(curr_params_dict)
    
    # -------------------------------------------------------------------------
    # Simulation Iteration and Model Updates
    # -------------------------------------------------------------------------
    def iterate(self, num_steps: int = 1) -> dict:
        """
        Advances the simulation for a given number of time steps.
        
        Records voltage, input currents, and synaptic inputs for each neuron.
        
        :param num_steps: Number of simulation steps to run.
        :return: A dictionary with keys "vs", "input_currents", and "synaptic_inputs".
        """
        sample_t = 0.1  # Sampling interval in seconds.
        num_steps_per_sample = sample_t / self.dt
        
        # Initialize data recording arrays.
        vs = [[] for _ in range(self.num_neurons)]
        input_currents = [[] for _ in range(self.num_neurons)]
        synaptic_inputs = [[] for _ in range(self.num_neurons)]
        
        for i in range(num_steps):
            # Update each neuron.
            for j in range(len(self.neuron_models)):
                if i % num_steps_per_sample == 0:
                    vs[j].append([self.t, self.neuron_models[j].v])
                    input_currents[j].append([self.t, self.neuron_models[j].input_current])
                    synaptic_inputs[j].append([self.t, -1 * self.neuron_models[j].i_syn])
                    
                self.neuron_models[j].update()
            # Update each synapse.
            for j in range(len(self.synapses)):
                self.synapses[j].update()
                self.synapse_gs[j].append(self.synapses[j].g_syn)
            
            self.times.append(self.t + self.dt)
            self.t += self.dt
            self.sim_index += 1
        
        return {"vs": vs, "input_currents": input_currents, "synaptic_inputs": synaptic_inputs}
    
    def create_synapse(self, pre_synaptic_neuron_indexes: list, post_synaptic_neuron_indexes: list, synapse_params: dict = {}) -> None:
        import sys
        """
        Creates a synapse between specified pre- and post-synaptic neurons.
        
        If no synapse parameters are provided, one set is chosen randomly.
        
        :param pre_synaptic_neuron_indexes: List of indices for pre-synaptic neurons.
        :param post_synaptic_neuron_indexes: List of indices for post-synaptic neurons.
        :param synapse_params: (Optional) Dictionary of synapse parameters.
        """
        import random
        synapse_params = self.synapse_switch[0]

        size = len(pre_synaptic_neuron_indexes) + len(post_synaptic_neuron_indexes)
        if size > self.largest_synapse_size:
            self.largest_synapse_size = size
        
        pre_synaptic_neurons, post_synaptic_neurons = self.synaptic_connection_dict_builder(pre_synaptic_neuron_indexes, post_synaptic_neuron_indexes)
        syn = tsodyks_markram_synapse(pre_synaptic_neurons, post_synaptic_neurons, synapse_params, self.dt)
        self.synapse_gs.append([])
        self.synapses.append(syn)
    
    def create_neuron(self, params: dict = {}) -> None:
        """
        Creates a neuron with the given parameters and adds it to the simulation.
        
        :param params: (Optional) A dictionary of neuron parameters.
        """
        from neuron_models.neuron_models import hodgkin_huxley
        model = hodgkin_huxley(params, self.dt)
        model.set_no_current()
        self.neuron_models.append(model)
        self.setup_vs()
        self.setup_input_currents()
    
    def clear(self, num_steps: int) -> None:
        """
        Clears the current input for each neuron for a fixed number of steps.
        
        Temporarily sets current to zero, iterates for the given number of steps,
        and then restores the original input current function.
        
        :param num_steps: Number of steps to clear the input.
        """
        for neuron in self.neuron_models:
            past_current_func = neuron.input_current_func
            neuron.set_no_current()
            self.iterate(num_steps)
            neuron.input_current_func = past_current_func
    
    # -------------------------------------------------------------------------
    # Restoration Functions
    # -------------------------------------------------------------------------
    def __setup_old_neuron(self, states: dict, params: dict, position: tuple, input_current_func, t: float, dt: float) -> None:
        """
        Sets up a neuron with previous state information.
        
        :param states: Dictionary containing state variables (e.g., voltage, gating variables).
        :param params: Dictionary of neuron parameters.
        :param position: Tuple (x, y) for neuron position.
        :param input_current_func: The input current function.
        :param t: Simulation time.
        :param dt: Time step.
        """
        from neuron_models.neuron_models import hodgkin_huxley
        neuron = hodgkin_huxley(params, dt)
        neuron.t = t
        neuron.v = states["v"]
        
        # Unpack gating variables.
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
        self.setup_vs()
        self.setup_input_currents()
    
    def __setup_old_neuron_from_dict(self, neuron_params: dict, neuron_gate_params: dict, t: float, dt: float) -> None:
        """
        Restores a neuron's state from dictionaries containing its parameters and gating variables.
        
        :param neuron_params: Dictionary containing neuron parameters, including voltage and position.
        :param neuron_gate_params: Dictionary containing gating parameters for the neuron.
        :param t: Simulation time.
        :param dt: Time step.
        """
        from neuron_models.neuron_models import hodgkin_huxley
        neuron = hodgkin_huxley(neuron_params, dt)
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
        current_type = neuron_params["current"][0]
        current_params = neuron_params["current"][1]
        
        match current_type:
            case "sin_current":
                neuron.set_sin_current(current_params[0], current_params[1])
            case "square_current":
                neuron.set_square_current(current_params[0], current_params[1])
                
            case "constant_current":
                neuron.set_const_current(current_params[0])
            case _:
                neuron.set_no_current()

        self.input_currents.append([])
        self.neuron_models.append(neuron)
        self.setup_vs()
        self.setup_input_currents()
    
    def setup_old_instance_from_dict(self, model_dict: dict) -> None:
        """
        Restores the simulation state from a model dictionary.
        
        This function reinitializes the simulation instance and then restores
        neurons and synapses from the provided dictionary.
        
        :param model_dict: Dictionary containing the simulation state.
        """
        neural_params = model_dict["neurons"]
        synapse_params = model_dict["synapses"]
        network_params = model_dict["network"]

        dt = network_params["dt"]
        t = network_params["t"]

        self.setup_sim(0, dt)
        self.t = t
       

        # Initialize the simulation with zero neurons; models will be added below.
        
        
        is_json = False
        for i in range(network_params["num_neurons"]):
            selected_params = {}
            try:
                selected_params = neural_params[i]
            except Exception:
                is_json = True

            if is_json:
                i = str(i)
            selected_params = neural_params[i]
            neuron_params = selected_params["params"]
            gate_params = selected_params["gating_params"]

            self.__setup_old_neuron_from_dict(neuron_params, gate_params, self.t, dt)
            self.num_neurons += 1

        for syn_ind in synapse_params:
            current_syn = synapse_params[syn_ind]
            syn_state = current_syn["state"]
            syn_params = current_syn["params"]
            syn_connections = current_syn["connections"]

            pre_con_indexes = syn_connections["pre"]
            post_con_indexes = syn_connections["post"]

            self.create_synapse(pre_con_indexes, post_con_indexes)

            self.synapses[-1].setup_old_activation_params(current_syn)
    
    # -------------------------------------------------------------------------
    # Output Functions
    # -------------------------------------------------------------------------
    def generate_model_dict(self) -> dict:
        """
        Generates a dictionary representation of the current simulation state.
        
        :return: A dictionary with keys 'neurons', 'synapses', and 'network'.
        """
        neurons = {}
        synapses = {}
        for i in range(len(self.neuron_models)):
            neuron_params = self.neuron_models[i].get_params()
            neurons[i] = neuron_params
            
        
        for i in range(len(self.synapses)):
            synapses[i] = self.synapses[i].get_params()
        
        network = {"t": self.t, "dt": self.dt, "num_neurons": self.num_neurons}
        return {"neurons": neurons, "synapses": synapses, "network": network}
    
    def store_model(self) -> None:
        """
        Stores the current simulation state to a JSON file.
        """
        import json
        with open("network.json", "w") as f:
            f.write(json.dumps(self.generate_model_dict()))
    
    def synaptic_connection_dict_builder(self, pre_synaptic_indices: list, post_synaptic_indices: list) -> list:
        """
        Builds dictionaries mapping neuron indices to neuron objects for synaptic connections.
        
        :param pre_synaptic_indices: List of pre-synaptic neuron indices.
        :param post_synaptic_indices: List of post-synaptic neuron indices.
        :return: A list containing two dictionaries: [pre_synaptic_neurons, post_synaptic_neurons].
        """
        pre_synaptic_neurons = {}
        post_synaptic_neurons = {}

        for i in pre_synaptic_indices:
            pre_synaptic_neurons[i] = self.neuron_models[i]

        for i in post_synaptic_indices:
            post_synaptic_neurons[i] = self.neuron_models[i]

        return [pre_synaptic_neurons, post_synaptic_neurons]
    
    def __str__(self) -> str:
        """
        Returns a string representation of the simulation state.
        
        :return: A string containing the simulation state.
        """
        return str(self.generate_model_dict())
