# Network-Simulation
A simulated network of neurons with stimulation
Neuron Model:
    |
    GATE:
        variables:
            alpha, beta, state
        Update(dt):
            updates alpha and beta states given the time
        set_infinte_state:
            sets the state as it t approaches infinity
        USE:
            n_gate = gate()
            n_gate.set_infinite_state()
            n.update(dt)

    |
    Hodgkin_huxley_neuron:
        **NOTES**
            Steady-state dynamics model, will not update any values set like resting voltage or action potential threshold. 

        
        Required Input:
            params: dictionary of neuron parameters
                g: the max membrane conductances of each ion channel
                e: the reversal potential 
                {gk, gna, gleak, ek, ena, eleak}

        Variables:
            x, y postions
            v_rest: resting voltage
            v_thresh: action potential threshold

        Primary functions:
            (every .1ms)
            n = neuron(dict_of_parameters, dt = 0.0001) 


            Defalt current setters,
                ----- future version will have a text input for an equation that has the variables
                ----- for current and time in ms

                n.set_sin_current(frequency, max voltage(mV))
                n.set_square_current(frequency, max voltage(mV))
                n.set_const_current(current)
                n.set_no_current()

            n.update(): iterates everything

            n.v: membrane potential

            n.i_syn: sum total of synaptic input

        Use:
            n = neuron(dict_of_parameters) #default dt

            n.set_sin_current(12, 50)
            
            n.update()

            current_membrane_potential = n.v

            --(With Synapses)--

            n = neuron(dict_of_parameters)

            simulated_presynaptic_currents = [20, -40, -50, -11]
            sum_synaptic_currents = sum(simulated_presynaptic_currents)
            
            n.i_syn = sum_synaptic_currents

            n.update()

            
    
            
            

