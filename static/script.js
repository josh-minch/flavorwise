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
    addDropdownIngred(ingred, ev);
    $('.typeahead').typeahead('close');
    $('.typeahead').typeahead('val', '');
})

function searchAddIngred(ev) {
    let ingredForm = new FormData(this);
    let formData = new FormData();
    for (let ingred of ingredForm.keys()) {
        formData.append('add', ingred)
    }
    handleUserInput(formData, ev, '/add');
    // Clear search field after adding ingred
    this.reset();
}

function addDropdownIngred(ingred, ev) {
    let formData = new FormData();
    formData.append('add', ingred)
    handleUserInput(formData, ev, '/add');
}

function addRelatedIngred(ev) {
    const isButton = ev.target.nodeName === 'BUTTON';
    if (!isButton) {
        return;
    }
    let formData = new FormData();
    formData.append('add', String(ev.target.value))
    handleUserInput(formData, ev, '/add');
    // Clear table filters
    ingredTable.search('').draw();
    recipeTable.search('').draw();
}

function removeIngred(ev) {
    let formData = new FormData(this);
    handleUserInput(formData, ev, '/remove');
}

function handleUserInput(formData, ev, path) {
    ev.preventDefault();

    // Show loading icon
    document.getElementById('ingred-loading-icon').classList.remove('d-none');

    async function fetchIngreds() {
        let res = await fetch(path, {
            method: 'POST',
            body: formData
        });
        let curIngreds = await res.json();
        updateCurIngredsView(curIngreds);
        return await curIngreds;
    }

    fetchIngreds().then((curIngreds) => {
        let ingredFormData = new FormData();
        curIngreds.forEach(curIngred =>
            ingredFormData.append('add', curIngred)
        );
        fetch('/get_table_data', {
            method: 'POST',
            body: ingredFormData
        })
            .then(parseJSON)
            .then(updateTableView)
            .finally(hideLoadingIcon);
    });
}

function parseJSON(response) {
    return response.json();
}

function updateCurIngredsView(curIngreds) {
    toggleRemoveDisplay(curIngreds);
    toggleRandomIngredDisplay(curIngreds);

    removeCurIngreds();
    createCurIngreds(curIngreds);

    let checkboxes = document.querySelectorAll("input[type='checkbox']");
    setRemoveButtonState()
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', setRemoveButtonState)
    });
}

function updateTableView(jsonData) {
    createRelatedIngreds(jsonData.r_ingreds);
    createRecipes(jsonData.recipes);
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
        const box = createCheckbox(ingred);
        const label = createLabel(ingred);
        curIngredsForm.appendChild(ingredDiv);
        ingredDiv.appendChild(box);
        ingredDiv.appendChild(label);
    });
}

function createCheckbox(ingred) {
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

    let tableData = [];
    rankedIngreds.forEach(ingred => {
        const ingredName = ingred[0];
        const score = ingred[1];
        const recipes = ingred[2];
        const rowData = { "0": ingredName, "1": score, "2": recipes };
        tableData.push(rowData);
    });

    ingredTable.rows.add(tableData).draw();
}

function createAddBtn(ingredName) {
    const btn = document.createElement('button');
    btn.setAttribute('class', 'r-ingred-btn btn btn-outline-primary btn-sm');
    btn.setAttribute('name', 'r_ingred');
    btn.setAttribute('value', ingredName);
    btn.textContent = 'Add';
    return btn;
}

function createRecipes(recipes) {
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
}

function hideLoadingIcon() {
    document.getElementById('ingred-loading-icon').classList.add('d-none');
}