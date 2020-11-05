var search = document.getElementById('search');
search.addEventListener('submit', searchAddIngred);
var relatedIngreds = document.getElementById('r-ingreds');
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

function updateDisplay(jsonData) {
    removeAllChild(document.getElementById('cur-ingreds'));
    removeAllChild(document.getElementById('r-ingreds'));
    removeAllChild(document.getElementById('recipes'));
    createCurIngreds(jsonData.cur_ingreds);
    createRelatedIngreds(jsonData.r_ingreds);
    createRecipes(jsonData.recipes, jsonData.cur_ingreds);
}

function removeAllChild(node) {
    while (node.firstChild) {
        node.removeChild(node.firstChild);
    }
}

function createCurIngreds(curIngreds) {
    const curIngredsDiv = document.querySelector('#cur-ingreds');

    curIngreds.forEach(ingred => {
        const ingredSpan = document.createElement('span');
        ingredSpan.setAttribute('class', 'cur-ingred')
        const box = createInput(ingred);
        const label = createLabel(ingred);
        curIngredsDiv.appendChild(ingredSpan);
        ingredSpan.appendChild(label);
        label.prepend(box);
    });
    if (curIngreds.length > 0) {
        const btn = createRemoveBtn();
        curIngredsDiv.appendChild(btn);
    }
}

function createInput(ingred) {
    const input = document.createElement('input');
    input.setAttribute('type', 'checkbox');
    input.setAttribute('id', ingred);
    input.setAttribute('name', ingred);
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
    const rankedIngredsDiv = document.querySelector('#r-ingreds');

    rankedIngreds.forEach(ingred => {
        const btn = document.createElement('button');
        btn.setAttribute('type', 'button');
        btn.setAttribute('class', 'r-ingred btn btn-outline-primary btn-sm');
        btn.setAttribute('value', ingred);
        btn.innerText = ingred;
        rankedIngredsDiv.appendChild(btn)
    });
}

function createRecipes(recipes, curIngreds) {
    const recipesSec = document.querySelector('#recipes');
    const recipesTitleDiv = createRecipesTitle(recipes, curIngreds);
    const recipesBodyDiv = createRecipesBody(recipes);

    recipesSec.appendChild(recipesTitleDiv);
    recipesSec.appendChild(recipesBodyDiv);
}

function createRecipesTitle(recipes, curIngreds) {
    const introSpan = document.createElement('span');
    introSpan.setAttribute('class', 'recipe-intro');

    const prepSpan = document.createElement('span');
    prepSpan.setAttribute('class', 'recipe-prep');
    prepSpan.innerText = 'with '

    if (curIngreds.length == 0) {
        introSpan.innerText = 'Recipes'
    } else if (curIngreds.length > 0 && recipes.length == 1) {
        introSpan.innerText = `${recipes.length} recipe `;
        introSpan.append(prepSpan);
    } else if (curIngreds.length > 0 && recipes.length > 1) {
        introSpan.innerText = `${recipes.length} recipes `;
        introSpan.append(prepSpan);
    }

    const curIngredsText = curIngreds.join(', ');
    const recipeSpan = document.createElement('span');
    recipeSpan.setAttribute('class', 'recipe-ingred');
    recipeSpan.innerText = curIngredsText;
    introSpan.appendChild(recipeSpan);

    return introSpan
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

        recipesBody.appendChild(recipe)
    }

    return recipesBody
}


