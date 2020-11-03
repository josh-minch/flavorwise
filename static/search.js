var search = document.getElementById('search');
search.addEventListener('submit', searchAddIngred);
var relatedIngreds = document.getElementById('r_ingreds');
relatedIngreds.addEventListener('click', addRelatedIngred);
var remove = document.getElementById('cur-ingreds');
remove.addEventListener('submit', removeIngred);


function searchAddIngred(ev) {
    fetchPathEvent(new FormData(this), ev, '/search')
    this.reset();
}


function addRelatedIngred(ev) {
    const isButton = ev.target.nodeName === 'BUTTON';
    if (!isButton) {
        return;
    }
    var formData = new FormData();
    formData.append('search', String(ev.target.value))
    fetchPathEvent(formData, ev, '/search');
}


function removeIngred(ev) {
    fetchPathEvent(new FormData(this), ev, '/remove')
}

function fetchPathEvent(formData, ev, path) {
    ev.preventDefault();
    fetch(path, {
        method: 'POST',
        body: formData
    })
        .then(parseJSON)
        .then(updateDisplay);
}

function parseJSON(response) {
    return response.json();
}

function updateDisplay(json_data) {
    removeAllChild(document.getElementById('cur-ingreds'));
    removeAllChild(document.getElementById('r_ingreds'));
    removeAllChild(document.getElementById('recipes'));
    createCurIngreds(json_data.cur_ingreds);
    createRelatedIngreds(json_data.r_ingreds);
    createRecipes(json_data.recipes, json_data.cur_ingreds);
}

function removeAllChild(node) {
    while (node.firstChild) {
        node.removeChild(node.firstChild);
    }
}

function createCurIngreds(cur_ingreds) {
    const curIngredsDiv = document.querySelector('#cur-ingreds');

    cur_ingreds.forEach(element => {
        const ingred = document.createElement('span');
        const box = createInput(element);
        const label = createLabel(element);
        curIngredsDiv.appendChild(ingred);
        ingred.appendChild(label);
        label.prepend(box);
    });
    const btn = createRemoveBtn();
    curIngredsDiv.appendChild(btn);
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
    btn.setAttribute('type', 'submit');
    btn.setAttribute('value', 'Remove');
    btn.setAttribute('id', 'remove-button');
    return btn;
}

function createRelatedIngreds(rankedIngreds) {
    const rankedIngredsDiv = document.querySelector('#r_ingreds');

    rankedIngreds.forEach(element => {
        const ingred = document.createElement('button');
        ingred.setAttribute('type', 'button');
        ingred.setAttribute('class', 'btn btn-outline-primary btn-sm');
        ingred.setAttribute('value', element);
        ingred.innerText = element
        rankedIngredsDiv.appendChild(ingred)
    });
}

function createRecipes(recipes, cur_ingreds) {
    const recipesSec = document.querySelector('#recipes');
    const recipesTitleDiv = createRecipesTitle(recipes, cur_ingreds);
    const recipesBodyDiv = createRecipesBody(recipes);

    recipesSec.appendChild(recipesTitleDiv);
    recipesSec.appendChild(recipesBodyDiv);
}

function createRecipesTitle(recipes, curIngreds) {
    const div = document.createElement('div');
    div.setAttribute('class', 'recipe-title');
    if (curIngreds.length == 0) {
        div.innerText = 'Recipes'
    } else if (curIngreds.length > 0 && recipes.length == 1) {
        div.innerText = `${recipes.length} recipe with `;
    } else if (curIngreds.length > 0 && recipes.length > 1) {
        div.innerText = `${recipes.length} recipes with `;
    }

    const curIngredsText = curIngreds.join(', ');
    const span = document.createElement('span');
    span.setAttribute('class', 'bold-ingred');
    span.innerText = curIngredsText;
    div.appendChild(span);

    return div
}

function createRecipesBody(recipes) {
    const recipesBody = document.createElement('div');

    for (let i = 0; i < recipes.length; i++) {
        const recipe = document.createElement('div');

        const link = document.createElement('a');
        recipe.appendChild(link)
        link.setAttribute('href', recipes[i][1]);
        link.innerText = recipes[i][0];
        recipe.appendChild(link)

        if (i < recipes.length - 1) {
            const span = document.createElement('span');
            span.innerText = ', '
            recipe.appendChild(span)
        }

        recipesBody.appendChild(recipe)
    }

    return recipesBody
}


