import { buildGraphs } from './graph.js';

/**
 * Iterates the simulation by making a POST request to the iterateSim endpoint.
 * @returns {Promise<Object>} A promise that resolves to the simulation data in JSON.
 */
export function iterateSim() {
    return fetch('/simulation/iterateSim', {
        method: 'POST',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Response was not ok");
        }
        return response.json();
    })
    .catch((error) => {
        console.error("Error in iterateSim:", error);
        throw error;
    });
}

/**
 * Sets up the simulation network by prompting the user for the number of neurons,
 * sending these parameters to the server, and then initializing the graph with the
 * returned simulation state.
 */
export function setUpNetwork() {
    // Prompt the user for the number of neurons.
    const numNeurons = prompt("Please enter number of neurons:", "0");

    // Prepare network parameters.
    const networkParams = { "numNeurons": numNeurons, dimensions: { x: "5", y: "5" } };

    fetch('/simulation/startSim', {
        method: 'POST',
        headers: {
            "Content-Type": 'application/json'
        },
        body: JSON.stringify(networkParams)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Response was not ok");
        }
        return response.json();
    })
    .then(data => {
        // Build the graph with the initial simulation state.
        buildGraphs(data);
    })
    .catch((error) => {
        console.error("Error in setUpNetwork:", error);
    });
}

/**
 * Sends current stimulation data to the server.
 * @param {Object} currentDict - An object containing the current stimulation parameters.
 */
export function addCurrent(currentDict) {
    console.log("Adding current", currentDict);
    
    fetch('/simulation/setCurrent', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(currentDict)
    })
    .catch((error) => {
        console.error("Error in addCurrent:", error);
    });
}
