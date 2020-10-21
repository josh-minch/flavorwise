var search = document.getElementById('search');
search.addEventListener('submit', searchSubmit);
var remove = document.getElementById('cur-ingreds')
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
    removeAllChild(document.getElementById('cur-ingreds'));
    removeAllChild(document.getElementById('r_ingreds'));
    removeAllChild(document.getElementById('recipes'));
    createCurIngreds(json_data.cur_ingreds);
    createRankedIngreds(json_data.r_ingreds);
    createRecipes(json_data.recipes, json_data.cur_ingreds);
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
    btn.setAttribute('type', "submit");
    btn.setAttribute('value', "Remove");
    btn.setAttribute('id', "remove-button");
    return btn;
}

function createRankedIngreds(rankedIngreds) {
    const rankedIngredsSec = document.querySelector('#r_ingreds');
    const rankedIngredsText = rankedIngreds.join(", ");
    rankedIngredsSec.innerText = rankedIngredsText
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

    const curIngredsText = curIngreds.join(", ");
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


function removeAllChild(node) {
    while (node.firstChild) {
        node.removeChild(node.firstChild);
    }
}



