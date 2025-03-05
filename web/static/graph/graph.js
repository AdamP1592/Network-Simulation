
import {hsbColorRangeFinder} from './color_functions.js'
import {getElectrodeChanges} from './contextMenu.js'


document.addEventListener("DOMContentLoaded",setUpNetwork);
var chart;
//setup for 0: [1, 4, 5], 1: [5, 2], 2:[ 3, 5], 3: [4, 5]
const connections = {n0:["s0"], n2:["s1"], s0:["n2", "n1"],  s1:["n4", "n3", "n5"]}

var rightClickTarget = null;

var rightClickX;
var rightClickY;

var paused = false;

var electrodes = [];
var addedElectrodes = 0;

var curTime = Date.now();


export function getTarget(){
    return rightClickTarget;
}

function pauseRender(){
    //branchless approach
    let switchClass = {pause:"play", play:"pause"}
    let switchPause = {pause:false, play:true}
    let btn = document.getElementById("pause_button");
    
    paused = switchPause[btn.className];

    btn.className = switchClass[btn.className]
    
}
var isDragging = false
function rgbToCss(rgbArray) {
    return `rgb(${rgbArray[0]}, ${rgbArray[1]}, ${rgbArray[2]})`;
}

//processes neuron and synapse data into an object containing each datapoint
function clean_data(neurons, synapses){
    //combines all the neurons and synapses into one dictionary to used for storing positions
    //and style for the display
    let nodes = {}
    for (let neuron_ind in neurons){
        let neuron_name = "n" + String(neuron_ind)

        let neuron = neurons[neuron_ind]
        let neuron_params = neuron["neuron_params"]

        let color = hsbColorRangeFinder(0, 70, neuron_params["vrest"] - 1, neuron_params["vthresh"], neuron_params["v"])
        
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
    //console.log("Pulling Connections...")
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
            //console.log("Recieved data:",  data)
            
            updateGraph(data)
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

        buildGraphs(data)

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
            inputCurrents:"none",
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
function removeElectrode(nodeName){
    let currentData = {currentType: "None"};
    //remove electrode with the name nodeName from electrodes and
    //remove current from each neuron in simulation
    for(let electrodeIndex in electrodes){
        let electrode = electrodes[electrodeIndex];

        //find electrode in the electrode dict
        if(electrode["name"] == nodeName){
            //since electrode is getting removed, create dict to set all the neurons currents
            let data = {};
            for(let neuronNameIndex in electrode["connectedNeurons"]){
                //set each neuron in connected neurn to no current
                let neuronIndex = electrode["connectedNeurons"][neuronNameIndex][1];
                data[neuronIndex] = currentData;
            }

            //send updates to server
            addCurrent(data);
            //remove electrode from dict
            electrodes.splice(electrodeIndex, 1);

        }
    }

}

function nodeClicked(params){
    let nodeName = params["data"]["name"];

    //if event is a part of the first component(main graph)
    if(params["componentIndex"] == 0){

        switch(nodeName[0]){
            //if electrode is clicked
            case "e":
                removeElectrode(nodeName);
                break;
            case "n":
                focusNeuron(nodeName);
                break;
            case "s":
                //do synapse thing
                break;
            default:
                console.warn(`Warning: Unknown nodeType:${nodeName} detected`)
                break;
        }
    }
}
function rightClick(event){

    //sets global right click x and y based on pixel position
    rightClickX = event.event.clientX;
    rightClickY = event.event.clientY;
}
function nodeRightClick(event){
    //console.log(event)
    //catch case if non electrode node is clicked
    if (event.name[0] != "e"){
        return;
    }

    rightClickTarget = event.name; 

    let customMenuElem = document.getElementById("customContextMenuHolder");
    let clickPosition = event.value;

    let [x, y] = [rightClickX, rightClickY];

    customMenuElem.style.left = x + "px";
    customMenuElem.style.top = y + "px";
    customMenuElem.style.display = "flex";
}

function getNeuronsInsideRect(pixelCenterCoords, width, height){
    //could do the whole collision between circles and rectangles based on the tan line
    //of the circle and the closest point on the rect but point neurons are easier.
    //console.log(pixelCenterCoords)
    
    let electrodeBottom = pixelCenterCoords[1] + (height/2);
    let electrodeLeft = pixelCenterCoords[0] - (width/2);

    let electrodeTop = electrodeBottom - height;
    let electrodeRight = electrodeLeft + width;

    let seriesData = chart.getOption().series[1].data
    let neuronsInElectrodes = []

    for(let key in seriesData){

        let datapoint = seriesData[key]
        let dataName = datapoint.name

        //only neurons
        if(dataName[0] != "n"){
            continue;
        }

        let pos = datapoint.value

        let [pixelX, pixelY] = chart.convertToPixel({seriesIndex:0}, pos)
        //console.log(pixelX, pixelY)
        if (pixelX >= electrodeLeft && pixelX <= electrodeRight && 
            pixelY >= electrodeTop && pixelY <= electrodeBottom) {
            neuronsInElectrodes.push(dataName)
           // console.log("neuronInElectrode")
        }

    }
    return neuronsInElectrodes;
}

function chartClicked(event){
    if(event.target){
        return
    }
    // Convert click position to chart coordinates
    let width = Number(document.getElementById("electrode_width").value);
    let height = Number(document.getElementById("electrode_height").value);

    let pointInPixel = [event.offsetX, event.offsetY];
    let pointIsInGrid = chart.containPixel({ seriesIndex: 0}, pointInPixel);
    let pixelToGrid = chart.convertFromPixel({seriesIndex: 0}, pointInPixel);

    
    if (pointIsInGrid) {
        //pulling data from the chart
        let neuronsInBounds = getNeuronsInsideRect(pointInPixel, width, height)
        //gets the electrodes position
        //console.log("Adding");
        let electrode = {
            name: `e${addedElectrodes}`,
            symbol: "rect",
            value:[pixelToGrid[0], pixelToGrid[1]],
            current:"none",
            currentType:"none",
            freq:"none",
            connectedNeurons: neuronsInBounds,

            symbolSize:[width, height],
            style: { fill: "rgb(112, 112, 112)" }
        }
        electrodes.push(electrode)
        //console.log(electrode)
        addedElectrodes += 1
        
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

function buildGraphs(simDict) {

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
            { text: "Network Activity", left: "5%", top: "5%" }, // Left chart title
            { text: "Neuron Dynamics", left: "60%", top: "5%" }, // Right top title
            { text: "Input Current", left: "60%", top: "50%" } // Right bottom title
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
        series:buildSeries(simDict),
    };
    // Apply options
    if (chart){
        chart.setOption(option);
    }else{
        console.error("Echart instance failed to init")
    }
    updateGraph(simDict)

}
function addCurrent(currentDict){
    
    console.log("Adding current", currentDict)

    fetch('/simulation/setCurrent', {
        method:'POST',
        headers:{
            'Content-Type': 'application/json'
        },
        body:JSON.stringify(currentDict)
    })
    
}

function electrodeBuilder(electrodeChanges){
    //apply changes from contextMenu to electrodes. NEEDS TO APPLY CHANGES TO NEURON
    electrodes.forEach((electrode)=>{
        if(electrodeChanges[electrode.name]){
            //merge dicts

            for(let key in electrodeChanges[electrode.name]){ 
                electrode[key] = electrodeChanges[electrode.name][key];
            }
            let currentBuilder = {}
            for(let i in electrode["connectedNeurons"]){
                let neuronName = electrode["connectedNeurons"][i] 
                //neuronIndex
                currentBuilder[neuronName[1]] = electrodeChanges[electrode.name]
                
            }
            //console.log(currentBuilder)
            addCurrent(currentBuilder)
        }
    });
}
function buildSeries(simDict){

    let neurons = simDict["neurons"]
    let synapses = simDict["synapses"]
    
    let pos_dict = clean_data(neurons, synapses);
    let con_dict = get_connections(synapses)

    let electrodeChanges = getElectrodeChanges()
    electrodeBuilder(electrodeChanges)

    let cons = get_connection_list(con_dict);
    let pos_ls = position_to_data_arr(pos_dict);

    
    //why the do I have to do this, concat refused to work.

    //electrodes.map(electrode => pos_ls.push(electrode))

    let series= [
        {  
        //electrode graph placed behind neuron activity
        roam: "enabled", 
        type: "graph", 

        //positon
        xAxisIndex: 0,
        yAxisIndex: 0,
        z:0,
        zlevel:0,

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
        data: electrodes,

        },
        {   

            roam: "enabled", 
            //meta
            name: "Neuron Activity", 
            type: "graph", 

            //positon
            xAxisIndex: 0,
            yAxisIndex: 0,
            z:10,
            zlevel:0,

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

function updateGraph(simData){

    let newTime = Date.now();

    //split data into equal portions of numSteps
    //build a series with options for each step
    //run each series as an option with an animation that fills durration
    //halfway through the animation at the middlemost or just prior to the middlemost
    //timestep pull the data for the next animation
    //once the last update is called, build a new series with the new options.

    let series = buildSeries(simData);    
    
    let timeDifferencePerUpdate = newTime - curTime;
    let updateTime = 5000; // each update is 5 seconds in sim time

    //dynamic number of steps based on the passed step time

    let updateTimeToTimeDifferenceRatio = Math.trunc(updateTime / timeDifferencePerUpdate);
    
    console.log(numSteps)

    curTime = Date.now()
    chart.setOption({
        series:series,
        animation: false
    });
    
    requestAnimationFrame(() => {
        let newTime = Date.now();
        iterateSim()
    });
}
