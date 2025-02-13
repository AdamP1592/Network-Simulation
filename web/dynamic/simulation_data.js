let response = fetch(`${window.location.href}/sim_data`, {method:'POST'})
console.log(response.text())