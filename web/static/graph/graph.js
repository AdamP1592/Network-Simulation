

//import * as echarts from 'echarts';
const num_nodes = 6;

const connections = {0: [1, 4, 5], 1: [5, 2], 2:[ 3, 5], 3: [4, 5]}

const positions = {0:[5, 10], 1:[30, 10], 2:[10, 30], 3:[40, 20], 4: [30, 45], 5: [45, 50]}

function position_to_data_arr(positions){
    let position_ls = [];
    for (let name in positions){
        let position_obj = 
        {
            name:name.toString(),
            value:[positions[name][0], positions[name][1]],
            label: "n" + name.toString()
        }
        position_ls.push(position_obj)
    };
    return position_ls
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


document.addEventListener("DOMContentLoaded", function () {

    let chart_container = document.getElementById('chart_container')



    let cons = get_connection_list(connections);
    let pos_ls = position_to_data_arr(positions);

    console.log(cons)
    console.log(pos_ls)
    

    var chart = echarts.init(chart_container);

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

        // Define Series (Assigning Data to Different Grids)
        tooltip:{ 
            trigger:"item",
            formatter: function (params) {
                if (params.dataType === "node") {
                    return `Neuron: <b>${params.name}</b><br>Position: (${params.value[0]}, ${params.value[1]})`;
                } else if (params.dataType === "edge") {
                    return `Synapse: <b>${params.data.source} → ${params.data.target}</b>`;
                }
            }
        },
        series: [
            { 
                //meta
                name: "Neuron Activity", 
                type: "graph", 

                //positon
                xAxisIndex: 0,
                yAxisIndex: 0,

                //charting settings
                layout: "none",
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
    console.log(option)
    // Apply options
    if (chart){
        chart.setOption(option);
    }else{
        console.error("Echart instance failed to init")
    }
    });

