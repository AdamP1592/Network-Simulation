
import {hsbColorRangeFinder} from './color_functions.js'

var chart;
//setup for 0: [1, 4, 5], 1: [5, 2], 2:[ 3, 5], 3: [4, 5]
const connections = {n0:["s0"], n2:["s1"], s0:["n2", "n1"],  s1:["n4", "n3", "n5"]}
var rightClickX;
var rightClickY;

var paused = false;

var electrodes = []

var addedElectrodes = 0

let updateTimeout;

function pauseRender(){
    let switchClass = {pause:"play", play:"pause"}
    let switchPause = {pause:false, play:true}
    let btn = document.getElementById("pause_button");
    
    paused = switchPause[btn.className];

    btn.className = switchClass[btn.className]
    
}
var isDragging = false
document.addEventListener("DOMContentLoaded",setUpNetwork);
function rgbToCss(rgbArray) {
    return `rgb(${rgbArray[0]}, ${rgbArray[1]}, ${rgbArray[2]})`;
}

function clean_data(neurons, synapses){
    //combines all the neurons and synapses into one dictionary to used for storing positions
    //and style for the display
    let nodes = {}
    for (let neuron_ind in neurons){
        let neuron_name = "n" + String(neuron_ind)

        let neuron = neurons[neuron_ind]
        let neuron_params = neuron["neuron_params"]

        let color = hsbColorRangeFinder(0, 70, neuron_params["vrest"], neuron_params["vthresh"], neuron_params["v"])
        
        let x = neuron_params["x"]
        let y = neuron_params["y"]

        nodes[neuron_name] = {position:[x, y], color:color }
    }
    for (let syn_ind in synapses){
        let synapse_name = "s" + String(syn_ind)

        let synapse = synapses[syn_ind]
        let synapse_params = synapse["params"]

        let color = "#61a0a8"
        
        let x = synapse_params["x"]
        let y = synapse_params["y"]

        nodes[synapse_name] = {position:[x, y], color:color }
    }
    return nodes
}   

function get_connections(synapses){

    //generates a dict of connections, splitting out synapses as independent nodes
    let connection_dict = {}
    console.log("Pulling Connections...")
    for (let syn_key in synapses){

        let syn = synapses[syn_key]
        
        let synapse_name = "s" + syn_key;

        let con = syn["connections"]

        let pre_syn = con["pre"]
        let post_syn = con["post"]

        
        //iterate through all pre_syn neurons.
        //Create connections for each neuron that points to this synapse
        for (let neuron_ind in pre_syn){

            let neuron_name = "n" + pre_syn[neuron_ind];
            if(connection_dict[neuron_name] === undefined){
                connection_dict[neuron_name] = [];
            }
            connection_dict[neuron_name].push(synapse_name)
        }
        //create connection for all the neurons this synapse points to

        let post_syn_names = post_syn.map(element => "n" + element)
        connection_dict[synapse_name] = post_syn_names

    }
    return connection_dict;
}

function iterateSim(){
    if (!paused){
        
        fetch('/simulation/iterateSim', {
            method:'POST',

        }).then( response => {
            if(!response.ok){
                throw new Error("Response was not ok");
            }
            return response.json();


        }).then(data => {
            console.log("Recieved data:",  data)

            let neurons = data["neurons"]
            let synapses = data["synapses"]
            
            let pos_dict = clean_data(neurons, synapses);
            let con_dict = get_connections(synapses)
            
            updateGraph(pos_dict, con_dict)
        }).catch((error)=>{
            console.error("Error:", error);
        });
    }else{
        setTimeout(iterateSim, 1000)
    }
}
function setUpNetwork(){
    let btn = document.getElementById("pause_button");
    btn.addEventListener('click',pauseRender)

    let numNeurons = prompt("Please enter number of neurons:", "0");

    let networkParams = {"numNeurons": numNeurons, dimensions:{x:"5", y:"5"}};
    fetch('/simulation/startSim',{
        method:'POST',
        headers: {
            "Content-Type" : 'application/json'

        },
        body: JSON.stringify(networkParams)
    }).then( response => {
        if(!response.ok){
            throw new Error("Response was not ok");
        }
        return response.json();


    }).then(data => {

        console.log("Recieved data:",  data)

        let neurons = data["neurons"]
        let synapses = data["synapses"]

        let pos_dict = clean_data(neurons, synapses);
        let con_dict = get_connections(synapses)

        buildGraphs(pos_dict, con_dict)

    }).catch((error)=>{
        console.error("Error:", error);
    });
}


//data processing
function position_to_data_arr(positions){
    let position_ls = [];
    let symbols = {n:"circle", s:"rect"};
    let symbolSizes = {n:25, s:20};
    for (let name in positions){
        
        let pos_container = positions[name];
        let color = "#4287f5";

        if(name[0] == 'n'){
            color = rgbToCss(positions[name]["color"]);
        }

        let position_obj = 
        {
            name:name.toString(),
            value:[positions[name]["position"][0], positions[name]["position"][1]],
            
            //text
            label: {formatter:name.toString(), color:"#000000"},

            //symbol style
            symbol: symbols[name[0]],
            symbolSize:symbolSizes[name[0]],

            itemStyle:{color: color}

        }
        position_ls.push(position_obj)
    };
    return position_ls
}

function dragEvent(event){
    console.log(event)
}
function nodeClicked(params){
    console.log("Node Clicked: ", params)

    let nodeName = params["data"]["name"]
    if(params["componentIndex"] == 0 && nodeName[0] == "e"){//if main graph and node is electrode
        for(let electrodeIndex in electrodes){
            if(electrodes[electrodeIndex]["name"] == nodeName){
                electrodes.splice(electrodeIndex, 1);
            }
        }
    }
}
function rightClick(event){
    rightClickX = event.event.clientX;
    rightClickY = event.event.clientY;
}
function nodeRightClick(event){
    
    if (event.name[0] != "e"){
        return;
    }
   
    let customMenuElem = document.getElementById("customContextMenuHolder");
    let clickPosition = event.value;

    let [x, y] = [rightClickX, rightClickY];

    console.log(x,y)
    customMenuElem.style.left = x + "px";
    customMenuElem.style.top = y + "px";
    customMenuElem.style.display = "flex";

}
function chartClicked(event){
    // Convert click position to chart coordinates
    let width = 50;
    let height = 50;

    let pointInPixel = [event.offsetX, event.offsetY];
    let pointIsInGrid = chart.containPixel({ seriesIndex: 0}, pointInPixel)
    let pixelToGrid = chart.convertFromPixel({seriesIndex: 0}, pointInPixel);

    
    if (!event["target"] && pointIsInGrid) {
        console.log("Adding");
        
        electrodes.push({
            name: `e${addedElectrodes}`,
            symbol: "rect",
            value:[pixelToGrid[0], pixelToGrid[1]],

            symbolSize:[width, height],
            style: { fill: "rgb(112, 112, 112)" }, // Semi-transparent green
            z: -1 // Ensure it's behind the neurons
        })
        addedElectrodes += 1
        // Add a shape at the clicked position
        
    }
}
function get_connection_list(connections){
    
    let connection_list = [];
    for (let key in connections){
        connections[key].forEach(output => {
            connection_list.push({ source: key.toString(), target: output.toString() });
        });
    }
    return connection_list
}

function buildGraphs(positions, connections) {

    let chart_container = document.getElementById('chart_container')


    chart_container.addEventListener('contextmenu', function(e) {
        e.preventDefault();
      });
    chart = echarts.init(chart_container);
    
    chart.getZr().on('click',chartClicked);
    chart.on('click', nodeClicked);
    chart.on('contextmenu', nodeRightClick);
    chart.getZr().on('contextmenu', rightClick);
    var option = {
        title: [
            { text: "Neuron Activity", left: "10%", top: "5%" }, // Left chart title
            { text: "Membrane Potential", left: "60%", top: "5%" }, // Right top title
            { text: "Synapse Dynamics", left: "60%", top: "55%" } // Right bottom title
        ],

        // Define multiple grids (areas for sub-charts)
        grid: [
            { left: "5%", right: "45%", top: "10%", bottom: "10%" }, // Left (big) chart
            { left: "65%", right: "5%", top: "10%", height: "35%" }, // Right top chart
            { left: "65%", right: "5%", top: "55%", height: "35%" }  // Right bottom chart
        ],

        // Define X-Axes (One for each chart)
        xAxis: [
            { type: "value", gridIndex: 0}, //Left chart
            { type: "category", gridIndex: 1, data: ["T1", "T2", "T3"] }, // Right top chart
            { type: "category", gridIndex: 2, data: ["T1", "T2", "T3"] }  // Right bottom chart
        ],

        // Define Y-Axes (One for each chart)
        yAxis: [
            { type: "value", gridIndex: 0}, //left chart
            { type: "value", gridIndex: 1}, // Right top chart
            { type: "value", gridIndex: 2}  // Right bottom chart
        ],
        dataZoom: [
            { type: 'inside', xAxisIndex: [0]},{ type: 'inside', yAxisIndex: [0]}
        ],


        // Define Series (Assigning Data to Different Grids)
        tooltip: { 
            trigger:"item",
            formatter: function (params) {
                if (params.dataType === "node") {
                    if(params.name.includes("n")){
                        return `Neuron: <b>${params.name}</b><br>Position: (${params.value[0]}, ${params.value[1]})`;
                    } else{
                        return `Synapse: <b>${params.name}</b><br>Position: (${params.value[0]}, ${params.value[1]})`;
                    }
                
                } else if (params.dataType === "edge") {
                    
                    return `Synapse: <b>${params.data.source} → ${params.data.target}</b>`;
                }
            }
        },
        series:buildSeries(positions, connections),
    };
    // Apply options
    if (chart){
        chart.setOption(option);
    }else{
        console.error("Echart instance failed to init")
    }
    updateGraph(positions, connections)

}
function buildSeries(positions, connections){
    let cons = get_connection_list(connections);
    let pos_ls = position_to_data_arr(positions);

    //why the do I have to do this, concat refused to work.
    electrodes.map(electrode => pos_ls.push(electrode))

    let series= [
        {   

            roam: "enabled", 
            //meta
            name: "Neuron Activity", 
            type: "graph", 

            //positon
            xAxisIndex: 0,
            yAxisIndex: 0,

            //charting settings
            layout: "force",
            coordinateSystem: 'cartesian2d',

            //symbol style
            symbolSize: 30, 
            label: {
                show: true,
                fontSize:14 
            }, 

            //edge style
            edgeSymbol: ['circle', 'arrow'], 
            edgeSymbolSize: [4, 8], 

            //data
            data: pos_ls,
            links: cons,

            lineStyle:{
                color:"#000000"
            },

        },
        { name: "Membrane Potential", type: "line", data: [2, 4, 3], xAxisIndex: 1, yAxisIndex: 1 }, // Right top chart
        { name: "Synapse Dynamics", type: "bar", data: [5, 2, 6], xAxisIndex: 2, yAxisIndex: 2 }  // Right bottom chart
    ]
    return series;
}


function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
function verifyUpdate(data, oldData){

}
function updateGraph(positions, connections){
    let series = buildSeries(positions, connections)
    clearTimeout(updateTimeout)

    chart.setOption({
        series:series,
        animation: false
    });
    requestAnimationFrame(() => {
        iterateSim()
    })
    

       
}
