from flask import Flask, request, render_template, redirect, jsonify, make_response
import uuid, time, threading
import driver  # Assuming driver.create_sim and simulation methods are defined here

app = Flask(__name__)

# Global simulation store and lock for thread safety.
simulation_store = {}
store_lock = threading.Lock()

def create_session_cookie(resp):
    """Generate a unique session ID and set it as a cookie."""
    session_id = str(uuid.uuid4())
    # You can set max_age (in seconds) if desired; here we leave it to the browser defaults.
    max_age = 30 * 60
    resp.set_cookie('session_id', session_id, max_age = max_age)
    return session_id

def get_session_id():
    """Retrieve the session ID from the request cookies."""
    return request.cookies.get('session_id')

def clean_up_sessions():
    """Remove sessions that have been idle for more than 10 minutes."""
    current_time = time.time()
    with store_lock:
        for session_id in list(simulation_store.keys()):
            if (current_time - simulation_store[session_id]["last_interaction"]) > 600:  # 600 seconds = 10 minutes
                print("Removing session id:", session_id)
                del simulation_store[session_id]

@app.route("/")
def index():
    # Redirect root to the home page.
    return redirect("/home")

@app.route("/nav")
def get_nav_template():
    try:
        return render_template("nav.html")
    except Exception as e:
        app.logger.error("Error rendering nav template: %s", e)
        return jsonify({"error": "Could not load navigation template"}), 500

@app.route("/simulation")
def get_graph_template():
    # Clean up old sessions before serving the simulation page.
    clean_up_sessions()
    try:
        # Render background.html with simulation.html injected into it.
        return render_template("background.html", page_name="simulation.html")
    except Exception as e:
        app.logger.error("Error rendering simulation template: %s", e)
        return jsonify({"error": "Could not load simulation template"}), 500

@app.route("/simulation/iterateSim", methods=['POST'])
def iterate_simulation():
    session_id = get_session_id()
    if not session_id:
        app.logger.error("Session ID not found")
        return jsonify({"error": "Session ID not found"}), 400

    with store_lock:
        session_data = simulation_store.get(session_id)
    if not session_data:
        return jsonify({"error": "Simulation not initialized"}), 400

    sim = session_data["sim"]

    # Update last interaction time.
    with store_lock:
        simulation_store[session_id]["last_interaction"] = time.time()

    try:
        # Calculate number of steps for 100ms (0.1 seconds) of simulation.
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
    
    session_id = get_session_id()
    if not session_id:
        app.logger.error("Session ID not found")
        return jsonify({"error": "Session ID not found"}), 400

    with store_lock:
        session_data = simulation_store.get(session_id)
    if not session_data:
        return jsonify({"error": "Simulation not initialized"}), 400

    sim = session_data["sim"]

    # Update last interaction time.
    with store_lock:
        simulation_store[session_id]["last_interaction"] = time.time()

    try:
        data = request.get_json()
        if not data:
            raise ValueError("No current data provided")
        # Apply stimulation parameters for each neuron.
        for neuron_index in data:
            stim_params = data[neuron_index]
            neuron_stim_type = stim_params["currentType"]
            neuron_index_int = int(neuron_index)
            neuron = sim.neuron_models[neuron_index_int]

            app.logger.info(f"Applying stimulation: {stim_params}")

            if neuron_stim_type == "Square":
                neuron.set_square_current(stim_params["freq"], stim_params["maxCurrent"])
            elif neuron_stim_type == "Sin":
                neuron.set_sin_current(stim_params["freq"], stim_params["maxCurrent"] / 2)
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
def setup_simulation():
    print(simulation_store)
    session_id = get_session_id()
    data = request.get_json()
    if not data:
        app.logger.warning("No simulation setup data received")
        return jsonify({"error": "No data received"}), 400

    try:
        num_neurons = int(data.get("numNeurons", 1))
    except Exception as e:
        app.logger.error("Invalid number of neurons: %s", e)
        num_neurons = 1

    max_neurons = 25
    num_neurons = min(max(num_neurons, 1), max_neurons)
    culture_dimensions = data["dimensions"]

    sim = driver.create_sim(num_neurons,
                            float(culture_dimensions["x"]),
                            float(culture_dimensions["y"]))

    resp = make_response(jsonify(sim.generate_model_dict()))
    if not session_id:
        session_id = create_session_cookie(resp)

    with store_lock:
        simulation_store[session_id] = {"sim": sim, "last_interaction": time.time()}

    return resp

@app.route("/home")
def home():
    try:
        return render_template("background.html", page_name="home.html")
    except Exception as e:
        app.logger.error("Error rendering home page: %s", e)
        return jsonify({"error": "Could not load home page"}), 500

@app.route("/about")
def about():
    try:
        return render_template("background.html", page_name="about.html")
    except Exception as e:
        app.logger.error("Error rendering about page: %s", e)
        return jsonify({"error": "Could not load about page"}), 500

if __name__ == '__main__':
    app.run(debug=False)
