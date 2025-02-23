
import {hsbColorRangeFinder} from './color_functions.js'

var chart;
//setup for 0: [1, 4, 5], 1: [5, 2], 2:[ 3, 5], 3: [4, 5]
const connections = {n0:["s0"], n2:["s1"], s0:["n2", "n1"],  s1:["n4", "n3", "n5"]}

const neurons = {n0:[5, 10], n1:[30, 10], n2:[10, 30], n3:[40, 20], n4: [30, 45], n5: [45, 50]}

const synapses = {s0:[8, 15], s1:[25, 35]}

const positions = {...neurons, ...synapses}

var electrodes = []

var addedElectrodes = 0

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
    console.log("nodes:", nodes)
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
    fetch('/simulation/iterateSim',{
        method:'POST',

    }).then( response => {
        if(!response.ok){
            throw new Error("Response was not ok");
        }
        return response.json();


    }).then(data => {

        console.log("Success", data);
    }).catch((error)=>{
        console.error("Error:", error);
    });
}
function setUpNetwork(){
    let numNeuronsStr = prompt("Please enter number of neurons:", "0");

    let numNeurons = parseInt(numNeuronsStr);
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

        buildGraphs(con_dict, pos_dict)
        
        console.log("Success", data);
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
        console.log(name[0] == 's');
        let color = "#4287f5";

        if(name[0] == 'n'){
            console.log("Changing color")
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
function chartClicked(event){
    // Convert click position to chart coordinates

    let tempElectrodes = electrodes

    let width = 55;
    let height = 55;


    let pointInPixel = [event.offsetX, event.offsetY];
    let pointInGrid = chart.containPixel({ seriesIndex: 0}, pointInPixel)

    
    if (event["target"]){
        let targetId = event["target"]["id"];
        console.log(targetId)
        
        for(let graphicIndex in electrodes){
            console.log(targetId)
            //index through electrodes to remove input pad
            if( electrodes[graphicIndex]["id"] == targetId){
                electrodes.splice(graphicIndex, 1);
                chart.setOption({
                    graphic:{
                        id: targetId,
                        $action: "remove"
                    }
                });
            }
                
        }
    
    }
    else if (pointInGrid) {
        console.log("Adding");
        let pixelPoint = chart.convertToPixel({ xAxisIndex: 0, yAxisIndex: 0 }, [event.offsetX, event.offsetY]);
        electrodes.push({
            id: `e ${ addedElectrodes}`,
            type: "rect",
            draggable:true,
            shape: {
                x: event.offsetX - width/2,
                y: event.offsetY - height/2, 
                width: width, 
                height: height,
            }, // Radius
            style: { fill: "rgb(112, 112, 112)" }, // Semi-transparent green
            z: -1 // Ensure it's behind the neurons
        })
        addedElectrodes += 1
        // Add a shape at the clicked position
        
    }
    if (tempElectrodes === electrodes){
        chart.setOption({
            graphic: electrodes
        });
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

 function buildGraphs(connections, positions) {

    let chart_container = document.getElementById('chart_container')
    chart = echarts.init(chart_container);
    
    chart.getZr().on('click',chartClicked)


    console.log("Connections: ", connections)
    let cons = get_connection_list(connections);
    let pos_ls = position_to_data_arr(positions);

    console.log("Connection List: ", cons)
    console.log("Positions: ", pos_ls)
    



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

        //zoom and scroll functions
        { type: 'inside', xAxisIndex: [0]},{ type: 'inside', yAxisIndex: [0]},

    ],


        // Define Series (Assigning Data to Different Grids)
        tooltip:{ 
            trigger:"item",
            formatter: function (params) {
                if (params.dataType === "node") {
                    if(params.name.includes("n")){
                        return `Neuron: <b>${params.name}</b><br>Position: (${params.value[0]}, ${params.value[1]})`;
                    } else{
                        console.log(params)
                        return `Synapse: <b>${params.name}</b><br>Position: (${params.value[0]}, ${params.value[1]})`;
                    }
                
                } else if (params.dataType === "edge") {
                    
                    return `Synapse: <b>${params.data.source} → ${params.data.target}</b>`;
                }
            }
        },
        series: [
            {   

                roam: "disabled", 
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
    };
    // Apply options
    if (chart){
        chart.setOption(option);
    }else{
        console.error("Echart instance failed to init")
    }
    iterateSim()
}

