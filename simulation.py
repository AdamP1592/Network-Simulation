class simulation():
    
    #gating constants
    eNa, eK, eLeak = 50, -77, -54.4
    gNa, gK, gLeak = 120, 36, 0.3
    #membrane cap
    Cm = 1

    #standard resting potential for neurons
    resting_potential = -70
    
    input_current = 0
    def __init__(self, vrest, vthresh, dt):
        from neuron_models import hodgkin_huxley
        self.model = hodgkin_huxley(vrest, vthresh, dt)

        self.model.gK = self.gK
        self.model.gNa = self.gNa
        self.model.gLeak = self.gLeak
        self.model.eK = self.eK
        self.model.eNa = self.eNa
        self.model.eLeak = self.eLeak
        self.model.membrane_cap = self.Cm

        self.input_current = 0
        self.n, self.m, self.h, = [], [], []
        self.v, self.input_currents  = [], []
        
        self.times = []
        self.dt = dt
        self.t = 0
        self.input_current_func = self.default_input
        self.i_syn = 0
    def set_params(self, params:dict):
        self.model.set_params(params)
    def iterate(self, num_steps= 1):
        for i in range(num_steps):
            self.times.append(self.dt + self.t)
            self.model.i_syn = self.i_syn
            self.input_current = self.input_current_func(self.t)
            self.input_currents.append(self.input_current)

            self.model.update(self.input_current)
            
            self.n.append(self.model.n_gate.state)
            self.m.append(self.model.m_gate.state)
            self.h.append(self.model.h_gate.state)

            self.v.append(self.model.v)
            self.t+=self.dt
            self.i_syn = 0
    
    def set_input_current(self, current_function):
        self.input_current_func = current_function

    def set_no_current(self):
        self.input_current_func = lambda t: 0
    def set_const_current(self, i):
        from input_currents import constant_current
        current = constant_current(i)
        self.input_current_func = current.get_current
    def clear(self, num_steps):
        past_current_func = self.input_current_func
        self.set_no_current()
        self.iterate(num_steps)
        self.input_current_func = past_current_func

    #input current functions 
    def default_input(self, t):
        return 0
    def square(self, t):
        return 50
    def sin(self, t):
        import math
        amplitude = 25
        return (amplitude * math.sin(math.pi * t * 0.1) + amplitude)
"""
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from matplotlib.widgets import RadioButtons

    #sim setup
    dt = 0.01
    neuron_sim = simulation(dt)

    #generating a mutable datatype so it can be used in set_current
    input_types = {"Defaut":0, "Sin":1, "Square":2}
    current_input_type = ["Default"]
    #helper function for radio buttons
    def set_current(input_type):
        #sets the current input type to the index of it's type
        current_input_type[0] = input_type
        input_dict = {"Square": neuron_sim.square , "Sin": neuron_sim.sin, "None": neuron_sim.default_input}
        neuron_sim.input_current_func = input_dict[input_type]
    
    #escape case events    
    def on_press(event):
        import sys
        #clear event
        sys.stdout.flush()

        #why are you like this
        if(event.key == " "):
            from pathlib import Path
            #savefig chooses to save two parent folders up, so set path directly
            p = Path("simulation.py")
            #current input type =  
            fig.savefig("{}/demo/{}.png".format(str(p.parent.absolute()), current_input_type[0]))
            print("saved")
        if event.key=="escape":
            exit()
    def on_close(event):
        exit()
        #plot setup
    plt.ion()
    plt.show()
    fig, ax_dict = plt.subplot_mosaic(
                                AAD
                                BBD
                                CCD
                                )
    #break up each dict
    ax0 = ax_dict["A"]
    ax1 = ax_dict["B"]
    ax2 = ax_dict["C"]
    ax3 = ax_dict["D"]
    #manager setup
    manager = plt.get_current_fig_manager()
    manager.resize(*manager.window.maxsize())

    #some styling
    fig.tight_layout()
    fig.set_figwidth(13)
    ax3.set_aspect(2.5)

    #escape cases
    fig.canvas.mpl_connect('key_press_event', on_press)
    fig.canvas.mpl_connect('close_event', on_close)

    #setup for radio buttons
    current_radio_buttons = RadioButtons(ax3, ["None", "Square", "Sin"])
    current_radio_buttons.on_clicked(set_current)

    #could not update y_data and still reload the graph, so this is what you get
    #no idea why
    i = 0
    while(i < 10000):
        #clears data points
        ax0.cla()
        ax1.cla()
        ax1.cla()
        ax2.cla()
        #resets lables after being cleared
        ax0.set_ylabel("Potential(mv)")
        ax1.set_ylabel("Activation")
        ax2.set_ylabel("Current (µA/cm²)")
        
        #redraw after every 10 steps
        for j in range(100):
            neuron_sim.iterate()

        #limit how many datapoints can be seen at once time
        num_datapoints = len(neuron_sim.times)
        past_range = 6000
        if num_datapoints < past_range:
            past_range = num_datapoints
       
        
        #plots data
        x = neuron_sim.times[num_datapoints - past_range:]

        ax0.plot(x, neuron_sim.v[num_datapoints - past_range:])

        ax1.plot(x, neuron_sim.m[num_datapoints - past_range:])
        ax1.plot(x, neuron_sim.n[num_datapoints - past_range:])
        ax1.plot(x, neuron_sim.h[num_datapoints - past_range:])

        ax2.plot(x, neuron_sim.input_currents[num_datapoints - past_range:])
        plt.draw()

        plt.pause(0.005)
    

        i+=1
    plt.close()

"""
