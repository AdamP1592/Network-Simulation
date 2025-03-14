console.log("nav pulled");

// Run startup when the DOM is ready.
document.addEventListener("DOMContentLoaded", startup);

/**
 * Initializes the navigation bar.
 */
function startup() {
    setActiveButton();
}

/**
 * Sets up active navigation button based on current URL.
 */
function setActiveButton() {
    console.log("Setting up nav");

    const buttonDict = {};
    // Get all navigation buttons.
    const navButtons = document.getElementsByClassName("nav_button");

    // Add click event to each button.
    Array.from(navButtons).forEach(buttonElem => {
        // Extract text content and convert to lowercase.
        const txt = buttonElem.textContent.trim().toLowerCase();
        console.log(buttonElem);
        buttonElem.addEventListener('click', function() {
            window.location.pathname = "/" + txt;
        });

        // Save reference to button in a dictionary.
        buttonDict[txt] = buttonElem;
    });

    // Determine current page from URL.
    const subURL = window.location.pathname.slice(1);
    
    // Check if a matching button exists, then add the active class.
    if (buttonDict[subURL]) {
        buttonDict[subURL].className += " nav_pressed";
    }
}
