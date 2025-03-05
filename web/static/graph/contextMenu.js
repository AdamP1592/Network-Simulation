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
function contextMenuButtonHover(event){

    //setup for switch
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
            //hovering anything but the buttons that need text data clears it
            menuTarget = null;
            menuButtonFocus = null;

            textFieldVisible = false;
            oneEntryElem.style.display = "none";
            twoEntryElem.style.display = "none";
            return;
            
    }
    //if you dont get caught by the default catch case the text field is visible
    textFieldVisible = true;

    //since textField is placed within the whole menu, the top = 0 is just the top of the menu
    //and left = 0 is the leftside of the menu, so shift it over the width of the menu
    setTextInputMenus(rect.width, (rect.top) - topMenu);
    
}
function keyReleased(event){
    var key = event.keyCode;
    if(key == 13){

        //clears enterPressed
        console.log("released")
        enterPressed = false;

        //if the text menu is visible, enter is the submit btn so hide the menu
        if(textFieldVisible){
            hideMenu()
        }
    }
}

//function to set the new current in electrodeChanges to get passed to the main graph
function setCurrent(changes){
    enterPressed = true;
    
    rightClickTarget = getTarget();
    electrodeChanges[rightClickTarget] = changes;
}

function keyPressed(event){
    var key = event.keyCode;

    //when enter is pressed and the text field for the context menu is visible, set the current based on the params in the text menu
    if(key == 13 && textFieldVisible){
        setCurrent(getTextInputParams())
    }
}
//gets the text input from the context menu textfield
function getTextInputParams(){
    var params = {}
    let inputSections = menuTarget.getElementsByClassName("textField");
    
    //pulls text from the currently opened menu
    let currentType = menuButtonFocus.innerText.trim();
    //sets current type
    params["currentType"] = currentType
    //iterates through the open text menu to pulll data from display
    for(let menuItemIndex in inputSections){
        let section = inputSections[menuItemIndex]
        //only the items that contain an id, some other elements pop up
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
    console.log("No current Clicked")
    let currentDict = {currentType:"None"}
    setCurrent(currentDict)
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
