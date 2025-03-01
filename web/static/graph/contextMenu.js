import {getTarget} from './graph.js'
document.addEventListener("DOMContentLoaded",setUpContextMenu);

var menuTarget;
var enterPressed;

var textFieldVisible = false;
var rightClickTarget = "";

var menuButtonFocus;

var electrodeChanges = {}

export function getElectrodeChanges(){
    let tempChanges = electrodeChanges;
    electrodeChanges = {}
    return tempChanges;
}

function setUpContextMenu(){
    console.log("Setting up")
    setUpButtonEvents();

}
function setTextInputMenus(left, top){
    //menuTarget is placed within the menu, so 
    menuTarget.style.top = top;
    menuTarget.style.left = left;

    menuTarget.style.display = "inline-block";
    
}
function hideTextInputMenus(){

}
function contextMenuButtonHover(event){
    var neededData = {Sin:2, Square:2, Constant:1, None:0};
    let btnElem = event.target;

    menuButtonFocus = btnElem;
    
    let menuElem = document.getElementById("customContextMenuHolder");

    let topMenu = parseInt(menuElem.style.top);
    let rect = btnElem.getBoundingClientRect();

    let btnElemText = btnElem.innerText
    let numEntries = neededData[btnElemText]

    let oneEntryElem =  document.getElementById("contextHoverOneEntry");
    let twoEntryElem = document.getElementById("contextHoverTwoEntries");
    
    let textMenuHeightMult = 1;

    switch(numEntries){
        case 1:
            menuTarget = oneEntryElem;
            //hides the other textfield
            twoEntryElem.style.display = "none";
            textMenuHeightMult = 2;
            break;
        case 2:
            menuTarget = twoEntryElem;
            //hides the other textfield
            oneEntryElem.style.display = "none";
            
            break;
        default:
            menuTarget = null;
            menuButtonFocus = null;

            textFieldVisible = false;
            oneEntryElem.style.display = "none";
            twoEntryElem.style.display = "none";
            return;
            
    }
    textFieldVisible = true;

    let normalizedHeight = textMenuHeightMult * rect.height;
    setTextInputMenus(rect.width, (rect.top) - topMenu);
    
}
function keyReleased(event){
    var key = event.keyCode;
    if(key == 13){
        console.log("released")
        enterPressed = false;

        if(textFieldVisible){
            hideMenu()
        }
    }
}
function keyPressed(event){
    var key = event.keyCode;
    if(key == 13){
        enterPressed = true;
        if(textFieldVisible){
            rightClickTarget = getTarget();

            electrodeChanges[rightClickTarget] = getTextInputParams();
        }
        console.log(electrodeChanges)
    }
}
function getTextInputParams(){
    var params = {}
    let inputSections = menuTarget.getElementsByClassName("textField");
    
    
    let currentType = menuButtonFocus.innerText.trim();
    params["currentType"] = currentType

    for(let menuItemIndex in inputSections){
        let section = inputSections[menuItemIndex]
        if(section.id){
            
            params[section.id] = Number(section.value)
        }
    }
    return params;
    
}
function hideMenu(){
    menuTarget = null;
    menuButtonFocus = null;

    textFieldVisible = false;
    textFieldVisible = false;
    let oneEntryElem =  document.getElementById("contextHoverOneEntry");
    let twoEntryElem = document.getElementById("contextHoverTwoEntries");
    let contextMenu = document.getElementById("customContextMenuHolder");

    oneEntryElem.style.display = "none";
    twoEntryElem.style.display = "none";
    contextMenu.style.display = "none";
}

function contextMenuButtonLeave(event){
    hideMenu()
}  
function noCurrentButtonClicked(event){
    console.log("Set electrode to no current");
    hideMenu()
}
function setUpButtonEvents(){

    let btns = Array.from(document.getElementsByClassName("buttonHolder"));
    let contextMenu = document.getElementById("customContextMenuHolder");
    document.addEventListener('keydown', keyPressed);
    document.addEventListener('keyup', keyReleased);

    for(let i in btns){
        let btnHolder = btns[i]; //buttons are stored in a buttonholder li
        let btn = btnHolder.children[0]; // only one button per holder
        if(btn.innerText.trim() == "None"){
            btn.addEventListener("click", noCurrentButtonClicked)
        }
        btn.addEventListener("mouseover", contextMenuButtonHover)
    }
    contextMenu.addEventListener("mouseleave", contextMenuButtonLeave)
    
}
