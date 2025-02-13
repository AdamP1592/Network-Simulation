class constant_current():
    def __init__(self, i):
        self.i = i
    def get_current(self, t):
        return self.i
class input_current():
    def __init__(self, params = []):
        self.needed_params = []
        self.set_params(params)
        pass

    def __str__(self):
        return "No Input"
    def get_current(self, t):
        return 0
    def set_params(self, params = []):
        self.params = params


class wave_current():
    #input params = [voltage, Frequency(mHz)]

    
    def __init__(self, dt, params = [0, 0]):
        #dt is number of seconds per t
        self.dt = dt

        self.needed_params = ["Max current(µA/cm²)", "Frequency(Hz)"]
        self.set_params(params)

    def set_amplitude(self, amplitude):
        self.amplitude = amplitude

    def set_frequency(self, freq):
        self.frequency = freq

    def set_params(self, params = [0, 0]):
        self.set_amplitude(params[0])
        self.set_frequency(params[1])

class square_current(wave_current):

    def __init__(self, dt, params = [0, 0.0001]):

        self.param_value_ranges = [[0, 50], [0.00001, 1]]
        self.param_steps = [1, 0.001]
        
        #wave variable setup
        super().__init__(dt, params)

    #returns the type of wave
    def __str__(self):
        return "Square Wave"

    #returns current with respect to t
    #t is time in ms 
    def get_current(self, t):
        period = 1/self.frequency

        current_period_time = t % period

        #square wave starts active and halfway thru period reverses
        return self.amplitude * (current_period_time < (period / 2))

class sin_current(wave_current):

    def __init__(self, dt, params = [0,0]):
        #display stuff
        self.param_value_ranges = [[0, 50], [0, 1]]
        self.param_steps = [1, 0.001]

        super().__init__(dt, params)

    def __str__(self):
        return "Sin Wave"
    
    def get_current(self, t):
        import math
        return (self.amplitude * math.sin(math.pi * t * self.frequency) + self.amplitude)
    
        
        