/*
    Main goals:
        Initialize with a network with sim(num_neurons)
        This generates all those neurons.

        Interface:
        
        1. generate graphs to show the neurons response to tsodyks markram synapses.
        2. Generate figure that shows the connectivity and activity of neuron responses 
            Neurons are circles black to white where black is totally inactive and white is action potential
            Synapses are lines made from red, yellow, and green colors (eventually ltp and ltd are going to be the border of said lines)
        3. Create electrode pads with input current I that connects to neurons within the borders of the electrode(these will be squares that are black to white)
        

        Simulation:

            generate_new_parameters(base_params, max_varainces, num_params) 
                Generates a series of neurons that each has a slight varaince from the base parameter. 
                Each varaince is some value between 0 and 1 to represent how much the max varance and each list must be the same size

            generate_neuron_parameters

            generate_synapse_parameters

            
            s = tsodyks_hodgkins_simulation(dt)
                s.base_neuron_params = {} 
                s.base_synapse_params = {}
                
                #since no db 
                s.pre_loaded_neuron_path 
                s.pre_loaded_synapse_path 

                #wish I had pointers for this because python is weird
                neurons = []
                


            






*/