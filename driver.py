from synapse_models.synapse import tsodyks_markram_synapse
import synapse_models.synapse_generator as synapse_generator
from simulation import simulation


def add_neuron(sim, params=None):
    """
    Adds a neuron to the simulation.
    
    If no parameters are provided, the simulation's default parameters are used.
    
    :param sim: The simulation instance.
    :param params: (Optional) A dictionary of parameters for the neuron.
    """
    if params is None:
        params = sim.default_neural_params
    sim.create_neuron()


def create_sim(num_neurons, x_max, y_max):
    """
    Creates a simulation instance with the specified number of neurons and culture dimensions.
    
    Neurons are positioned randomly within the given x and y dimensions.
    Synapses are generated between neurons using the synapse generator module.
    
    :param num_neurons: Number of neurons to create.
    :param x_max: Maximum x-dimension value.
    :param y_max: Maximum y-dimension value.
    :return: A simulation instance with neurons and synapses set up.
    """
    try:
        from numpy import random
    except ImportError as e:
        raise ImportError("Failed to import numpy.random: " + str(e))

    # Create simulation instance with a fixed dt (e.g., 0.0005).
    sim = simulation(num_neurons, 0.0005)
    
    # Generate random positions for neuron somata.
    soma_xs = random.rand(num_neurons) * x_max
    soma_ys = random.rand(num_neurons) * y_max
    soma_points = []

    for i in range(num_neurons):
        sim.neuron_models[i].x = soma_xs[i]
        sim.neuron_models[i].y = soma_ys[i]
        soma_points.append((soma_xs[i], soma_ys[i]))

    # Generate synaptic connections based on neuron positions.
    try:
        connections = synapse_generator.create_synapses(soma_points)
    except Exception as e:
        raise RuntimeError("Error generating synapses: " + str(e))

    for con in connections:
        pre_syn_neurons = con.hosts
        post_syn_neurons = con.connections

        # Get the center of the synapse region.
        x, y = con.get_center()

        # Create a synapse in the simulation.
        sim.create_synapse(pre_syn_neurons, post_syn_neurons)

        # Set the position of the newly created synapse.
        sim.synapses[-1].x = x
        sim.synapses[-1].y = y

    return sim


def get_sim_dict():
    """
    Reads and returns the simulation dictionary from a JSON file.
    
    :return: A dictionary containing simulation data.
    """
    import json
    try:
        with open("./data/sim.json", "r") as f:
            data = json.load(f)
    except Exception as e:
        raise IOError("Error reading simulation JSON file: " + str(e))
    return data


def store_sim(sim):
    """
    Saves the current simulation state to a JSON file.
    
    :param sim: The simulation instance.
    """
    import json
    try:
        sim_dict = sim.generate_model_dict()
        with open('./data/sim.json', 'w') as f:
            f.write(json.dumps(sim_dict))
    except Exception as e:
        raise IOError("Error writing simulation JSON file: " + str(e))

def set_sim_current(sim, neuron_index, neuron_stim_type, stim_params):
    # Create a simulation instance and restore state from the dictionary.
    
    neuron = sim.neuron_models[neuron_index]

    if neuron_stim_type == "Square":
        neuron.set_square_current(stim_params["freq"], stim_params["maxCurrent"])
    elif neuron_stim_type == "Sin":
        neuron.set_sin_current(stim_params["freq"], stim_params["maxCurrent"]/2)
    elif neuron_stim_type == "Constant":
        neuron.set_const_current(stim_params["maxCurrent"])
    elif neuron_stim_type == "None":
        neuron.set_no_current()
    else:
        print(f"Unknown stimulation type: {neuron_stim_type}")

def set_sim_dict_currents(sim_dict, data):

    network_dict = sim_dict["network"]
    dt = network_dict["dt"]
    
    sim = simulation(0, dt)
    try:
        sim.setup_old_instance_from_dict(sim_dict)
    except Exception as e:
        raise RuntimeError("Error setting up simulation from dictionary: " + str(e))
    
    for neuron_index in data:
        stim_params = data[neuron_index]
        neuron_stim_type = stim_params["currentType"]
        neuron_index_int = int(neuron_index)

        set_sim_current(sim, neuron_index_int, neuron_stim_type, stim_params)
        print(f"Applying stimulation: {stim_params}")

    return sim.generate_model_dict()

def iterate_sim(sim_dict, duration):
    print(sim_dict)
    """
    Recreates a simulation instance from a dictionary and iterates it for a given duration.
    
    :param sim_dict: The simulation dictionary.
    :param duration: Duration (in seconds) to iterate the simulation.
    """
    dt = 0.0005
    network_dict = sim_dict["network"]
    dt = network_dict["dt"]


    # Create a simulation instance and restore state from the dictionary.
    sim = simulation(0, dt)
    try:
        sim.setup_old_instance_from_dict(sim_dict)
    except Exception as e:
        raise RuntimeError("Error setting up simulation from dictionary: " + str(e))

    num_steps = int(duration / dt)
    graphing_params = sim.iterate(num_steps)
    
    print(graphing_params)
    vs = graphing_params["vs"]
    input_currents = graphing_params["input_currents"]
    synaptic_inputs = graphing_params["synaptic_inputs"]

    sim_dict = sim.generate_model_dict()
    # Update each neuron's data.
    for i in range(sim.num_neurons):
        sim_dict["neurons"][i]["vs"] = vs[i]
        sim_dict["neurons"][i]["input_currents"] = input_currents[i]
        sim_dict["neurons"][i]["synaptic_inputs"] = synaptic_inputs[i]


    
    return sim_dict

def print_sim_dict(sim_dict):
    print(sim_dict)
    """
    for key in sim_dict:
        for paramKey in sim_dict[key]:
            print(sim_dict[key][paramKey])
            
    """
if __name__ == '__main__':
    # Create a minimal simulation instance for testing.
    sim = create_sim(2, .2 , .2)
    print("Sim Created")
    
    # Set a sine current on the first neuron.
    
    # Run simulation for 100 steps and print voltage data.
    sim_dict = sim.generate_model_dict()

    print_sim_dict(sim_dict)

    print("\n\n")

    new_dict = set_sim_dict_currents(sim_dict,{'0': {'currentType': 'Sin', 'freq': 0.5, 'maxCurrent': 10}})
    print(new_dict)

    print("\n\n")
    new_sim = iterate_sim(new_dict, 0.1)




        


        
