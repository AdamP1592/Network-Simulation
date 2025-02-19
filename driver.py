from synapse_models.synapse import tsodyks_markram_synapse

import synapse_models.generate_synapses as generate_synapses

from simulation import simulation


#main variables for network sim:
# percent ampa
# percent gaba
# primarily active
# primarily inactive
def add_neuron(sim, params = None):
    
    if not params:
        params = sim.default_neural_params

    sim.create_neuron()


def create_sim(num_neurons):
    sim = simulation(num_neurons, 0.001)


def iterate_sim(sim_dict, duration):
    network_dict = sim_dict["network"]
    
    dt = network_dict["dt"]

    sim = simulation(0, 0)
    sim.setup_old_instance_from_dict(sim_dict)

    num_steps = int(duration/dt)

    sim.iterate(num_steps)

    

if __name__ == '__main__':
    
    dt = 0.001
    
    data = {"gk": 36.004631953926285, "gna": 119.91561331101256, "gleak": 0.2997385592373893, "ek": -82.03623253390188, "ena": 45.028284147345595, "eleak": -59.35717906013866, "c": 0.9998470285990088, "vrest": -59.35717564093531, "vthresh": 15.119047441363206}
    num_pre_neurons = 2
    num_post_neurons = 1

    pre_synaptic_neurons = []
    post_synaptic_neurons = []
    sim = simulation(num_pre_neurons + num_post_neurons, dt)

    for i in sim.neuron_models:
        i.set_params(data)

    cur = 40
    for i in range(num_pre_neurons):
        sim.neuron_models[i].set_sin_current(1, 50)
    
    sim.create_synapse(range(0, num_pre_neurons), range(num_pre_neurons, num_post_neurons + num_pre_neurons))
    g_syns = []
    ts = []
    t = 0
    for i in range(int(20/dt)):
        sim.iterate()

        t += dt
        ts.append(t)

    model_dict = sim.generate_model_dict()

    sim1 = str(sim)
    sim = simulation(0, dt)

    sim.setup_old_instance_from_dict(model_dict)

    sim.iterate()

