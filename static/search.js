var search = document.getElementById('search');
search.addEventListener('submit', searchSubmit);
var remove = document.getElementById('cur_ingreds')
remove.addEventListener('submit', removeIngred);


function searchSubmit(ev) {
    ev.preventDefault();
    fetch('/search', {
        method: 'POST',
        body: new FormData(this)
    })
        .then(parseJSON)
        .then(updateDisplay);
}

function removeIngred(ev) {
    ev.preventDefault();
    fetch('/remove', {
        method: 'POST',
        body: new FormData(this)
    })
        .then(parseJSON)
        .then(updateDisplay);
}

function parseJSON(response) {
    return response.json();
}

function updateDisplay(json_data) {
    removeAllChild(document.getElementById('cur_ingreds'))
    createCurIngreds(json_data.cur_ingreds);
    var r_ingreds = document.getElementById('r_ingreds');
    var recipes = document.getElementById('recipes');
    r_ingreds.innerText = json_data.r_ingreds;
    recipes.innerText = json_data.recipes;
}

function createCurIngreds(cur_ingreds) {
    const cur_ingreds_sec = document.querySelector('#cur_ingreds');
    cur_ingreds.forEach(element => {
        const div = document.createElement('div');
        const input = createInput(element);
        const label = createLabel(element);
        cur_ingreds_sec.appendChild(div);
        div.appendChild(label);
        label.prepend(input);
    });
    const btn = createRemoveBtn();
    cur_ingreds_sec.appendChild(btn)
}

function removeAllChild(node) {
    while (node.firstChild) {
        node.removeChild(node.firstChild);
    }
}
function createInput(element) {
    const input = document.createElement('input');
    input.setAttribute('type', 'checkbox');
    input.setAttribute('id', element);
    input.setAttribute('name', element);
    return input;
}

function createLabel(element) {
    const label = document.createElement('label');
    label.setAttribute('for', element);
    label.innerText = ` ${element}`;
    return label;
}

function createRemoveBtn() {
    const btn = document.createElement('input');
    btn.setAttribute('type', "submit");
    btn.setAttribute('value', "Remove");
    btn.setAttribute('id', "remove-button");
    return btn;
}

/* var node = document.createElement("LI");
var textnode = document.createTextNode("Water");
node.appendChild(textnode); */



