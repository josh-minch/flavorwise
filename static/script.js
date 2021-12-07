setRemoveButtonState()

document.querySelectorAll("input[type='checkbox']").forEach(checkbox => {
    checkbox.addEventListener('change', setRemoveButtonState)
});


function setRemoveButtonState() {
    // Change ingreds selected text to reflect ui state
    let checkboxes = document.querySelectorAll("input[type='checkbox']");
    let numChecked = 0;
    checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
            numChecked++;
        }
    });

    let selectedIngredText = document.getElementById('selected-ingred-text');
    selectedIngredText.textContent = `${numChecked} selected`;

    // Set button style disabled if no ingreds selected
    let removeBtn = document.getElementById('remove-button');
    if (removeBtn) {
        if (numChecked == 0) {
            selectedIngredText.classList.add('disabled-text');
            removeBtn.disabled = true;
        }
        else {
            selectedIngredText.classList.remove('disabled-text');
            removeBtn.disabled = false;
        }
    }
}

const search = document.getElementById('search');
search.addEventListener('submit', searchAddIngred);

const randomIngreds = document.getElementById('random-ingreds');
randomIngreds.addEventListener('click', addRelatedIngred);

const relatedIngreds = document.getElementById('r-ingreds');
relatedIngreds.addEventListener('click', addRelatedIngred);

const remove = document.getElementById('cur-ingreds');
remove.addEventListener('submit', removeIngred);

/* When selecting a dropdown ingredient, add ingredient to current ingredients,
close dropdown, and clear search field. */
$('.typeahead').on('typeahead:selected', function (ev, ingred) {
    addDropdownIngred(ingred);
    $('.typeahead').typeahead('close');
    $('.typeahead').typeahead('val', '');
})

function searchAddIngred(ev) {
    handleUserInput(new FormData(this), ev, '/search')
    // Clear search field after adding ingred
    this.reset();
}

function addDropdownIngred(ingred) {
    document.getElementById('recipe-loading-icon').classList.remove('d-none');
    document.getElementById('ingred-loading-icon').classList.remove('d-none');
    var formData = new FormData();
    formData.append('ingred_to_add', ingred)

    fetch('/add_dropdown_ingred', {
        method: 'POST',
        body: formData
    })
        .then(parseJSON)
        .then(updateView);
}

function addRelatedIngred(ev) {
    const isButton = ev.target.nodeName === 'BUTTON';
    if (!isButton) {
        return;
    }
    var formData = new FormData();
    formData.append('search', String(ev.target.value))
    handleUserInput(formData, ev, '/search');
    // Clear table filters
    ingredTable.search('').draw();
    recipeTable.search('').draw();
}

function removeIngred(ev) {
    handleUserInput(new FormData(this), ev, '/remove')
}

function handleUserInput(formData, ev, path) {
    document.getElementById('recipe-loading-icon').classList.remove('d-none');
    document.getElementById('ingred-loading-icon').classList.remove('d-none');

    ev.preventDefault();
    fetch(path, {
        method: 'POST',
        body: formData
    })
        .then(parseJSON)
        .then(updateView);
}

function parseJSON(response) {
    return response.json();
}

function updateView(jsonData) {
    toggleRemoveDisplay(jsonData.cur_ingreds);
    toggleRandomIngredDisplay(jsonData.cur_ingreds);

    removeCurIngreds();
    createCurIngreds(jsonData.cur_ingreds);
    createRelatedIngreds(jsonData.r_ingreds);
    createRecipes(jsonData.recipes, jsonData.cur_ingreds);

    let checkboxes = document.querySelectorAll("input[type='checkbox']");
    setRemoveButtonState()
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', setRemoveButtonState)
    });
}

function toggleRemoveDisplay(curIngreds) {
    let removeIngredSec = document.getElementById('remove-ingred-sec');

    if (curIngreds.length == 0) {
        removeIngredSec.classList.add('d-none');
        removeIngredSec.classList.remove('d-block');
    }
    else {
        removeIngredSec.classList.add('d-block');
        removeIngredSec.classList.remove('d-none');
    }
}

function toggleRandomIngredDisplay(curIngreds) {
    let randomIngreds = document.getElementById('random-ingreds');

    if (curIngreds.length == 0) {
        randomIngreds.classList.add('d-block');
        randomIngreds.classList.remove('d-none');
    }
    else {
        randomIngreds.classList.add('d-none');
        randomIngreds.classList.remove('d-block');
    }
}

function removeCurIngreds() {
    let curIngreds = document.querySelectorAll('.cur-ingred');
    for (const curIngred of curIngreds) {
        curIngred.remove()
    }
}

function createCurIngreds(curIngreds) {
    const curIngredsForm = document.querySelector('#cur-ingreds-list');

    curIngreds.forEach(ingred => {
        const ingredDiv = document.createElement('div');
        ingredDiv.setAttribute('class', 'cur-ingred')
        const box = createInput(ingred);
        const label = createLabel(ingred);
        curIngredsForm.appendChild(ingredDiv);
        ingredDiv.appendChild(box);
        ingredDiv.appendChild(label);
    });
}

function createInput(ingred) {
    const input = document.createElement('input');
    input.setAttribute('type', 'checkbox');
    input.setAttribute('autocomplete', 'off');
    input.setAttribute('id', ingred);
    input.setAttribute('name', ingred);
    return input;
}

function createLabel(element) {
    const label = document.createElement('label');
    label.setAttribute('for', element);
    label.innerText = `${element}`;
    return label;
}

function createRelatedIngreds(rankedIngreds) {
    ingredTable.clear();
    document.getElementById('ingred-loading-icon').classList.toggle('d-none');

    if (rankedIngreds == undefined || rankedIngreds.length == 0) {
        ingredTable.draw();
        return;
    }

    var tableData = [];
    rankedIngreds.forEach(ingred => {
        const ingredName = ingred[0];
        const score = ingred[1];
        const recipes = ingred[2];
        const rowData = { "0": ingredName, "1": score, "2": recipes };
        tableData.push(rowData);
    });

    ingredTable.rows.add(tableData).draw();
    document.getElementById('ingred-loading-icon').classList.add('d-none');
}

function createAddBtn(ingredName) {
    const btn = document.createElement('button');
    btn.setAttribute('class', 'r-ingred-btn btn btn-outline-primary btn-sm');
    btn.setAttribute('name', 'r_ingred');
    btn.setAttribute('value', ingredName);
    btn.textContent = 'Add';
    return btn;
}

function createRecipes(recipes, curIngreds) {
    recipeTable.clear();
    var tableData = [];

    recipes.forEach(recipe => {
        const recipeName = recipe[0];
        const recipeLink = recipe[1];
        const recipeImage = recipe[2];
        const recipeSource = recipe[3];
        const rowData = { '0': recipeName, '1': recipeLink, '2': recipeImage, '3': recipeSource };
        tableData.push(rowData);
    });
    console.time("add");
    recipeTable.rows.add(tableData);
    console.timeEnd("add");

    console.time('draw');
    recipeTable.draw(false);
    console.timeEnd('draw');

    document.getElementById('recipe-loading-icon').classList.add('d-none');
}