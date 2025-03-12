import math

class gate:
    """
    Represents an ion channel gate with activation/inactivation dynamics.
    """
    def __init__(self):
        self.alpha = 0
        self.beta = 0
        self.state = 0

    def update(self, dt):
        """
        Updates the gate state based on the rate constants and time step.
        
        :param dt: Time step.
        """
        alpha_state = self.alpha * (1 - self.state)
        beta_state = self.beta * self.state
        self.state += dt * (alpha_state - beta_state)

    def set_infinite_state(self):
        """
        Sets the gate state to its steady-state value (infinite time).
        """
        self.state = self.alpha / (self.alpha + self.beta)


class neuron:
    """
    Base class for a neuron.
    """
    def __init__(self):
        pass

    def set_vars(self, vars=[]):
        """
        Placeholder for setting neuron variables.
        :param vars: List of variables.
        """
        pass

    def update(self, voltage_in=0, time=0):
        """
        Placeholder for updating the neuron state.
        
        :param voltage_in: Input voltage (if any).
        :param time: The current time.
        """
        pass


class hodgkin_huxley(neuron):
    """
    Implements a Hodgkin-Huxley neuron model with dynamic gating.
    """
    def __init__(self, params: dict, dt=0.0001):
        """
        Initializes the Hodgkin-Huxley neuron.
        
        :param params: Dictionary of neural parameters.
        :param dt: Time step (seconds).
        """
        # Position of the neuron (soma)
        self.x, self.y = 0, 0

        # Initialize gating variables for potassium (n), sodium (m), and inactivation (h)
        self.n_gate = gate()
        self.m_gate = gate()
        self.h_gate = gate()

        self.dt = dt

        # Initialize ionic currents.
        self.i_k = 0
        self.i_na = 0
        self.i_leak = 0
        self.i_syn = 0

        # To store derivatives (for analysis/plotting)
        self.derivatives = []

        # Setup input current function. Default is no current.
        self.input_current_func = self.set_no_current()
        self.input_current = 0

        # Timing parameter.
        self.t = 0

        # Setup parameters from dictionary.
        self.set_params(params)
        # Update gating rate constants based on initial membrane potential.
        self.update_gates(self.v)
        # Set gating variables to their steady state.
        self.gating_varibles_setup()

    # ----------------- Squid Axon Gating Functions (unused) -----------------
    """
    # Squid axon gating functions (unused):
    def alpha_n(self, v):
        return 0.01 * ((10 - v) / (math.exp((10 - v) / 10) - 1))
    
    def beta_n(self, v):
        return 0.125 * (math.exp(-v / 80.0))
    
    def alpha_m(self, v):
        return 0.1*((25 - v) / (math.exp((25 - v) / 10.0) - 1))
    
    def beta_m(self, v):
        return 4.0 * (math.exp(-v/18.0))
    
    def alpha_h(self, v):
        return 0.07 * (math.exp(- v / 20.0))
    
    def beta_h(self, v):
        return 1.0/(1.0 + (math.exp((30.0 - v) / 10.0)))
    """

    # ----------------- Gating Functions -----------------
    def alpha_m(self, v):
        return 0.1 * (v + 40) / (1 - math.exp(-(v + 40) / 10))

    def beta_m(self, v):
        return 4.0 * math.exp(-(v + 65) / 18)

    def alpha_h(self, v):
        return 0.07 * math.exp(-(v + 65) / 20)

    def beta_h(self, v):
        return 1 / (1 + math.exp(-(v + 35) / 10))
    
    # Sodium (n) gating functions.
    def alpha_n(self, v):
        return 0.01 * (v + 55) / (1 - math.exp(-(v + 55) / 10))

    def beta_n(self, v):
        return 0.125 * math.exp(-(v + 65) / 80)
    
    def gating_varibles_setup(self):
        """
        Sets the gating variables (n, m, h) to their steady-state values.
        """
        self.n_gate.set_infinite_state()
        self.m_gate.set_infinite_state()
        self.h_gate.set_infinite_state()

    def update_gate_voltages(self, dt):
        """
        Updates the state of each gate using the current rate constants.
        
        :param dt: Time step.
        """
        self.n_gate.update(dt)
        self.m_gate.update(dt)
        self.h_gate.update(dt)

    def update_gates(self, v):
        """
        Updates the rate constants for each gate based on the current membrane potential.
        
        :param v: Membrane potential.
        """
        self.n_gate.alpha = self.alpha_n(v)
        self.n_gate.beta = self.beta_n(v)

        self.m_gate.alpha = self.alpha_m(v)
        self.m_gate.beta = self.beta_m(v)

        self.h_gate.alpha = self.alpha_h(v)
        self.h_gate.beta = self.beta_h(v)

    def runge_cutta_update(self):
        """
        Placeholder for a 4th order Runge-Kutta update of the membrane potential.
        """
        n = 4
        n_gates = [self.n_gate for i in range(n)]
        m_gates = [self.m_gate for i in range(n)]
        h_gates = [self.h_gate for i in range(n)]
        vs = [self.v for i in range(n)]
        step_size = self.dt / 4
        for i in range(n):
            pass  # Implementation placeholder.
            
    def update_v(self):
        """
        Updates the membrane potential (v) using ionic currents and the input current.
        """
        # Update the input current from the current function.
        self.input_current = self.input_current_func(self.t)
        # Calculate individual ionic currents.
        self.i_k = self.gK * (self.n_gate.state ** 4) * (self.v - self.eK)
        self.i_na = self.gNa * (self.m_gate.state ** 3) * self.h_gate.state * (self.v - self.eNa)
        self.i_leak = self.gLeak * (self.v - self.eLeak)
    
        # Sum currents: input - ionic currents and synaptic input.
        total_current = self.input_current - self.i_k - self.i_na - self.i_leak - self.i_syn
        dvdt = total_current / self.membrane_cap

        self.derivatives.append(dvdt)
        self.v += dvdt * self.dt
        self.t += self.dt

    def update(self):
        """
        Updates the neuron state:
          1. Update gating rate constants based on current voltage.
          2. Update membrane potential.
          3. Update gating variable states.
          4. Reset synaptic current.
        """
        self.update_gates(self.v)
        self.update_v()
        self.update_gate_voltages(self.dt)
        self.i_syn = 0

    # ----------------- Parameter Handling -----------------
    def set_params(self, params: dict):
        """
        Sets neural parameters from a dictionary.
        
        Expected keys: 'gk', 'gna', 'gleak', 'ek', 'ena', 'eleak', 'vrest', 'vthresh', 'c', 
        and optionally 'v'.
        
        :param params: Dictionary of neuron parameters.
        """
        self.gK = params['gk']
        self.gNa = params['gna']
        self.gLeak = params['gleak']

        self.eK = params['ek']
        self.eNa = params['ena']
        self.eLeak = params['eleak']

        self.resting_potential = params['vrest']
        self.action_potential_threshold = params['vthresh']
        self.input_current = 0

        try:
            self.v = params["v"]
        except KeyError:
            self.v = params["vrest"]

        self.membrane_cap = params['c']

    def set_old_params(self, neuron_params: dict, gate_params: dict, dt):
        """
        Sets the neuron's parameters from stored values.
        
        :param neuron_params: Dictionary containing neuron parameters (including x, y).
        :param gate_params: Dictionary containing gating parameters.
        :param dt: Time step.
        """
        self.set_params(neuron_params)
        self.x = neuron_params["x"]
        self.y = neuron_params["y"]
        self.dt = dt

    def get_params(self) -> dict:
        """
        Generates a dictionary representing the neuron's current state.
        
        Includes neural parameters and gating variable states.
        
        :return: Dictionary with keys 'params' and 'gating_params'.
        """
        params = {}
        neural_params = {}
        gating_params = {}
        gating_variables = {'n': self.n_gate, 'm': self.m_gate, 'h': self.h_gate}

        neural_params['gk'] = self.gK 
        neural_params['gna'] = self.gNa 
        neural_params['gleak'] = self.gLeak
        neural_params['ek'] = self.eK
        neural_params['ena'] = self.eNa
        neural_params['eleak'] = self.eLeak
        neural_params['vrest'] = self.resting_potential
        neural_params['vthresh'] = self.action_potential_threshold
        neural_params["v"] = self.v
        neural_params['c'] = self.membrane_cap
        neural_params["x"] = self.x
        neural_params["y"] = self.y
        neural_params['ik'] = self.i_k
        neural_params['ina'] = self.i_na
        neural_params['ileak'] = self.i_leak
        neural_params['isyn'] = self.i_syn

        for key in gating_variables:
            current_gate = gating_variables[key]
            gating_params[f"{key}_state"] = current_gate.state
            gating_params[f"{key}_alpha"] = current_gate.alpha
            gating_params[f"{key}_beta"] = current_gate.beta

        params['params'] = neural_params
        params['gating_params'] = gating_params
        return params

    # ----------------- Current Setter Functions -----------------
    def set_no_current(self):
        """
        Sets the input current function to return zero current.
        """
        from neuron_models.input_currents import input_current
        current = input_current()
        self.input_current_func = current.get_current

    def set_sin_current(self, freq, amplitude):
        """
        Sets the input current function to a sine wave.
        
        :param freq: Frequency (Hz).
        :param amplitude: Amplitude of the current.
        """
        from neuron_models.input_currents import sin_current
        current = sin_current(self.dt, [amplitude, freq])
        self.input_current_func = current.get_current

    def set_square_current(self, freq, amplitude):
        """
        Sets the input current function to a square wave.
        
        :param freq: Frequency (Hz).
        :param amplitude: Amplitude of the current.
        """
        from neuron_models.input_currents import square_current
        current = square_current(self.dt, [amplitude, freq])
        self.input_current_func = current.get_current

    def set_const_current(self, input_current_value):
        """
        Sets the input current function to a constant current.
        
        :param input_current_value: The constant current value.
        """
        from neuron_models.input_currents import constant_current
        current = constant_current(input_current_value)
        self.input_current_func = current.get_current

    def __str__(self) -> str:
        """
        Returns a string representation of the neuron's current state.
        """
        return str(self.get_params())


