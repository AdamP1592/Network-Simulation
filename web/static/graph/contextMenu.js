document.addEventListener("DOMContentLoaded",setUpContextMenu);

var menuTarget;
var menuOpen = false;
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
    //menuElem - btnElem = 

    var neededData = {Sin:2, Square:2, Constant:1, None:0};
    let btnElem = event.target;
    
    let textFields = document.getElementsByClassName("textField");
    let menuElem = document.getElementById("customContextMenuHolder");
    
    let topMenu = parseInt(menuElem.style.top);
    

    let rect = btnElem.getBoundingClientRect();
    let btnElemText = btnElem.innerText

    let numEntries = neededData[btnElemText]


    console.log(topMenu, rect.top)
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
            oneEntryElem.style.display = "none";
            twoEntryElem.style.display = "none";
            return;
            

    }
    setTextInputMenus(rect.width + 4, rect.top - topMenu);
    
}
function contextMenuButtonLeave(event){

}  
function noCurrentButtonClicked(event){
    console.log("Set electrode to no current");
}
function setUpButtonEvents(){

    let btns = Array.from(document.getElementsByClassName("buttonHolder"));
    for(let i in btns){
        let btnHolder = btns[i]; //buttons are stored in a buttonholder li
        let btn = btnHolder.children[0]; // only one button per holder
        if(btn.innerText.trim() == "None"){
            btn.addEventListener("click", noCurrentButtonClicked)
        }
        btn.addEventListener("mouseover", contextMenuButtonHover)
        btn.addEventListener("mouseleave", contextMenuButtonLeave)
    }
    
}
