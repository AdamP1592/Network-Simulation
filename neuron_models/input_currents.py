class constant_current:
    """
    Represents a constant current input.
    """
    def __init__(self, i):
        """
        Initializes the constant current with a fixed value.
        
        :param i: The constant current value.
        """
        self.i = i

    def get_current(self, t):
        """
        Returns the constant current regardless of time.
        
        :param t: Time (ignored).
        :return: The constant current value.
        """
        return self.i


class input_current:
    """
    Represents a generic input current that returns zero.
    This can serve as a base class or a placeholder for no input.
    """
    def __init__(self, params=None):
        """
        Initializes the input current.
        
        :param params: (Optional) A list of parameters for the input current.
        """
        if params is None:
            params = []
        self.needed_params = []
        self.set_params(params)

    def __str__(self):
        return "No Input"

    def get_current(self, t):
        """
        Returns the current (always zero for this base class).
        
        :param t: Time (ignored).
        :return: 0.
        """
        return 0

    def set_params(self, params=None):
        """
        Sets the parameters for the input current.
        
        :param params: A list of parameters.
        """
        if params is None:
            params = []
        self.params = params


class wave_current:
    """
    Base class for a time-varying (wave) current input.
    
    Expects parameters as [amplitude, frequency].
    """
    def __init__(self, dt, params=None):
        """
        Initializes the wave current.
        
        :param dt: Time step (seconds).
        :param params: (Optional) A list [amplitude, frequency]. Defaults to [0, 0].
        """
        if params is None:
            params = [0, 0]
        self.dt = dt
        self.needed_params = ["Max current (µA/cm²)", "Frequency (Hz)"]
        self.set_params(params)

    def set_amplitude(self, amplitude):
        """
        Sets the amplitude.
        
        :param amplitude: The amplitude value.
        """
        self.amplitude = amplitude

    def set_frequency(self, freq):
        """
        Sets the frequency.
        
        :param freq: The frequency value.
        """
        self.frequency = freq

    def set_params(self, params=None):
        """
        Sets the parameters for the wave current.
        
        :param params: A list [amplitude, frequency].
        """
        if params is None:
            params = [0, 0]
        self.set_amplitude(params[0])
        self.set_frequency(params[1])


class square_current(wave_current):
    """
    Represents a square wave current input.
    """
    def __init__(self, dt, params=None):
        """
        Initializes a square wave current.
        
        :param dt: Time step (seconds).
        :param params: (Optional) A list [amplitude, frequency]. Defaults to [0, 0.0001].
        """
        if params is None:
            params = [0, 0.0001]
        # Define parameter ranges and steps (could be used for UI scaling).
        self.param_value_ranges = [[0, 50], [0.00001, 1]]
        self.param_steps = [1, 0.001]
        super().__init__(dt, params)

    def __str__(self):
        return "Square Wave"

    def get_current(self, t):
        """
        Returns the square wave current at time t.
        The square wave is active during the first half of its period.
        
        :param t: Time in seconds.
        :return: Amplitude if within the active phase, otherwise 0.
        """
        period = 1 / self.frequency
        current_period_time = t % period
        # Returns amplitude if in the first half of the period, else 0.
        return self.amplitude * (current_period_time < (period / 2))


class sin_current(wave_current):
    """
    Represents a sine wave current input.
    """
    def __init__(self, dt, params=None):
        """
        Initializes a sine wave current.
        
        :param dt: Time step (seconds).
        :param params: (Optional) A list [amplitude, frequency]. Defaults to [0, 0].
        """
        if params is None:
            params = [0, 0]
        self.param_value_ranges = [[0, 50], [0, 1]]
        self.param_steps = [1, 0.001]
        super().__init__(dt, params)

    def __str__(self):
        return "Sin Wave"

    def get_current(self, t):
        """
        Returns the sine wave current at time t.
        The sine wave is shifted upward so that the current remains non-negative.
        
        :param t: Time in seconds.
        :return: The current value.
        """
        import math
        # math.sin() returns values in [-1, 1]; shifting by amplitude yields a range [0, 2*amplitude]
        return self.amplitude * math.sin(math.pi * t * self.frequency) + self.amplitude
