document.addEventListener("DOMContentLoaded",setUpContextMenu);

var menuTarget;
var menuOpen = false;
var enterPressed = false;
var textFieldVisible = false;

function setCurrent(currentType, freq, amplitude){

}

function setUpContextMenu(){
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
    
    let menuElem = document.getElementById("customContextMenuHolder");

    let topMenu = parseInt(menuElem.style.top);
    let rect = btnElem.getBoundingClientRect();

    let btnElemText = btnElem.innerText
    let numEntries = neededData[btnElemText]

    let oneEntryElem =  document.getElementById("contextHoverOneEntry");
    let twoEntryElem = document.getElementById("contextHoverTwoEntries");

    switch(numEntries){
        case 1:
            menuTarget = oneEntryElem;
            //hides the other textfield
            twoEntryElem.style.display = "none";
            break;
        case 2:
            menuTarget = twoEntryElem;
            //hides the other textfield
            oneEntryElem.style.display = "none";
            break;
        default:
            textFieldVisible = false;
            oneEntryElem.style.display = "none";
            twoEntryElem.style.display = "none";
            return;
            
    }
    textFieldVisible = true;
    setTextInputMenus(rect.width + 4, rect.top - topMenu);
    
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
    }
}
function hideMenu(){
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
