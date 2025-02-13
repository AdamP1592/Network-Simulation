import neuron_models
import synapse_models.synapse as synapse
from matplotlib import pyplot as plt
from simulation import simulation


if __name__ == '__main__':
    fig, axs= plt.subplots(4, 1)
    fig.set_tight_layout(1)
    pre_synaptic_plot = axs[0]

    post_synaptic_plot = axs[1]


    current_plot = axs[2]
    synapse_plot = axs[3]
    dt = 0.001


    pre_synaptic_plot.set_title("Pre synaptic neuron activity")
    post_synaptic_plot.set_title("Post synaptic neuron activity")
    current_plot.set_title("input currents")
    synapse_plot.set_title("synaptic activity")
    
    data =   {"gk": 36.004631953926285, "gna": 119.91561331101256, "gleak": 0.2997385592373893, "ek": -82.03623253390188, "ena": 45.028284147345595, "eleak": -59.35717906013866, "c": 0.9998470285990088, "vrest": -59.35717564093531, "vthresh": 15.119047441363206}
    num_pre_neurons = 2
    num_post_neurons = 1

    pre_synaptic_neurons = []
    post_synaptic_neurons = []
    sim = simulation(num_pre_neurons + num_post_neurons, 0.001)


    #pre_synaptic_neurons = neurons[:num_pre_neurons]
    #post_synaptic_neurons = neurons[num_post_neurons+1:]

    for i in sim.neuron_models:
        i.set_params(data)

    print(sim.neuron_models[0].resting_potential)

    sim.create_synapse(range(0, num_pre_neurons), range(num_pre_neurons, num_post_neurons + num_pre_neurons))

    sim.clear(int(10/dt))

    cur = 40
    sim.neuron_models[0].set_const_current(50)
    
    
    
    g_syns = []
    ts = []
    t = int(10/dt)
    for i in range(int(20/dt)):
        sim.iterate()
        #pre_synaptic_2.iterate()
        #post_synaptic_1.iterate()

        t += dt
        ts.append(t)
        #g_syns.append(s1.g_syn)
        #s1.update()
    #print(pre_synaptic_vs)
    for i in range(num_pre_neurons):
        pre_synaptic_plot.plot(sim.vs[i])
    
    for i in range(num_pre_neurons, num_post_neurons + num_pre_neurons):
        post_synaptic_plot.plot( sim.vs[i])
    #print(sim.input_currents)
    for i in sim.input_currents:
        current_plot.plot(i)
    synapse_plot.plot(sim.synapse_gs[0])
    #pre_synaptic_plot.plot(ts, pre_synaptic_2.v)
    #post_synaptic_plot.plot(ts, post_synaptic_1.v)
        #pre_synaptic_plot.plot(ts, pre_synaptic_neurons[i].input_currents)
    """for i in range(num_post_neurons):
        post_synaptic_plot.plot(ts, post_synaptic_neurons[i].v)"""

    #synapse_plot.plot(ts, g_syns)

    plt.draw() 
    plt.show()

