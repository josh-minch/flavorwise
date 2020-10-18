function searchSubmit(ev) {
    ev.preventDefault();
    fetch('/search', {
        method: 'POST',
        body: new FormData(this)
    })
        .then(parseJSON)
        .then(updateDisplay);
    updateCurIngreds();
}

function parseJSON(response) {
    return response.json();
}

function updateDisplay(json_data) {
    var cur_ingreds = document.getElementById('cur_ingreds');
    var r_ingreds = document.getElementById('r_ingreds');
    var recipes = document.getElementById('recipes');
    cur_ingreds.innerText = json_data.cur_ingreds
    r_ingreds.innerText = json_data.r_ingreds;
    recipes.innerText = json_data.recipes;
}


var form = document.getElementById('calc');
form.addEventListener('submit', searchSubmit);
