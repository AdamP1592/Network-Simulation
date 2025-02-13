import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox
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

if __name__ == '__main__':
    fig = plt.figure(figsize=(10, 6))
    axs = fig.subplot_mosaic("""
                             aaab
                             aaac
                             aaac
                             aaac
                             aaac
                             aaac
                             dddd
                             eeee
                             """)
    
    fig.tight_layout()

    """for i in axs.keys():
        axs[i].set_axis_off()"""
    main_plot = axs["a"]
    side_plot_top = axs["b"]
    side_plot = axs["c"]
    bottom1_plot = axs["d"]
    bottom2_plot = axs["e"]



    main_plot.set_axis_on()
    dt = 0.01
    
    data =    {"gk": 36.004631953926285, "gna": 119.91561331101256, "gleak": 0.2997385592373893, "ek": -82.03623253390188, "ena": 45.028284147345595, "eleak": -59.35717906013866, "c": 0.9998470285990088, "vrest": -59.35717564093531, "vthresh": 15.119047441363206}
    num_pre_neurons = 2
    num_post_neurons = 1

    pre_synaptic_neurons = []
    post_synaptic_neurons = []
    sim = simulation(num_pre_neurons+ num_post_neurons, 0.001)


    #pre_synaptic_neurons = neurons[:num_pre_neurons]
    #post_synaptic_neurons = neurons[num_post_neurons+1:]

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
        #pre_synaptic_2.iterate()
        #post_synaptic_1.iterate()

        t += dt
        ts.append(t)
        #g_syns.append(s1.g_syn)
        #s1.update()
    #print(pre_synaptic_vs)

    #synapse_plot.plot(ts, g_syns)

    plt.draw() 
    plt.show()

