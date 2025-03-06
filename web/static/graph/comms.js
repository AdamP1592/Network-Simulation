import {buildGraphs} from './graph.js'

import {updateGraph} from './graph.js'
export function iterateSim(){

    fetch('/simulation/iterateSim', {
        method:'POST',

    }).then( response => {
        if(!response.ok){
            throw new Error("Response was not ok");
        }
        return response.json();


    }).then(data => {
        buildGraphs(data);
    }).catch((error)=>{
        console.error("Error:", error);
    });

}
export function setUpNetwork(){

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

export function addCurrent(currentDict){
    
    console.log("Adding current", currentDict)

    fetch('/simulation/setCurrent', {
        method:'POST',
        headers:{
            'Content-Type': 'application/json'
        },
        body:JSON.stringify(currentDict)
    })
    
}
