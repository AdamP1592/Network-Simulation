// ------------------------------------------------------------
// Import Dependencies
// ------------------------------------------------------------
import { hsbColorRangeFinder, rgbToCss } from './color_functions.js';
import { getElectrodeChanges } from './contextMenu.js';
import { iterateSim, setUpNetwork, addCurrent } from './comms.js';
import { queue } from './queue.js';

// ------------------------------------------------------------
// Global Variables and Initialization
// ------------------------------------------------------------
document.addEventListener("DOMContentLoaded", setUpNetwork);

// ECharts instance
let chart;

// Baseline and dynamic symbol sizes
const baselineSymbolSizes = [0.3, 0.25];
let symbolSizes = { n: baselineSymbolSizes[0], s: baselineSymbolSizes[1] };

// Global variables for managing right-click events and simulation state
let rightClickTarget = null;
let neuronTarget = 0;
let rightClickX;
let rightClickY;

let paused = false;
let electrodes = [];
let addedElectrodes = 0;

// Data queue to hold simulation updates for side graphs
let dataQueue = new queue();

// ------------------------------------------------------------
// Exports
// ------------------------------------------------------------
/**
 * Returns the current right-click target.
 * @returns {*} The current right-click target.
 */
export function getTarget() {
    return rightClickTarget;
}

/**
 * Toggles the pause/play state of the simulation.
 */
export function pauseRender() {
    const switchClass = { pause: "play", play: "pause" };
    const switchPause = { pause: false, play: true };
    const btn = document.getElementById("pause_button");

    // Update the paused flag and toggle the button's CSS class.
    paused = switchPause[btn.className];
    btn.className = switchClass[btn.className];
}

/**
 * Initializes the chart and builds the initial graph.
 * The provided simDict represents the starting state of the simulation.
 * @param {Object} simDict - The initial simulation state.
 */
export function buildGraphs(simDict) {
    // Enqueue the initial simulation state.
    dataQueue.enqueue(simDict);

    // Set up the pause button listener.
    const btn = document.getElementById("pause_button");
    btn.addEventListener('click', pauseRender);

    // Disable the default context menu on the chart container.
    const chartContainer = document.getElementById('chart_container');
    chartContainer.addEventListener('contextmenu', e => e.preventDefault());

    // Initialize the ECharts instance.
    chart = echarts.init(chartContainer);

    // Attach event handlers for zooming, clicks, and right-clicks.
    chart.on('dataZoom', updateSymbolSizesRelativeToGrid);
    chart.getZr().on('click', chartClicked);
    chart.on('click', nodeClicked);
    chart.on('contextmenu', nodeRightClick);
    chart.getZr().on('contextmenu', rightClick);

    // Calculate grid dimensions based on container width for responsive layout.
    const container = document.getElementById('main_graph');
    const containerWidth = container.offsetWidth;
    const leftGridWidth = containerWidth * 0.5;
    const rightGraphWidth = leftGridWidth * 0.4;

    // Set up chart configuration options with multiple grids and axes.
    const option = {
        title: [
            { text: "Network Activity", left: "5%", top: "5%" },
            { text: "Membrane Potential (mV)", left: "60%", top: "5%" },
            { text: "Input stimuli (µA/cm²).", left: "60%", top: "48%" }
        ],
        grid: [
            { left: "5%", right: "45%", top: "15%", height: leftGridWidth + "px" },
            { left: "65%", right: "5%", top: "15%", height: rightGraphWidth + "px" },
            { left: "65%", right: "5%", top: "55%", height: rightGraphWidth + "px" }
        ],
        xAxis: [
            { type: "value", gridIndex: 0, min: 0, max: 5 },
            { type: "value", gridIndex: 1, scale: true },
            { type: "value", gridIndex: 2, scale: true }
        ],
        yAxis: [
            { type: "value", gridIndex: 0, min: 0, max: 5 },
            { type: "value", gridIndex: 1 },
            { type: "value", gridIndex: 2 }
        ],
        dataZoom: [
            { type: 'inside', xAxisIndex: [0] },
            { type: 'inside', yAxisIndex: [0] }
        ],
        tooltip: {
            trigger: "item",
            // Handles tooltip formatting based on node type and chart component.
            formatter: function (params) {
                if (params.componentIndex < 2) {
                    if (params.dataType === "node") {
                        switch (params.name[0]) {
                            case "n":
                                return `Neuron: <b>${params.name}</b><br>Position: (${params.value[0]}, ${params.value[1]})`;
                            case "s":
                                // For synapses, show connection details and neurotransmitter type.
                                const connections = params.data.connectedNeurons;
                                return `Connections: <b>Pre: ${connections.pre} Post: ${connections.post}</b><br>Neurotransmitter Type: <b>${params.data.neurotransmitterType}</b>`;
                            case "e":
                                return `Connected Neurons: <b>${params.data.connectedNeurons}</b><br>Current Type: <b>${params.data.currentType}</b>`;
                        }
                    } else if (params.dataType === "edge") {
                        return `Synapse: <b>${params.data.source} → ${params.data.target}</b>`;
                    }
                } else if (params.componentIndex === 2) {
                    return `Membrane Potential: <b>${params.data[1].toFixed(2)}</b> (mV)`;
                } else if (params.componentIndex === 3) {
                    return `Synaptic Current: <b>${params.data[1].toFixed(2)}</b> (µA/cm²)`;
                } else if (params.componentIndex === 4) {
                    return `Electrode Current: <b>${params.data[1].toFixed(2)}</b> (µA/cm²)`;
                }
            }
        }
    };

    if (chart) {
        chart.setOption(option);
        updateSymbolSizesRelativeToGrid();
    } else {
        console.error("Echart instance failed to init");
    }
    // Update the graph using the initial simulation state.
    updateGraph(simDict);
}

// ------------------------------------------------------------
// Data Helper Functions
// ------------------------------------------------------------
/**
 * Builds a data array for neurons or synapses.
 * @param {Array} objs - Array of objects representing neurons or synapses.
 * @param {string} paramType - 'n' for neuron, 's' for synapse.
 * @returns {Array} Array of formatted position objects.
 */
function dataBuilder(objs, paramType) {
    const positionList = [];
    const target = `n${neuronTarget}`;
    const symbols = { n: "circle", s: "rect" };

    // Iterate over each object using a for...in loop.
    for (let objIndex in objs) {
        const params = objs[objIndex].params;
        const nodeName = paramType + String(objIndex);
        const x = params.x;
        const y = params.y;
        let cssColor = "#4287f5";

        if (paramType === "n") {
            const rgbColor = hsbColorRangeFinder(0, 70, params.vrest - 1, params.vthresh, params.v);
            cssColor = rgbToCss(rgbColor);
        }
        const positionObj = {
            name: nodeName.toString(),
            value: [x, y],
            inputCurrents: "none",
            label: {
                formatter: nodeName.toString(),
                color: "#000000",
                fontSize: symbolSizes.n * 0.5
            },
            symbol: symbols[paramType],
            symbolSize: symbolSizes[paramType],
            itemStyle: {
                color: cssColor,
                borderColor: "#000000",
                borderWidth: 1.5 * Number(nodeName === target)
            }
        };
        if (paramType === "s") {
            positionObj.neurotransmitterType = params.neurotransmitterType;
            positionObj.connectedNeurons = objs[objIndex].connections;
        }
        positionList.push(positionObj);
    }
    return positionList;
}

/**
 * Concatenates the neuron and synapse data arrays.
 * @param {Array} neurons - Array of neuron objects.
 * @param {Array} synapses - Array of synapse objects.
 * @returns {Array} Concatenated array of position objects.
 */
function positionToDataArr(neurons, synapses) {
    const neuronData = dataBuilder(neurons, "n");
    const synapseData = dataBuilder(synapses, "s");
    return neuronData.concat(synapseData);
}

/**
 * Constructs a connection list for synapses.
 * @param {Array} synapses - Array of synapse objects.
 * @returns {Array} List of connection objects linking neurons and synapses.
 */
function getConnectionList(synapses) {
    const connectionList = [];
    // Iterate over each synapse using a for...in loop.
    for (let synapseIndex in synapses) {
        const cons = synapses[synapseIndex].connections;
        const preSynConnections = cons.pre;
        const postSynConnections = cons.post;
        const synapseName = "s" + String(synapseIndex);

        // Create connection objects for pre-synaptic connections.
        preSynConnections.forEach(neuronIndex => {
            connectionList.push({ source: "n" + neuronIndex, target: synapseName });
        });
        // Create connection objects for post-synaptic connections.
        postSynConnections.forEach(neuronIndex => {
            connectionList.push({ source: synapseName, target: "n" + neuronIndex });
        });
    }
    return connectionList;
}

// ------------------------------------------------------------
// Simulation Update Functions
// ------------------------------------------------------------
/**
 * Applies electrode changes from the context menu to the current electrodes.
 * @param {Object} electrodeChanges - An object mapping electrode names to their updated properties.
 */
function electrodeBuilder(electrodeChanges) {
    // Iterate over each electrode.
    for (let i in electrodes) {
        const electrode = electrodes[i];
        if (electrodeChanges[electrode.name]) {
            // Merge the new properties into the electrode.
            for (let key in electrodeChanges[electrode.name]) {
                electrode[key] = electrodeChanges[electrode.name][key];
            }
            const currentBuilder = {};
            // Update current for each neuron connected to this electrode.
            for (let j in electrode.connectedNeurons) {
                const neuronName = electrode.connectedNeurons[j];
                currentBuilder[neuronName.slice(1)] = electrodeChanges[electrode.name];
            }
            addCurrent(currentBuilder);
        }
    }
}

/**
 * Removes an electrode and resets current for its connected neurons.
 * @param {string} nodeName - The name of the electrode node to remove.
 */
function removeElectrode(nodeName) {
    const currentData = { currentType: "None" };
    // Iterate over electrodes to locate the one to remove.
    for (let electrodeIndex in electrodes) {
        const electrode = electrodes[electrodeIndex];
        if (electrode.name === nodeName) {
            console.log(electrode, nodeName)
            const data = {};
            // For each connected neuron, set its current to "none".
            for (let neuronIndex in electrode.connectedNeurons) {
                let neuron = electrode.connectedNeurons[neuronIndex];
                let neuron_index = neuron.slice(1);
                data[neuron_index] = currentData;
            }
            addCurrent(data);
            // Remove the electrode from the list.
            electrodes.splice(electrodeIndex, 1);
        }
    }
}

/**
 * Finds neurons whose positions (in pixels) fall within a specified rectangular region.
 * @param {Array} pixelCenterCoords - [x, y] coordinates of the rectangle's center in pixels.
 * @param {number} width - The width of the rectangle in pixels.
 * @param {number} height - The height of the rectangle in pixels.
 * @returns {Array} Array of neuron names that lie within the rectangle.
 */
function getNeuronsInsideRect(pixelCenterCoords, width, height) {
    // Calculate the rectangle's boundaries.
    const electrodeBottom = pixelCenterCoords[1] + (height / 2);
    const electrodeLeft = pixelCenterCoords[0] - (width / 2);
    const electrodeTop = electrodeBottom - height;
    const electrodeRight = electrodeLeft + width;

    const seriesData = chart.getOption().series[1].data;
    const neuronsInElectrodes = [];

    // Iterate over each data point.
    for (let key in seriesData) {
        const datapoint = seriesData[key];
        const dataName = datapoint.name;
        if (dataName[0] !== "n") continue; // Only consider neuron nodes.

        const pos = datapoint.value;
        // Convert the data-space coordinates to pixel coordinates.
        const [pixelX, pixelY] = chart.convertToPixel({ seriesIndex: 0 }, pos);
        // Check if the point is within the rectangular boundaries.
        if (pixelX >= electrodeLeft && pixelX <= electrodeRight &&
            pixelY >= electrodeTop && pixelY <= electrodeBottom) {
            neuronsInElectrodes.push(dataName);
        }
    }
    return neuronsInElectrodes;
}

// ------------------------------------------------------------
// Graphic Event Functions
// ------------------------------------------------------------
/**
 * Updates each electrode's symbol size relative to the current grid dimensions.
 */
function updateElectrodesRelativeToGrid() {
    // Iterate over each electrode and update its symbolSize property.
    for (let i in electrodes) {
        const electrode = electrodes[i];
        const [width, height] = electrode.dimensions;
        const [symbolWidth, symbolHeight] = convertWidthHeightPxToChart(width, height);
        electrode.symbolSize = [symbolWidth, symbolHeight];
    }
}

/**
 * Updates global symbol sizes based on the current grid scaling.
 */
function updateSymbolSizesRelativeToGrid() {
    updateElectrodesRelativeToGrid();
    // Recalculate global symbolSizes based on baseline values.
    symbolSizes = {
        n: convertSizeToChart(baselineSymbolSizes[0]),
        s: convertSizeToChart(baselineSymbolSizes[1])
    };
}

/**
 * Sets the target neuron based on the given node name.
 * @param {string} nodeName - The name of the neuron node (e.g., "n5").
 */
function focusNeuron(nodeName) {
    neuronTarget = parseInt(nodeName.substring(1));
}

/**
 * Handles click events on individual nodes.
 * @param {Object} params - Event parameters provided by the chart.
 */
function nodeClicked(params) {
    const nodeName = params.data.name;
    if (params.seriesIndex < 2) {
        switch (nodeName[0]) {
            case "e":
                removeElectrode(nodeName);
                break;
            case "n":
                focusNeuron(nodeName);
                break;
            case "s":
                // Placeholder for synapse actions.
                break;
            default:
                console.warn(`Warning: Unknown nodeType: ${nodeName}`);
                break;
        }
    }
}

/**
 * Updates the global right-click coordinates based on the event.
 * @param {Object} event - The event object containing clientX and clientY.
 */
function rightClick(event) {
    rightClickX = event.event.clientX;
    rightClickY = event.event.clientY;
}

/**
 * Handles right-click events on nodes (specifically electrodes).
 * @param {Object} event - The event object from the chart.
 */
function nodeRightClick(event) {
    if (event.name[0] !== "e") return;
    rightClickTarget = event.name;
    const customMenuElem = document.getElementById("customContextMenuHolder");
    // Position the custom context menu at the right-click location.
    customMenuElem.style.left = rightClickX + "px";
    customMenuElem.style.top = rightClickY + "px";
    customMenuElem.style.display = "flex";
}

/**
 * Converts a given size from chart units to pixel units.
 * @param {number} size - The size in chart units.
 * @returns {number} The size in pixels.
 */
function convertSizeToChart(size) {
    const p1 = chart.convertToPixel({ gridIndex: 0 }, [0, 0]);
    const p2 = chart.convertToPixel({ gridIndex: 0 }, [size, 0]);
    return Math.abs(p2[0] - p1[0]);
}

/**
 * Converts width and height from chart units to pixels.
 * @param {number} width - The width in chart units.
 * @param {number} height - The height in chart units.
 * @returns {Array} An array containing the width and height in pixels.
 */
function convertWidthHeightPxToChart(width, height) {
    const p1 = chart.convertToPixel({ seriesIndex: 0 }, [0, 0]);
    const p2 = chart.convertToPixel({ seriesIndex: 0 }, [width, height]);
    return [Math.abs(p2[0] - p1[0]), Math.abs(p2[1] - p1[1])];
}

/**
 * Handles click events on the chart background (excluding nodes).
 * @param {Object} event - The click event object.
 */
function chartClicked(event) {
    // Ignore clicks on nodes.
    if (event.target) return;

    const width = Number(document.getElementById("electrode_width").value);
    const height = Number(document.getElementById("electrode_height").value);
    const pointInPixel = [event.offsetX, event.offsetY];
    const pointIsInGrid = chart.containPixel({ seriesIndex: 0 }, pointInPixel);
    const pixelToGrid = chart.convertFromPixel({ seriesIndex: 0 }, pointInPixel);

    if (pointIsInGrid) {
        const [xSize, ySize] = convertWidthHeightPxToChart(width, height);
        // Identify neurons within the electrode area.
        const neuronsInBounds = getNeuronsInsideRect(pointInPixel, xSize, ySize);
        const electrode = {
            name: `e${addedElectrodes}`,
            symbol: "rect",
            value: [pixelToGrid[0], pixelToGrid[1]],
            current: "none",
            currentType: "none",
            freq: "none",
            connectedNeurons: neuronsInBounds,
            dimensions: [width, height],
            symbolSize: [xSize, ySize],
            style: { fill: "rgb(112, 112, 112)" }
        };
        electrodes.push(electrode);
        addedElectrodes += 1;
    }
}

// ------------------------------------------------------------
// Series and Graph Builder Functions
// ------------------------------------------------------------
/**
 * Constructs series for the chart based on the provided simulation data.
 * @param {Object} simDict - The simulation data dictionary.
 * @returns {Array} An array of series objects for the chart.
 */
function buildSeries(simDict) {
    const sideGraphData = getSideGraph();
    const neurons = simDict.neurons;
    const synapses = simDict.synapses;
    const electrodeChanges = getElectrodeChanges();
    // Update electrodes with any changes from the context menu.
    electrodeBuilder(electrodeChanges);
    const cons = getConnectionList(synapses);
    const posList = positionToDataArr(neurons, synapses);

    const series = [
        {
            // Base electrode graph (displayed as the background).
            roam: "enabled",
            type: "graph",
            xAxisIndex: 0,
            yAxisIndex: 0,
            z: 0,
            zlevel: 0,
            layout: "force",
            coordinateSystem: 'cartesian2d',
            symbolSize: 30,
            label: { show: true, fontSize: 14 },
            edgeSymbol: ['circle', 'arrow'],
            edgeSymbolSize: [4, 8],
            data: electrodes,
        },
        {
            // Main graph with neurons and synapses.
            roam: "enabled",
            name: "Electrodes",
            type: "graph",
            xAxisIndex: 0,
            yAxisIndex: 0,
            z: 10,
            zlevel: 0,
            layout: "force",
            coordinateSystem: 'cartesian2d',
            symbolSize: 30,
            label: { show: true, fontSize: 14 },
            edgeSymbol: ['circle', 'arrow'],
            edgeSymbolSize: [4, 8],
            data: posList,
            links: cons,
            lineStyle: { color: "#000000" },
        },
        { // Right top: Membrane potential chart.
            name: "Membrane Potential",
            type: "line",
            data: sideGraphData.vs,
            xAxisIndex: 1,
            yAxisIndex: 1,
            showSymbol: false,
        },
        { // Right bottom: Synaptic dynamics chart.
            name: "Synaptic Dynamics",
            type: "line",
            lineStyle: { color: '#000000' },
            data: sideGraphData.synapticInputs,
            xAxisIndex: 2,
            yAxisIndex: 2,
            showSymbol: false,
            tooltip: {
                trigger: 'axis',
                formatter: params => {
                    console.log(params);
                }
            }
        },
        { // Right bottom: Input currents chart.
            name: "Input Currents",
            type: "line",
            data: sideGraphData.inputCurrents,
            xAxisIndex: 2,
            yAxisIndex: 2,
            showSymbol: false
        }
    ];
    return series;
}

/**
 * Aggregates side graph data for the currently focused neuron.
 * @returns {Object} An object containing arrays for membrane potentials (vs), synaptic inputs, and input currents.
 */
function getSideGraph() {
    let vs = [];
    let synapticInputs = [];
    let inputCurrents = [];

    // Iterate over each simulation update stored in the queue.
    for (let i in dataQueue.items) {
        const simDict = dataQueue.items[i];
        const neuronData = simDict.neurons[neuronTarget];
        vs = vs.concat(neuronData.vs);
        synapticInputs = synapticInputs.concat(neuronData.synaptic_inputs);
        inputCurrents = inputCurrents.concat(neuronData.input_currents);
    }
    return { vs, synapticInputs, inputCurrents };
}

// ------------------------------------------------------------
// Animation and Update Loop
// ------------------------------------------------------------
/**
 * Updates the graph using the latest simulation data from the queue.
 * Maintains a maximum queue length by dequeuing older entries.
 */
function updateGraph() {
    // Retrieve the most recent simulation data from the queue.
    let simDict = dataQueue.items[dataQueue.length - 1];

    // If the queue is at maximum capacity, remove the oldest entry.
    if (dataQueue.length === 100) {
        dataQueue.dequeue();
    }

    // Build chart series using the current simulation state.
    const series = buildSeries(simDict);

    // Update the chart with the new series, disabling animations.
    chart.setOption({
        series: series,
        animation: false,
    });

    // Schedule the next update.
    setTimeout(() => {
        window.requestAnimationFrame(() => updateFrame());
    }, 50);
}

/**
 * Animation loop: Fetches new simulation data and updates the graph.
 */
function updateFrame() {
    if (paused) {
        // When paused, limit the update rate to 30 FPS.
        setTimeout(() => {
            requestAnimationFrame(updateFrame);
        }, 1000 / 30);
        return;
    }
    // Fetch new simulation data from the server.
    iterateSim().then(data => {
        dataQueue.enqueue(data);
        updateGraph();
    });
}
