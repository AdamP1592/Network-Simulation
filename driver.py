from synapse_models.synapse import tsodyks_markram_synapse

import synapse_models.synapse_generator as synapse_generator

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


def create_sim(num_neurons, x_max, y_max):
    from numpy import random
    sim = simulation(num_neurons, 0.001)

    soma_xs = random.rand(num_neurons) * x_max
    soma_ys = random.rand(num_neurons) * y_max

    soma_points = []

    for i in range(num_neurons):

        sim.neuron_models[i].x = soma_xs[i]
        sim.neuron_models[i].y = soma_ys[i]

        soma_points.append((soma_xs[i], soma_ys[i]))

    connections = synapse_generator.create_synapses(soma_points)

    #[print("connections\n\n", con) for con in connections]

    for con in connections:
        pre_syn_neurons = con.hosts
        post_syn_neurons = con.connections

        #use for probability of connection
        x, y = con.get_center()

        sim.create_synapse(pre_syn_neurons, post_syn_neurons)
        #set position of last created neuron
        sim.synapses[-1].x = x
        sim.synapses[-1].y = y


    return sim
def get_sim_dict():
    import json
    data = {}
    with open("./data/sim.json", "r") as f:
        data = json.load(f)

    return data

def store_sim(sim):
    import json
    sim_dict = sim.generate_model_dict()

    with open('./data/sim.json', 'w') as f:

        f.write(json.dumps(sim_dict))


def iterate_sim(sim_dict, duration):
    network_dict = sim_dict["network"]
    
    dt = network_dict["dt"]

    sim = simulation(0, 0)
    sim.setup_old_instance_from_dict(sim_dict)

    num_steps = int(duration/dt)

    sim.iterate(num_steps)

if __name__ == '__main__':
    #neuron_sim = create_sim(5, 5, 5)


    sim = create_sim(5, 5, 5)
    #sim.setup_old_instance_from_dict(sim_dict)
    """
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
    """

