from flask import Flask, request, render_template, redirect, jsonify
import sys, os
from cachetools import TTLCache

max_users = 1
sim_timeout = 120 #120 seconds

#times out instances after some time
sims_cache = TTLCache(max_users, sim_timeout) 

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


@app.route("/simulation/startSim", methods=['POST'])
def setupSim():
    data = request.get_json()

    if not data:
        app.logger.warning("Error recieving sim setup data")

    numNeurons = data["numNeurons"]
    return render_template("background.html", page_name=f"simulation.html")

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