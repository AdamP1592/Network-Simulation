import {getTarget} from './graph.js'

console.log("nav pulled");

// Set up context menu when DOM is ready.
document.addEventListener("DOMContentLoaded", setUpContextMenu);

let menuTarget;
let enterPressed;
let menuHideTimer = setTimeout(() => {}, 1);
let textHideTimer = setTimeout(() => {}, 1);
let textFieldVisible = false;
let rightClickTarget = "";
let menuButtonFocus;
let electrodeChanges = {};

/**
 * Retrieves and clears any electrode changes that have been set.
 * @returns {Object} The electrode changes.
 */
export function getElectrodeChanges() {
    const tempChanges = electrodeChanges;
    electrodeChanges = {};
    return tempChanges;
}

/**
 * Initializes context menu functionality.
 */
function setUpContextMenu() {
    console.log("Setting up context menu");
    setUpButtonEvents();
}

/**
 * Positions and displays the text input menu.
 * @param {number} left - The left offset for the text input menu.
 */
function setTextInputMenus(left) {
    // Position the menu at the given left offset.
    menuTarget.style.left = left + "px";
    // Append the text input menu to the currently focused button element.
    menuButtonFocus.appendChild(menuTarget);
    menuTarget.style.display = "inline-block";
}

/**
 * Handles hover events on context menu buttons.
 * Determines which text input block to display based on the button text.
 * @param {Event} event - The mouseover event.
 */
function contextMenuButtonHover(event) {
    clearTimeout(menuHideTimer);

    // Mapping of stimulation type to the number of required text input fields.
    const neededData = { Sin: 2, Square: 2, Constant: 1, None: 0 };

    const btnElem = event.currentTarget;
    menuButtonFocus = btnElem;

    const menuElem = document.getElementById("customContextMenuHolder");
    const rect = btnElem.getBoundingClientRect();

    // Get the button text (in lowercase) to determine required inputs.
    const btnElemText = btnElem.innerText.trim();
    const numEntries = neededData[btnElemText];

    // Get the two potential text input menu elements.
    const oneEntryElem = document.getElementById("contextHoverOneEntry");
    const twoEntryElem = document.getElementById("contextHoverTwoEntries");

    switch (numEntries) {
        case 1:
            menuTarget = oneEntryElem;
            // Hide the other text input element.
            twoEntryElem.style.display = "none";
            break;
        case 2:
            menuTarget = twoEntryElem;
            // Hide the one-entry text input element.
            oneEntryElem.style.display = "none";
            break;
        default:
            // If the button doesn't require text input, do nothing.
            return;
    }

    textFieldVisible = true;
    // Position the text input menu to the left by the width of the button.
    setTextInputMenus(rect.width);
    // Focus the first text field within the menu.
    menuTarget.getElementsByClassName("textField")[0].select();
}

/**
 * Hides the text input menu.
 */
function hideText() {
    const oneEntryElem = document.getElementById("contextHoverOneEntry");
    const twoEntryElem = document.getElementById("contextHoverTwoEntries");
    menuTarget = null;
    menuButtonFocus = null;
    textFieldVisible = false;
    oneEntryElem.style.display = "none";
    twoEntryElem.style.display = "none";
}

/**
 * Handles key release events.
 * If Enter is released and the text input menu is visible, it submits the input.
 * @param {KeyboardEvent} event - The keyup event.
 */
function keyReleased(event) {
    if (event.keyCode === 13) { // Enter key
        console.log("Enter key released");
        enterPressed = false;
        if (textFieldVisible) {
            hideMenu();
        }
    }
}

/**
 * Sets the current stimulation parameters for the electrode.
 * @param {Object} changes - The current parameters from the text input.
 */
function setCurrent(changes) {
    enterPressed = true;
    // Retrieve the target from the graph.
    rightClickTarget = getTarget();
    electrodeChanges[rightClickTarget] = changes;
}

/**
 * Handles key press events.
 * When Enter is pressed and the text field is visible, it submits the input.
 * @param {KeyboardEvent} event - The keydown event.
 */
function keyPressed(event) {
    if (event.keyCode === 13 && textFieldVisible) {
        setCurrent(getTextInputParams());
    }
}

/**
 * Retrieves the parameters entered in the text input menu.
 * @returns {Object} An object containing the current stimulation parameters.
 */
function getTextInputParams() {
    const params = {};
    const inputSections = menuTarget.getElementsByClassName("textField");
    // Use the first line of the button text as the current type.
    const currentType = menuButtonFocus.innerText.split(/\r?\n/)[0];
    params["currentType"] = currentType;
    // Iterate through the text fields to collect values.
    for (let menuItemIndex in inputSections) {
        const section = inputSections[menuItemIndex];
        if (section.id) { // Ensure this element is an input.
            params[section.id] = Number(section.value);
        }
    }
    return params;
}

/**
 * Hides the context menu.
 */
function hideMenu() {
    menuTarget = null;
    menuButtonFocus = null;
    textFieldVisible = false;
    const oneEntryElem = document.getElementById("contextHoverOneEntry");
    const twoEntryElem = document.getElementById("contextHoverTwoEntries");
    const contextMenu = document.getElementById("customContextMenuHolder");

    oneEntryElem.style.display = "none";
    twoEntryElem.style.display = "none";
    contextMenu.style.display = "none";
}

/**
 * Handles clicks on the "None" button, indicating no current stimulation.
 * @param {Event} event - The click event.
 */
function noCurrentButtonClicked(event) {
    console.log("No current Clicked");
    const currentDict = { currentType: "None" };
    setCurrent(currentDict);
    hideMenu();
}

/**
 * Handles mouse leave events for context menu buttons.
 * Schedules the menu to be hidden after a short delay.
 */
function contextMenuButtonLeave() {
    menuHideTimer = setTimeout(() => {
        hideMenu();
    }, 200);
}

/**
 * Clears hide timers when the mouse enters the text input menu.
 */
function textMenuEnter() {
    clearTimeout(textHideTimer);
    clearTimeout(menuHideTimer);
}

/**
 * Hides the text input menu when the mouse leaves, after a short delay.
 */
function textMenuLeave() {
    textHideTimer = setTimeout(() => {
        hideText();
        console.log("Hiding text menu");
    }, 200);
    menuHideTimer = setTimeout(() => {
        hideMenu();
    }, 200);
}

/**
 * Sets up event listeners for context menu buttons and text inputs.
 */
function setUpButtonEvents() {
    const btns = Array.from(document.getElementsByClassName("buttonHolder"));
    const contextMenu = document.getElementById("customContextMenuHolder");

    document.addEventListener('keydown', keyPressed);
    document.addEventListener('keyup', keyReleased);

    const inputSections = Array.from(document.getElementsByClassName("contextText"));
    inputSections.forEach(textElem => {
        textElem.addEventListener('mouseenter', textMenuEnter);
        textElem.addEventListener('mouseleave', textMenuLeave);
    });

    btns.forEach(btnHolder => {
        // Each buttonHolder should contain one button.
        const btn = btnHolder.children[0];
        if (btn.innerText.trim() === "None") {
            btn.addEventListener("click", noCurrentButtonClicked);
        }
        btn.addEventListener("mouseover", contextMenuButtonHover);
    });

    contextMenu.addEventListener("mouseleave", contextMenuButtonLeave);
}
