# Network-Simulation

A network simulation project modeling a network of neurons with stimulation. This project uses a Hodgkin–Huxley neuron model with dynamic synapses based on the Tsodyks–Markram model. It combines biophysical modeling, computational geometry for connectivity, and a Flask backend API to serve a webpage interface.

---

## Table of Contents

- [Overview](#overview)
- [Neuron Model](#neuron-model)
- [Synapse Generator](#synapse-generator)
- [Backend API](#backend-api)
- [Installation](#installation)
- [Usage](#usage)
- [Future Enhancements](#future-enhancements)

---

## Overview

This project simulates a network of neurons using a Hodgkin–Huxley model with dynamic synapses. The core components include:

- **Biophysical Neuron Model:** Implements ion-channel dynamics and membrane potential updates using the Hodgkin–Huxley framework.
- **Dynamic Synapses:** Uses computational geometry to determine connectivity based on the overlap of axonal and dendritic projections.
- **Flask Backend:** Provides REST API endpoints for simulation initialization, iteration, and current stimulation.
- **Webpage Interface:** The backend API serves data to a webpage that displays the simulation results.

---

## Neuron Model

### Gate
- **Description:**  
  Implements ion channel gating dynamics.
- **Key Methods:**
  - `update(dt)`: Updates the gate state based on rate constants and a time step.
  - `set_infinite_state()`: Sets the gate state to its steady state.
- **Usage Example:**  
```python
    from neuron_model import gate

    dt = 0.01
    g = gate()
    g.set_infinite_state()
    g.update(dt)
    print("Gate state:", g.state)

```

### Hodgkin–Huxley Neuron
- **Description:**  
  A steady-state dynamics model for neurons using Hodgkin–Huxley equations. It accepts parameters for ion channel conductances (`gk`, `gna`, `gleak`), reversal potentials (`ek`, `ena`, `eleak`), membrane capacitance (`c`), resting voltage (`vrest`), and action potential threshold (`vthresh`).
- **Key Functions:**
  - **Current Setters:**  
    - `set_sin_current(frequency, max_voltage)`
    - `set_square_current(frequency, max_voltage)`
    - `set_const_current(current)`
    - `set_no_current()`
  - `update()`: Iterates the neuron state based on ionic and synaptic currents.
- **Usage Example:**  

```python
    from neuron_model import hodgkin_huxley

    params = {
        "gk": 36.0,
        "gna": 120.0,
        "gleak": 0.3,
        "ek": -77.0,
        "ena": 50.0,
        "eleak": -54.387,
        "vrest": -65,
        "vthresh": -55,
        "c": 1.0
    }
    dt = 0.0001
    n = hodgkin_huxley(params, dt)
    n.set_sin_current(12, 50)
    n.update()
    print("Membrane potential:", n.v)
```

---

## Synapse Generator

The synapse generator uses computational geometry to model connectivity:

- **Polygon Generation:**  
  Neuronal projections (axonal and dendritic) are modeled as semicircular polygons.
  
- **Connectivity Determination:**  
  Overlap between an axonal polygon from one neuron and a dendritic polygon from another produces a synapse (a `connection` object). Nested intersections are computed recursively.
  
- **Duplicate Removal:**  
  Duplicate connection objects are removed using the `remove_duplicate_intersections` function.

**Usage Example:**  
```python
        import numpy as np
        from shapely.geometry import Point
        # Adjust import based on any project structure changes
        from synapse_generator import create_synapses  

        num_neurons = 5
        max_size = 5
        soma_x = np.random.rand(num_neurons) * max_size
        soma_y = np.random.rand(num_neurons) * max_size
        soma_points = [Point(soma_x[i], soma_y[i]) for i in range(num_neurons)]

        synapses = create_synapses(soma_points)
        print("Generated", len(synapses), "synapses")
```
---

## Backend API

The Flask backend exposes several endpoints to manage the simulation:

- **`/simulation/startSim`**  
  Initializes the simulation with a specified number of neurons and culture dimensions.
- **`/simulation/iterateSim`**  
  Advances the simulation for a short duration (e.g., 100 ms) and returns updated neuron parameters as JSON.
- **`/simulation/setCurrent`**  
  Applies stimulation parameters to neurons and returns the updated simulation state.
- Additional routes such as `/home`, `/about`, and `/nav` render corresponding Jinja templates for the webpage.

## Installation

1. **Clone the Repository:**
```bash
    git clone https://github.com/AdamP1592/Network-Simulation.git 
    cd Network-Simulation
```

2. **Install Dependencies:**
```bash
   pip install -r requirements.txt
```


## Usage

- **Simulation Initialization:**  
  The simulation is initialized by prompting the user for the number of neurons. The backend builds the initial state and serves it to the webpage.
  
- **Interactivity:**  
  Interact with the simulation via the provided Flask API endpoints to set stimulation currents and iterate the simulation.
  
- **Example:**

```bash
   python ./web/app.py
```
   Then, open the provided URL in your browser.

---

## Future Enhancements

- **User-Defined Currents:**  
  Add support for user-defined current equations via text input.
- **Multi-User Support:**  
  Extend the backend to support multiple simulation instances concurrently.
- **Performance Optimization:**  
  Optimize the nested intersection computation for larger networks.

---

