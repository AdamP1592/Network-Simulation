from flask import Flask, request, render_template, redirect, jsonify

import sys, os
from cachetools import TTLCache
num_iterations = 0
#for importing driver
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import driver

max_users = 1
sim_timeout = 120 #120 seconds

#times out instances after some time
sims_cache = TTLCache(max_users, sim_timeout) 

sim = None

#Overflow could be initialized on request
#for now limited usercount

app = Flask(__name__)


#Template Fetchers swap to general fetcher with database
"""
@app.route("/templates/<path:filename>")
def templates(filename):
    #for dynamically passing html templates via urlfor so they can get renderd with jinja as they are passed
    return render_template("graph.html")

    template = render_template("background.html")

    template_connection = "{" + "% include '{}.html' %".format(page_route_str) + "}"

    style_connection = {}

    template = template.replace("%%", template_connection)
"""

import time
def build_page(page_route_str):

    return render_template("background.html")

@app.route("/")
def page_load():
    return redirect("/home")

@app.route("/nav")
def get_nav_template():
    return render_template("nav.html")

@app.route("/simulation")
def get_graph_template():
    return render_template("background.html", page_name=f"simulation.html")

@app.route("/simulation/iterateSim", methods=['POST'])
def iterate_sim():
    global sim
    global num_iterations
    t = time.time()
    ##  get 5 seconds of sim data. Add that to the dict
    num_steps = int(5/sim.dt)
    graphing_params = sim.iterate(num_steps)

    vs = graphing_params["vs"]
    input_currents = graphing_params["input_currents"]
    synaptic_inputs = graphing_params["synaptic_inputs"]

    ## pull 5 seconds of vs from the simulation

    sim_dict = sim.generate_model_dict()
    #loads voltage data into the sim dict based on the number of steps

    for i in range(sim.num_neurons):
        sim_dict["neurons"][i]["vs"] = vs[i]
        sim_dict["neurons"][i]["input_currents"] = input_currents[i]
        sim_dict["neurons"][i]["synaptic_inputs"] = synaptic_inputs[i]


    #num_iterations += 1

    return jsonify(sim_dict)

@app.route("/simulation/setCurrent", methods=['POST'])
def set_current():
    global sim
    data = request.get_json()
    for neuron_index in data:  

        stim_params = data[neuron_index]
        neuron_stim_type = stim_params["currentType"]

        neuron_index = int(neuron_index)

        neuron = sim.neuron_models[neuron_index]

        print(stim_params)
        
        if neuron_stim_type == "Square":
            neuron.set_square_current(stim_params["freq"], stim_params["maxCurrent"])

        elif neuron_stim_type == "Sin":
            neuron.set_sin_current(stim_params["freq"], stim_params["maxCurrent"])

        elif neuron_stim_type == "Constant":
            neuron.set_const_current(stim_params["maxCurrent"])

        elif neuron_stim_type == "None":
            neuron.set_no_current()

    return jsonify(sim.generate_model_dict())

@app.route("/simulation/startSim", methods=['POST'])
def setup_sim():
    global sim
    data = request.get_json()

    if not data:
        app.logger.warning("Error recieving sim setup data")\
    
    num_neurons = int(data["numNeurons"])
    culture_dimensions = data["dimensions"]

    sim = driver.create_sim(num_neurons, float(culture_dimensions["x"]), float(culture_dimensions["y"]))

    return jsonify(sim.generate_model_dict())

@app.route("/home")
def home():
    return render_template("background.html", page_name=f"home.html")

@app.route("/about")
def about():
    return render_template("background.html", page_name=f"about.html")
#Async js requests

@app.route("/simulation/sim_data", methods=["GET"])
def sim_data():


    js_file = ""
    print("./web/templates/dynamic/simulation_data.js")
    with open("/web/templates/home.html") as f:
        js_file = f.readlines()
        print(js_file, file=sys.stderr)
        
    js_file = "<script>" + "\n".join(js_file) + "</script>"
    
    return js_file
    
if __name__ == '__main__':
    app.run(debug=True)