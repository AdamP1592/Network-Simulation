console.log("nav pulled");
//window.onload(set_active_button())


document.addEventListener("DOMContentLoaded", startup)


function startup(){
    set_active_button();

}
function set_active_button(){
    var button_dict = {};
    //get all available pages(buttons point directly to pages)
    const nav_buttons = document.getElementsByClassName("nav_button");

    //maps buttons to
    Array.from(nav_buttons).forEach(button_elem => {
        let txt = button_elem.innerText.trim().toLowerCase();

        button_elem.addEventListener('click', function(){
            window.location.pathname = txt
        })
        
        button_dict[txt] = button_elem;
    });

    //get current url, finds that urlname in the 
    const subURL = window.location.pathname.slice(1);
    var button = button_dict[subURL];

    //adds onclick to 
    button.className+=" nav_pressed"


}


