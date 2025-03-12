console.log("nav pulled");
//window.onload(set_active_button())


document.addEventListener("DOMContentLoaded", startup)

function startup(){
    set_active_button();
}

function set_active_button(){
    console.log("Setting up nav")
    
    var button_dict = {};
    //get all available pages(buttons point directly to pages)
    const nav_buttons = document.getElementsByClassName("nav_button");

    //adds onlcik event to all buttons
    Array.from(nav_buttons).forEach(button_elem => {
        
        let txt = button_elem.textContent.trim().toLowerCase();
        console.log(button_elem)
        button_elem.addEventListener('click', function(){
            window.location.pathname = "/" + txt
        })
        
        button_dict[txt] = button_elem;
    });

    //get current url, finds that urlname 
    const subURL = window.location.pathname.slice(1);
    
    var button = button_dict[subURL];
    button.className+=" nav_pressed"

}


