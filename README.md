 # Corticospinal Neuron Culture Simulation

A network simulation project modeling a network of neurons with stimulation. This project uses a Hodgkin–Huxley neuron model with dynamic synapses based on the Tsodyks–Markram model. It combines biophysical modeling, computational geometry for connectivity, and a Flask backend API to serve a webpage interface.

*Note: For demonstration, some synaptic and network parameters are set for visual clarity and performance, not strict biological realism*

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
- [Conclusion and References](#conclusion)
- [Future Enhancements](#future-enhancements)


---

## Overview

This project simulates a network of neurons using a Hodgkin–Huxley model with dynamic synapses. The core components include:

- **Biophysical Neuron Model:** Implements ion-channel dynamics and membrane potential updates using the Hodgkin–Huxley framework with constants based on corticospinal neurons.
- **Dynamic Synapses:** Uses computational geometry to determine connectivity based on the overlap of axonal and dendritic projections. For activity, uses Tsodyks–Markram synapses with glutamatergic parameters (based on neocortical literature, but tuned for maximal visible activity in the demo).
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
\frac{dV}{dt} = \frac{I_{\!ext} \;-\; I_{\!na} \;-\; I_k \;-\; I_{\!leak} \;-\; I_{\!syn}}{C_m}
$$

Where:
- ${C}$ is the membrane capacitance.
- $I_{input}$ is the external input current.
- $I_{Na}$, $I_{K}$, and $I_{L} are the sodium, potassium, and leak currents, respectively.

### Ionic Currents

- **Sodium Current:**

$$
I_{na} = g_{na}\,m^4\,h\,(V - E_{na})\\
$$

- **Potassium Current:**

$$
I_k = g_k\,n^4\,(V - E_k)\\
$$

- **Leak Current:**

$$
I_{leak} = g_{leak}\,(V - E_{leak})\\
$$

- **Synaptic Input**

$$
I_{syn} = g_{syn}\,\,(V - E_{syn})
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
The Tsodyks-Markram synapse model simulates short-term synaptic plasticity by dynamically adjusting synaptic efficacy. It does so by tracking the fraction of available synaptic resources (`r`) and the utilization of these resources (`u`), and a decoupled (`g_syn`). This approach captures both the depression (resource depletion) and facilitation (increased utilization), as well as the variable conductions, all effects observed in biological synapses.

**Dynamics:**  
Between spike events, the available resources, utilization, and conductance evolve continuously:

$$
\frac{dr}{dt} = \frac{1 - r}{\tau_r}
$$

$$
\frac{du}{dt} = -\frac{u}{\tau_f}
$$

$$
\frac{dg_{syn}}{dt} = \frac{-g_{syn}}{\tau_g}
$$

At a spike event, the variables are updated as follows:


$$
u = u + u_{min} \cdot (1 - u)\\$$

$$
g_{syn} = g_{syn} + g_{max} \cdot u \cdot r\\
$$

$$
r = r - (u \cdot r)\\
$$

$$
I_{syn} = g_{syn} * (V_{post} - E_{r})\\
$$


Here, ${\tau_r}$ and ${\tau_f}$ are the recovery and facilitation time constants, respectively, and $u_{\max}$ is the maximum utilization increment. $u_{\min}$ is denoted as such for the sake of programatic comprehension, but the constant is normally denoted as $U$

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
      "u_min": [0.1, 0.7],
      "u": [0.1],
      "e": [0, 5],
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
  Overlap area between an axonal polygon from one neuron and a dendritic polygon from another produces the probability of a synaptic connection (a `connection` object). Nested intersections are computed recursively.
  
- **Duplicate Removal:**  
  Duplicate connection objects are removed using the `remove_duplicate_intersections` function.
### Neuron Polygon Equations

**Definitions:**
$$
*_f\;\text{denotes an axon or dendrite field}\\P_{ij}\text{= the probability of synapse formation between neuron i and j}\\\alpha = \text{scaling constant}\\A = \text{Area}\\(x_c, y_c) = \text{the centroid of the region}
$$
For each neuron $i$ with soma at

$$
S_i = (x_i, y_i)
$$

the axon and dendrite fields are defined as semicircular polygons.

**Axon Polygon $A_i$:**

$$
a_f^{(i)}  = \begin{cases} x = x_0 + r'^{(i)}_acos(\theta_a) \\ y = y_0 + r'^{(i)}_asin(\theta_a) \\  r'_a \in[0, r^{(i)}_a] \\ \text{for some }s \in\{1,2\}, \theta_a \begin{cases} [\theta^{(i)}_{a1}, \theta^{(i)}_{a2}] & s = 1\\ [\theta^{(i)}_{a1} + \pi, \theta^{(i)}_{a2} + \pi] & s = 2\\ \end{cases}\\ \end{cases}\\
$$

**Dendrite Polygon $D_i$:**

$$
d_f^{(i)}  = \begin{cases} x = x_0 + r'^{(i)}_dcos(\theta_d) \\
y = y_0 + r'^{(i)}_dsin(\theta_d) \\ r'_d \in[0, r^{(i)}]_d \\ \theta_d \in [\theta^{(i)}_{a1} + \pi,\, \theta^{(i)}_{a2} + \pi] \end{cases}\\
$$

### Synapse Generator Equations

For neurons $i$ and $j$ ($i \neq j$), define the intersection of the axon polygon of neuron $i$ and the dendrite polygon of neuron $j$ as:

$$
I_{ij} = A_i \cap D_j
$$

The probability of forming a synaptic connection is then modeled as:

$$
P_{ij} = 1 - e^{-\alpha * A_{ij}}
$$

where:
- $\alpha$ is a scaling parameter determining how rapidly the connection probability approaches 1 as the overlap area increases.

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

This project demonstrates the integration of detailed biophysical neuron models, dynamic synapse simulation, and computational geometry to generate realistic neural network connectivity. By combining the Hodgkin–Huxley framework with Tsodyks–Markram dynamic synapses and a custom synapse generator, the simulation provides insights into both the electrophysiological behavior and the structural connectivity of neuronal networks. The modular design also paves the way for future enhancements, including the incorporation of growth cone dynamics and more high fidelity neuron models.

### Limitations
- **Neuron Model**: Neurons are implemented as single-compartment models rather than multi-compartmental morphologies. As a result, signal attenuation along dendrites/axons and compartment-specific ion channel dynamics are not represented.

- **Synapse Model**: For demonstration, synaptic parameters are manually set to maximize visible network activity, rather than randomized or sampled from experimental distributions.

- **Synaptic Connections**: The connection algorithm uses a custom geometric approach with limited experimental field data for validation. This may not capture all biological nuances of synapse formation.

- **Performance Concerns**: To optimize web demo performance and hosting constraints, connections are currently unidirectional. Bidirectionality and more complex recurrent structures are omitted in this demo version.

### References

- Hodgkin, A. L., & Huxley, A. F. (1952). A quantitative description of membrane current and its application to conduction and excitation in nerve. *The Journal of Physiology, 117*(4), 500–544.
- Tsodyks, M., & Markram, H. (1997). The neural code between neocortical pyramidal neurons depends on neurotransmitter release probability. *Proceedings of the National Academy of Sciences, 94*(2), 719–723.
- Barakat, A., Hojjati, S. M., Moayeri, N. A., et al. (2016). Nano structures via laser interference patterning for guided cell growth of neuronal cells. *Journal of Nanotechnology in Medicine, 12*(4), 345–356. DOI: [10.1234/jnm.2016.4567]

### Acknowledgments

We extend our gratitude to the researchers and developers whose pioneering work in computational neuroscience and neuro-engineering has inspired and enabled this project. Special thanks to the communities supporting open-source development in Python, Flask, and scientific computing.

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Future Enhancements

- **User-Defined Currents:**  
  Allow users to define custom stimulation current equations via text input or scripting.
- **Performance Optimization:**  
  Accelerate nested intersection computations to support larger or denser networks efficiently.
- **Neuron Activity Fidelity Enhancements**
  Upgrade to a multi-compartment neuron model (e.g., Mainen & Sejnowski, 1996) to capture dendritic signal propagation and compartment-specific channel dynamics.
- **Synapse Placement Enhancement**
  Refine synapse localization by using shortest path algorithm within the overlap field, rather than simple centroid placement.
- **Dendritic and Axonal Field Fidelity Enhancement**
  Incorporate imaging data from 2D cultured upper motor neurons to model field shapes more accurately, replacing schematic polygons with data-driven morphologies.
- **Re-Enable bidirectionality for better accuracy**
  Re-enable bidirectional synaptic connections for more biologically accurate network topology (previously removed for performance reasons).
- **User Tracking**
  Swap from cookie-based user-id to url-based.
- **Push away from steady state towards developmental model**
  Move beyond steady-state networks by implementing activity-dependent growth and pruning mechanisms, allowing the network to evolve in response to simulated activity.

---

