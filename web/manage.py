from flask import Flask, request, render_template, redirect
import sys, os
from cachetools import TTLCache

max_users = 20
sim_timeout = 120 #120 seconds

#times out instances after some time
sims_cache = TTLCache(max_users, sim_timeout) 

#Overflow could be initialized on request
#for now limited usercount

app = Flask(__name__)


#Template Fetchers

@app.route("/")
def page_load():
    return redirect("/home")

@app.route("/graph")
def get_graph_template():
    return render_template("main_graph.html")

@app.route("/nav")
def get_nav_template():
    return render_template("nav.html")

@app.route("/home")
def home():
    return render_template("home.html")


    





"""
@app.route("/templates/<path:filename>")
def templates(filename):
    #for dynamically passing html templates via urlfor so they can get renderd with jinja as they are passed
    return render_template("graph.html")
"""
@app.route("/simulation", methods=['GET'])
def simulation():
    return "<script>fetch(`${window.location.href}/sim_data`,{method :'post'})</script>"

@app.route("/simulation/sim_data", methods=["POST"])
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