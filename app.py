from flask import Flask, request, render_template, redirect, jsonify, make_response
import uuid, time

import driver

# Global simulation instance (for now, limited to one user).
sim_instances = {}

app = Flask(__name__)

@app.route("/")
def page_load():
    """Redirects the root URL to the home page."""
    return redirect("/home")

@app.route("/nav")
def get_nav_template():
    """Returns the navigation template."""
    try:
        return render_template("nav.html")
    except Exception as e:
        app.logger.error("Error rendering nav template: %s", e)
        return jsonify({"error": "Could not load navigation template"}), 500

@app.route("/simulation")
def get_graph_template():
    """
    Returns the main simulation page by injecting the simulation 
    template into the background template.
    """
    try:
        return render_template("background.html", page_name="simulation.html")
    except Exception as e:
        app.logger.error("Error rendering simulation template: %s", e)
        return jsonify({"error": "Could not load simulation template"}), 500

@app.route("/simulation/iterateSim", methods=['POST'])
def iterate_sim():
    """
    Iterates the simulation by running a small number of steps (100ms worth)
    and returns a JSON representation of the updated simulation state.
    """
    
    username = request.cookies.get("username")
    sim = sim_instances[username]["sim"]
    sim_instances[username]["last_interaction"] = time.time()
    try:
        if sim is None:
            raise ValueError("Simulation not initialized")
        num_steps = int(0.1 / sim.dt)
        graphing_params = sim.iterate(num_steps)

        vs = graphing_params["vs"]
        input_currents = graphing_params["input_currents"]
        synaptic_inputs = graphing_params["synaptic_inputs"]

        sim_dict = sim.generate_model_dict()

        # Update each neuron's data.
        for i in range(sim.num_neurons):
            sim_dict["neurons"][i]["vs"] = vs[i]
            sim_dict["neurons"][i]["input_currents"] = input_currents[i]
            sim_dict["neurons"][i]["synaptic_inputs"] = synaptic_inputs[i]

        return jsonify(sim_dict)
    except Exception as e:
        app.logger.error("Error iterating simulation: %s", e)
        return jsonify({"error": str(e)}), 500

@app.route("/simulation/setCurrent", methods=['POST'])
def set_current():
    """
    Receives current stimulation parameters from the client, applies
    them to the corresponding neurons, and returns the updated simulation state.
    """
    username = request.cookies.get("username")
    sim = sim_instances[username]["sim"]
    sim_instances[username]["last_interaction"] = time.time()
    try:
        if sim is None:
            raise ValueError("Simulation not initialized")
        data = request.get_json()
        if not data:
            raise ValueError("No current data provided")
        # Iterate through each neuron in the data.
        for neuron_index in data:
            stim_params = data[neuron_index]
            neuron_stim_type = stim_params["currentType"]
            neuron_index_int = int(neuron_index)
            neuron = sim.neuron_models[neuron_index_int]

            app.logger.info(f"Applying stimulation: {stim_params}")

            if neuron_stim_type == "Square":
                neuron.set_square_current(stim_params["freq"], stim_params["maxCurrent"])
            elif neuron_stim_type == "Sin":
                neuron.set_sin_current(stim_params["freq"], stim_params["maxCurrent"]/2)
            elif neuron_stim_type == "Constant":
                neuron.set_const_current(stim_params["maxCurrent"])
            elif neuron_stim_type == "None":
                neuron.set_no_current()
            else:
                app.logger.warning(f"Unknown stimulation type: {neuron_stim_type}")

        return jsonify(sim.generate_model_dict())
    except Exception as e:
        app.logger.error("Error setting current: %s", e)
        return jsonify({"error": str(e)}), 500

@app.route("/simulation/startSim", methods=['POST'])
def setup_sim():
    """
    Initializes the simulation with the specified number of neurons and 
    culture dimensions. Returns the initial simulation state as JSON.
    """
    try:
        data = request.get_json()
        num_neurons = 0
        if not data:
            app.logger.warning("No simulation setup data received")
            return jsonify({"error": "No data received"}), 400
        num_neurons_err = False
        try:
            num_neurons = int(data["numNeurons"]) 
            if num_neurons <= 0:
                num_neurons_err = True
            
        except Exception as e:
            app.logger.error("Unable to make empty simulation")
            num_neurons_err

        if num_neurons_err:
            num_neurons = 1
            
    
        culture_dimensions = data["dimensions"]

        sim = driver.create_sim(num_neurons,
                                float(culture_dimensions["x"]),
                                float(culture_dimensions["y"]))
        
        resp = make_response(jsonify(sim.generate_model_dict()))

        user = str(uuid.uuid4())
        sim_instances[user] = {"sim":sim, "last_interaction": time.time()}
        resp.set_cookie("username", user)

        return resp
    except Exception as e:
        app.logger.error("Error setting up simulation: %s", e)
        return jsonify({"error": str(e)}), 500

@app.route("/home")
def home():
    """Returns the home page by injecting the home template into the background."""
    print(sim_instances)
    for key in sim_instances:
        #clean up all old instances when home page is loaded 
        
        last_interaction = sim_instances[key]["last_interaction"]
        cur_time = time.time()

        elapsed_time = cur_time - last_interaction
        elapsed_minutes = elapsed_time/60

        if elapsed_minutes > 10:
            sim_instances[key] = {}
        
    try:
        return render_template("background.html", page_name="home.html")
    except Exception as e:
        app.logger.error("Error rendering home page: %s", e)
        return jsonify({"error": "Could not load home page"}), 500

@app.route("/about")
def about():
    """Returns the about page by injecting the about template into the background."""
    try:
        return render_template("background.html", page_name="about.html")
    except Exception as e:
        app.logger.error("Error rendering about page: %s", e)
        return jsonify({"error": "Could not load about page"}), 500

if __name__ == '__main__':
    app.run(debug=True)
