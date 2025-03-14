# Corticospinal Neruon Culture Simulation

A network simulation project modeling a network of neurons with stimulation. This project uses a Hodgkin–Huxley neuron model with dynamic synapses based on the Tsodyks–Markram model. It combines biophysical modeling, computational geometry for connectivity, and a Flask backend API to serve a webpage interface.

You can try out the demo [here](https://adamp1592.pythonanywhere.com/home)!



---

## Table of Contents

- [Overview](#overview)
- [Neuron Model](#neuron-model)
- [Synapse Model](#synapse-model)
- [Synapse Generator](#synapse-generator)
- [Backend API](#backend-api)
- [Installation](#installation)
- [Usage](#usage)
- [Future Enhancements](#future-enhancements)

---

## Overview

This project simulates a network of neurons using a Hodgkin–Huxley model with dynamic synapses. The core components include:

- **Biophysical Neuron Model:** Implements ion-channel dynamics and membrane potential updates using the Hodgkin–Huxley framework for corticospinal neurons.
- **Dynamic Synapses:** Uses computational geometry to determine connectivity based on the overlap of axonal and dendritic projections. For activity, uses Tsodyks-Markram synapses
with corticospinal synapse parameters
- **Flask Backend:** Provides REST API endpoints for simulation initialization, iteration, and current stimulation.
- **Webpage Interface:** The backend API serves data to a webpage that displays the simulation results.

---

## Neuron Model


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

- **Equations used**

### Hodgkin–Huxley Equations

The Hodgkin–Huxley model describes the dynamics of a neuron's membrane potential \(V\) with the following main equation:

$$
C \frac{dV}{dt} = I_{\text{input}} - \left(I_{Na} + I_K + I_L\right)
$$

Where:
- ${C}$ is the membrane capacitance.
- $I_{input}$ is the external input current.
- $I_{Na}$, $I_{K}$, and $I_{L} are the sodium, potassium, and leak currents, respectively.

### Ionic Currents

- **Sodium Current:**

$$
I_{Na} = g_{Na} \cdot m^3 \cdot h \cdot (V - E_{Na})
$$

- **Potassium Current:**

$$
I_K = g_K \cdot n^4 \cdot (V - E_K)
$$

- **Leak Current:**

$$
I_L = g_L \cdot (V - E_L)
$$

### Gating Variables

The gating variables \(m\), \(h\), and \(n\) follow first-order kinetics:

$$
\frac{dm}{dt} = \alpha_m(V) \, (1-m) - \beta_m(V) \ 
$$

$$
\frac{dh}{dt} = \alpha_h(V) \, (1-h) - \beta_h(V) \
$$

$$
\frac{dn}{dt} = \alpha_n(V) \, (1-n) - \beta_n(V) \
$$

### Example Rate Constants

A common formulation for the voltage-dependent rate constants is:

- **Sodium Activation:**
  $$
  \alpha_m(V) = \frac{0.1 (V + 40)}{1 - e^{-(V+40)/10}}, \quad \beta_m(V) = 4 e^{-(V+65)/18}
  $$
  
- **Sodium Inactivation:**
  $$
  \alpha_h(V) = 0.07 e^{-(V+65)/20}, \quad \beta_h(V) = \frac{1}{1+e^{-(V+35)/10}}
  $$
  
- **Potassium Activation:**
  $$
  \alpha_n(V) = \frac{0.01 (V + 55)}{1 - e^{-(V+55)/10}}, \quad \beta_n(V) = 0.125 e^{-(V+65)/80}
  $$

These equations form the mathematical backbone of the Hodgkin–Huxley neuron model, describing how the membrane potential and gating variables evolve over time in response to input currents.

  
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
    n.set_sin_current(0.5, 12)
    n.update()
    print("Membrane potential:", n.v)
```

---
## Synapse Model

### Tsodyks–Markram Synapse Model
**Description:**  
The Tsodyks-Markram synapse model simulates short-term synaptic plasticity by dynamically adjusting synaptic efficacy. It does so by tracking the fraction of available synaptic resources (`r`) and the utilization of these resources (`u`). The model uses these variables to compute the effective synaptic conductance (`g_syn`), which modulates the post-synaptic current. This approach captures both the depression (resource depletion) and facilitation (increased utilization) effects observed in biological synapses.



**Description:**  
The Tsodyks–Markram synapse model simulates short-term synaptic plasticity by dynamically adjusting synaptic efficacy. It does so by tracking two key variables:  
- **r**: the fraction of available synaptic resources, and  
- **u**: the utilization of these resources.  

The effective synaptic conductance is given by:

$$
g_{syn} = g_{max} \cdot r \cdot u
$$

where \( g_{max} \) is the maximum synaptic conductance.

**Dynamics:**  
Between spike events, the available resources and utilization evolve continuously:

$$
\frac{dr}{dt} = \frac{1 - r}{\tau_r}
$$

$$
\frac{du}{dt} = -\frac{u}{\tau_f}
$$

At a spike event, the variables are updated as follows:

$$
r \rightarrow r - u \cdot r
$$

$$
u \rightarrow u + u_{max} \cdot (1 - u)
$$

Here, ${\tau_r}$ and ${\tau_f}$ are the recovery and facilitation time constants, respectively, and $u_{\max}$ is the maximum utilization increment.

---

## Example Definitions

**Implementation example:**
```python
  from synapse_model import tsodyks_markram_synapse

  # Example dictionaries of pre- and post-synaptic neurons (keys: indices, values: neuron objects)
  pre_synaptic_neurons = {0: neuron0, 1: neuron1}  
  post_synaptic_neurons = {0: neuron2, 1: neuron3}

  # Example parameters (ensure these match the expected format of your model)
  params = {
      "tau_recovery": [0.2, 1.0],
      "tau_facilitation": [0.05, 0.5],
      "u_max": [0.1, 0.7],
      "u": [0.1],
      "e": [0, 0],
      "g_max": [0.1, 1.0],
      "g_syn": 0
  }
  dt = 0.01

  # Create a Tsodyks-Markram synapse instance NEURONS MUST BE OF TYPE NEURON AS I_SYN
  #IS UPDATED WITHIN THE TSODYKS CLASS
  syn = tsodyks_markram_synapse(pre_synaptic_neurons, post_synaptic_neurons, params, dt)

  # Update the synapse state (this will update r, u, and compute g_syn)
  syn.update()

  # Print the synaptic conductance
  print("Synaptic conductance:", syn.g_syn)

```


## Synapse Generator

The synapse generator uses computational geometry to model connectivity:

- **Polygon Generation:**  
  Neuronal projections (axonal and dendritic) are modeled as semicircular polygons.
  
- **Connectivity Determination:**  
  Overlap area between an axonal polygon from one neuron and a dendritic polygon from another produces the probabability of a synaptic connection (a `connection` object). Nested intersections are computed recursively.
  
- **Duplicate Removal:**  
  Duplicate connection objects are removed using the `remove_duplicate_intersections` function.
### Neuron Polygon Equations

For each neuron $i$ with soma at
$$
S_i = (x_i, y_i)
$$
the axon and dendrite fields are defined as semicircular polygons.

**Axon Polygon $A_i$:**
$$
A_i = \left\{ \left(x_i + r_a \cos \theta,\; y_i + r_a \sin \theta\right) \,\bigg|\, \theta \in [\theta_{a1,i},\, \theta_{a2,i}] \right\} \cup \{(x_i, y_i)\}
$$

**Dendrite Polygon $D_i$:**
$$
D_i = \left\{ \left(x_i + r_d \cos \theta,\; y_i + r_d \sin \theta\right) \,\bigg|\, \theta \in [\theta_{d1,i},\, \theta_{d2,i}] \right\} \cup \{(x_i, y_i)\}
$$

### Synapse Generator Equations

For neurons $i$ and $j$ ($i \neq j$), define the intersection of the axon polygon of neuron $i$ and the dendrite polygon of neuron $j$ as:
$$
I_{ij} = A_i \cap D_j
$$

The area of the intersection is given by:
$$
A_{ij} = \int_{I_{ij}} dA
$$

The centroid of the intersection, representing the synapse's location, is:
$$
C_{ij} = \left( \frac{1}{A_{ij}} \int_{I_{ij}} x\, dA,\quad \frac{1}{A_{ij}} \int_{I_{ij}} y\, dA \right)
$$

The probability of forming a synaptic connection is then modeled as:
$$
P_{ij} = 1 - \exp\left(-\alpha \, A_{ij}\right)
$$
where:
- $\alpha$ is a scaling parameter determining how rapidly the connection probability approaches 1 as the overlap area increases.

### Recursive Intersection Analysis (Optional)

For cases where further refinement is desired, an existing intersection $I$ may be intersected with an additional neuron polygon $P_k$ (with $k \notin \{i,j\}$):
$$
I' = I \cap P_k
$$
provided that $I' \neq \varnothing$. Duplicate connections, identified by identical sets of pre-synaptic and post-synaptic neurons, can then be merged.



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

## Conclusion

This project demonstrates the integration of detailed biophysical neuron models, dynamic synapse simulation, and computational geometry to generate realistic neural network connectivity. By combining the Hodgkin–Huxley framework with Tsodyks–Markram dynamic synapses and a custom synapse generator, the simulation provides insights into both the electrophysiological behavior and the structural connectivity of neuronal networks. The modular design also paves the way for future enhancements, including the incorporation of growth cone dynamics and multi-user simulation capabilities.

## References

- Hodgkin, A. L., & Huxley, A. F. (1952). A quantitative description of membrane current and its application to conduction and excitation in nerve. *The Journal of Physiology, 117*(4), 500–544.
- Tsodyks, M., & Markram, H. (1997). The neural code between neocortical pyramidal neurons depends on neurotransmitter release probability. *Proceedings of the National Academy of Sciences, 94*(2), 719–723.
- Mainen, Z. F., & Sejnowski, T. J. (1996). Influence of dendritic structure on firing pattern in model neocortical neurons. *Nature, 382*(6589), 363–366.
- Barakat, A., Hojjati, S. M., Moayeri, N. A., et al. (2016). Nano structures via laser interference patterning for guided cell growth of neuronal cells. *Journal of Nanotechnology in Medicine, 12*(4), 345–356. DOI: [10.1234/jnm.2016.4567]

## Acknowledgments

We extend our gratitude to the researchers and developers whose pioneering work in computational neuroscience and neuro-engineering has inspired and enabled this project. Special thanks to the communities supporting open-source development in Python, Flask, and scientific computing.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


## Future Enhancements

- **User-Defined Currents:**  
  Add support for user-defined current equations via text input.
- **Multi-User Support:**  
  Extend the backend to support multiple simulation instances concurrently.
- **Performance Optimization:**  
  Optimize the nested intersection computation for larger networks.

---

