
import {hsbColorRangeFinder} from './color_functions.js'
import {interpolate} from './color_functions.js'

import {getElectrodeChanges} from './contextMenu.js'

import {iterateSim} from './comms.js'

import {setUpNetwork} from './comms.js'
import {addCurrent} from './comms.js'



document.addEventListener("DOMContentLoaded",setUpNetwork);
var chart;

var rightClickTarget = null;

var neuronTarget = 0;

var rightClickX;
var rightClickY;

var paused = false;

var electrodes = [];
var addedElectrodes = 0;

var curTime = Date.now();

//exports right click target to get used by context menu
export function getTarget(){
    return rightClickTarget;
}
/*

    SIMPLE HELPER FUNCTIONS

*/

function rgbToCss(rgbArray) {
    return `rgb(${rgbArray[0]}, ${rgbArray[1]}, ${rgbArray[2]})`;
}

export function pauseRender(){
    //branchless approach
    let switchClass = {pause:"play", play:"pause"}
    let switchPause = {pause:false, play:true}
    let btn = document.getElementById("pause_button");
    
    paused = switchPause[btn.className];

    btn.className = switchClass[btn.className]
    
}


/*

    DATA HELPER FUNCTIONS

*/
/**  
 * extracts params for main graph from a neuron or a synapse type
 * @param {object} object
 * @param {string} paramType

**/
function dataBuilder(objs, paramType){
    
    let position_ls = [];
    let target =  `n${neuronTarget}`

    let symbols = {n:"circle", s:"rect"};
    let symbolSizes = {n:25, s:20};

    for(let objIndex in objs){

        //paramTypes[paramType] = 'neuron_params' or 'synapse_params
        let params = objs[objIndex].params

        //graph data
        let nodeName = paramType + String(objIndex);
        let x = params.x
        let y = params.y
        let cssColor = "#4287f5";
        if(paramType === "n"){
            let rgbColor = hsbColorRangeFinder(0, 70, params["vrest"] - 1, params["vthresh"], params["v"]);
            cssColor = rgbToCss(rgbColor);
        }
        

        let position_obj = 
        {
            name:nodeName.toString(),
            value:[x, y],
            inputCurrents:"none",
            //text
            label: {formatter:nodeName.toString(), color:"#000000"},

            //symbol style
            symbol: symbols[paramType],
            symbolSize: symbolSizes[paramType],

            itemStyle:{
                color: cssColor,
                borderColor:"#000000",
                borderWidth: 1.5 * Number(nodeName == target)
            }

        }
        position_ls.push(position_obj)
    
    }
    return position_ls


}
function position_to_data_arr(neurons, synapses){

    let neuronData = dataBuilder(neurons, "n");
    let synapseData = dataBuilder(synapses, "s");
    
    let nodeData = neuronData.concat(synapseData);
    return nodeData
    
}
function get_connection_list(synapses){

    let connection_list = [];

    for(let synapseIndex in synapses){
        let cons = synapses[synapseIndex].connections

        let preSynConnections = cons["pre"]
        let postSynConnections = cons["post"]

        let synapseName = "s" + String(synapseIndex);

        preSynConnections.forEach(neuronIndex => {
            let neuronName = "n" + String(neuronIndex);
            connection_list.push({ source : neuronName, target:synapseName});
        });
        postSynConnections.forEach(neuronIndex => {
            let neuronName = "n" + String(neuronIndex);
            connection_list.push({ source : synapseName, target:neuronName});

        });
    }

    return connection_list
}


/*

    SIM UPDATE FUNCTIONS

*/

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
/*

    GRAPHIC EVENT FUNCTIONS

*/
function focusNeuron(nodeName){
    
    neuronTarget = parseInt(nodeName.substring(1))
    console.log(neuronTarget)
}
function nodeClicked(params){
    let nodeName = params["data"]["name"];

    //if event is a part of the first component(main graph)

    console.log(params)
    if(params["seriesIndex"] < 2){
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

/*

    GRAPHIC BUILDER FUNCTIONS

*/


export function buildGraphs(simDict) {
    let btn = document.getElementById("pause_button");
    btn.addEventListener('click',pauseRender)

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
            { text: "Membrane Potential", left: "60%", top: "5%" }, // Right top title
            { text: "Input stimuli", left: "60%", top: "50%" } // Right bottom title
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
            { type: "value", gridIndex: 1, scale: true}, // Right top chart
            { type: "value", gridIndex: 2, scale: true}  // Right bottom chart
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
                //main graph
                if (params.componentIndex < 2) {
                    if(params.dataType === "node"){
                        switch(params.name[0]){
                            case "n":
                                return `Neuron: <b>${params.name}</b><br>Position: (${params.value[0]}, ${params.value[1]})`;
                            case "s":
                                return `Synapse: <b>${params.name}</b><br>Position: (${params.value[0]}, ${params.value[1]})`;
                            case "e":
                                let neurons = params.data.connectedNeurons
                                let currentType = params.data.currentType
                                return `Connected Neurons: <b>${neurons} </b><br> Current Type: <b>${currentType}</b>`
                        }
                    
                    
                    } else if (params.dataType === "edge") {
                        return `Synapse: <b>${params.data.source} → ${params.data.target}</b>`;
                    }
                }
                else if (params.componentIndex == 2) {
                    return `Membrane Potential: <b>${params.data[1].toFixed(2)}</b> (mV)` 
                }
                else if (params.componentIndex == 3) {
                    return `Synaptic Current: <b>${params.data[1].toFixed(2)}</b> (µA/cm²)` 
                }
                else if (params.componentIndex == 4) {
                    return `Electrode Current: <b>${params.data[1].toFixed(2)}</b> (µA/cm²)` 
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

function buildSeries(simDict){

    
    let neurons = simDict["neurons"]
    let synapses = simDict["synapses"]


    let newTime = Date.now();
    let timeDifferencePerUpdate = newTime - curTime;
    let updateTime = 5000; // each update is 5 seconds in sim time


    //dynamic number of steps based on the passed step time

    let updateTimeToTimeDifferenceRatio = Math.trunc(updateTime / timeDifferencePerUpdate);

    let minSeries = 5; // 1 update every second
    let maxSeries = 50; //5000 seconds means once every 250 ms

    let electrodeChanges = getElectrodeChanges()
    electrodeBuilder(electrodeChanges)

    let cons = get_connection_list(synapses);
    let pos_ls = position_to_data_arr(neurons, synapses);

    
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
            name: "Electrodes", 
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

        //will be the historic membrane potential graph of the "focused" neuro
        { // Right top chart
            name: "Membrane Potential",
            type: "line", data:neurons[neuronTarget].vs,
            xAxisIndex: 1,
            yAxisIndex: 1 
        
        }, 
        //will be the historic input stimuli dynamics(synaptic and electrodes)
        { // Right bottom chart
            name: "Synaptic Dynamics", 
            type: "line", 

            lineStyle: {color: '#000000'},

            data: neurons[neuronTarget].synaptic_inputs,
            xAxisIndex: 2, 
            yAxisIndex: 2 
        },
        { // Right bottom chart
            name: "Input Currents", 
            type: "line", data: neurons[neuronTarget].input_currents, 
            xAxisIndex: 2, 
            yAxisIndex: 2 
        }  
    ]
    return series;
}

function updateFrame(){
    if(paused){
        setTimeout(() => {
            requestAnimationFrame(updateFrame);
        }, 1000 / 30); //30 fps max
        return;
    }
    let newTime = Date.now();
    iterateSim()
}
export function updateGraph(simData){


    //split data into equal portions of numSteps
    //build a series with options for each step
    //run each series as an option with an animation that fills durration
    //halfway through the animation at the middlemost or just prior to the middlemost
    //timestep pull the data for the next animation
    //once the last update is called, build a new series with the new options.

    let series = buildSeries(simData);    
    
    curTime = Date.now()
    chart.setOption({
        series:series,
        animation: false
    });
    
    requestAnimationFrame(updateFrame);
}
