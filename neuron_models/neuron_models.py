
#each neuron will be 3 vectors, 1 point, and internal dynamics
#the point is the cell  body, the vectors are
#synaptic vector, axonal vector, and dendritic vector
#synaptic vector overlap will act as a modifier on the stdp rule
#axonal vector will either be mono or bidirectional, and will solely act 
#by branching out until connection is formed with a dendritic tree or
#the neuron can't grow anymore(cornered/reaches max length)
#The overlap between a dendritic vector and a axonal vector is
#where I will be determining connectivity, however it is important to note
#this is only 1 of 3 kinds of axonal connection. 


import math
class gate():
    def __init__(self):
        self.alpha, self.beta, self.state = 0, 0, 0

    def update(self, dt):
        alpha_state = self.alpha * (1 - self.state)
        beta_state = self.beta * self.state

        self.state += dt * (alpha_state - beta_state)
    def set_infinite_state(self):
        self.state = self.alpha / (self.alpha + self.beta)

class neuron():
    def __init__(self):
        pass
    def set_vars(self, vars = []): 
        pass
    #returns the mebrane potential after a given amount of time
    def update(self, voltage_in=0, time=0):
        pass

class hodgkin_huxley(neuron):
    
    #implement gate class
    def __init__(self, params:dict, dt = 0.0001):
        self.x, self.y = 0, 0
        #state setup
        self.n_gate, self.m_gate, self.h_gate = gate(), gate(), gate()
        
        self.dt = dt
        self.i_syn = 0

        #current params stup
        self.derivatives = []
        
        self.input_current_func = self.set_no_current()
        self.input_current = 0

        #timing params
        self.t = 0

        self.i_syn = 0

        #setup params
        self.set_params(params)
        self.update_gates(self.v)
        self.gating_varibles_setup()

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
    
    def gating_varibles_setup(self):
        self.n_gate.set_infinite_state()
        self.m_gate.set_infinite_state()
        self.h_gate.set_infinite_state()

    def update_gate_voltages(self, dt):
        #updates voltages
        self.n_gate.update(dt)
        self.m_gate.update(dt)
        self.h_gate.update(dt)

    def update_gates(self, v):
        #updates gate constants
        self.n_gate.alpha = self.alpha_n(v)
        self.n_gate.beta = self.beta_n(v)

        self.m_gate.alpha = self.alpha_m(v)
        self.m_gate.beta = self.beta_m(v)

        self.h_gate.alpha = self.alpha_h(v)
        self.h_gate.beta = self.beta_h(v)

    def runge_cutta_update(self):
        #4th order
        n = 4
        n_gates = [self.n_gate for i in range(n)]
        m_gates = [self.m_gate for i in range(n)]
        h_gates = [self.h_gate for i in range(n)]
        vs = [self.v for i in range(n)]
        step_size = self.dt/4
        for i in range(n):
            pass
            
    def update_v(self):
        #update input_current variable
        self.input_current = self.input_current_func(self.t)
        #calculates totals for each ion channel
        self.i_k = self.gK * (self.n_gate.state ** 4) * (self.v - self.eK)
        self.i_na = self.gNa * (self.m_gate.state ** 3) * self.h_gate.state * (self.v - self.eNa)
        self.i_leak = self.gLeak * (self.v - self.eLeak)
    
        #adds the sum total of all input currents to the current total voltage
        total_current = self.input_current - self.i_k - self.i_na - self.i_leak - self.i_syn
        dvdt = total_current/self.membrane_cap

        self.derivatives.append(dvdt)
        self.v += dvdt * self.dt
        self.t+= self.dt

    def update(self):
        #update the gate state varaibles, then update the voltage as a result of those gate changes, then update the voltage over those gates as a result of the voltage change
        self.update_gates(self.v)
        self.update_v() 
        self.update_gate_voltages(self.dt)

        self.i_syn = 0
    
    #sets all neural parameters to the specified values ---tweak to conform to naming standard for separating neural parameters and gating paramaters
    def set_params(self, params:dict):
        #params = {gk:, gna:, gleak:, ek:, ena:, eleak:, c:}
        self.gK = params['gk']
        self.gNa = params['gna']
        self.gLeak = params['gleak']

        self.eK = params['ek']
        self.eNa = params['ena']
        self.eLeak = params['eleak']

        self.resting_potential = params['vrest']
        self.action_potential_threshold = params['vthresh']
        
        self.v = self.resting_potential

        self.membrane_cap = params['c']
    
    #create a dictionary object with all stored neural parameters so instance can be stored
    def get_params(self):
        #this neurons parameters
        params = {}
        neural_params = {}
        gating_params = {}
        gating_variables = {'n': self.n_gate, 'm': self.m_gate, 'h': self.h_gate}

        #params = {gk:, gna:, gleak:, ek:, ena:, eleak:, c:, resting_voltage, action_potential_threshhold} 
        neural_params['gk'] = self.gK 
        neural_params['gna'] = self.gNa 
        neural_params['gleak'] =  self.gLeak 

        neural_params['ek'] = self.eK
        neural_params['ena'] = self.eNa
        neural_params['eleak'] = self.eLeak

        neural_params['resting_voltage'] = self.resting_potential
        neural_params['action_potential_threshhold'] = self.action_potential_threshold
        #generates a dictionary of all the gating variables(n, m, h)
        #each gating variable is a dictionary of the current state, and 
        for i in gating_variables.keys():
            #stores each gating variable in a dictionary.
            current_gate = gating_variables[i]
            gating_params[f"{i}_state"] = current_gate.state
            gating_params[f"{i}_alpha"] = current_gate.alpha
            gating_params[f"{i}_beta"] = current_gate.beta


        params['neuron'] = neural_params
        params['gating'] = gating_params

        return params
    

    #setter functions for different types of currents

    def set_no_current(self):
        from neuron_models.input_currents import input_current
        current = input_current()

        self.input_current_func = current.get_current

    def set_sin_current(self, freq, amplitude):
        from neuron_models.input_currents import sin_current
        
        current = sin_current(self.dt, [amplitude, freq])
        self.input_current_func = current.get_current



    def set_square_current(self, freq, amplitude):
        from neuron_models.input_currents import square_current

        current = square_current(self.dt, [amplitude, freq])
        self.input_current_func = current.get_current


    def set_const_current(self, input_current):
        from neuron_models.input_currents import constant_current

        current = constant_current(input_current)
        self.input_current_func = current.get_current

    
#each neuron will be 3 vectors, 1 point, and internal dynamics
#the point is the cell  body, the vectors are
#synaptic vector, axonal vector, and dendritic vector
#synaptic vector overlap will act as a modifier on the stdp rule
#axonal vector will either be mono or bidirectional, and will solely act 
#by branching out until connection is formed with a dendritic tree or
#the neuron can't grow anymore(cornered/reaches max length)
#The overlap between a dendritic vector and a axonal vector is
#where I will be determining connectivity, however it is important to note
#this is only 1 of 3 kinds of axonal connection. 


#axon max length is defined by a combination of enviornmental constraints and 
#natural growth constraints of neuron. 
#connections will be determined by checking each dendrite and axon vectors for overlap.
#axons vectors will naturally "repel" eachother by increasing
"""primary thigs:

n = neuron(dict of parameters)
    creates neuron

n.set_x_current(current params) 
    sets the input current I for the neuron

n.update() 
    updates neuron state given the input current equation

n.v 
    membrane potential


n.i_syn = synaptic input variable
    use case: when a neurons are connected via synapses there will be a synaptic input current that is the sum of all synaptic inputs from other neurons
    IF USED ALWAYS SET AT NETWORK LEVEL BEFORE EACH STEP

"""