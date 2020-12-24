$(document).ready(function () {
    $('#ingred-table').DataTable({
        dom: "<if>t<lp>",
        columnDefs: [
            { className: "pl-0", "targets": [0] },
            { className: "text-right pr-0", "targets": [3] },
            { orderable: false, targets: [0, 3] },
            {
                targets: -1,
                render: function (data, type, row) {
                    let btn = '<button type="button" class="r-ingred btn btn-outline-primary" name="r_ingred" value="' + row[0] + '">Add</button>'
                    return btn;
                }
            }
        ],
        aoColumns: [
            null,
            { "orderSequence": ["desc", "asc"] },
            { "orderSequence": ["desc", "asc"] },
            null
        ],
        order: [[1, "desc"]],
        pageLength: 11,
        lengthChange: false,
        language: {
            emptyTable: "Add an ingredient to see recommendations",
            info: "_TOTAL_ results based on your ingredients",
            infoEmpty: "0 results based on your ingredients",
            search: "_INPUT_",
            searchPlaceholder: "Filter results",
            infoFiltered: "and filter",
            zeroRecords: "No ingredients match your search filter. Bummer dude!"
        }
    });
});

var search = document.getElementById('search');
search.addEventListener('submit', searchAddIngred);
search.addEventListener('change', searchAddIngred);
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
    let table = $('#ingred-table').DataTable();

    table.clear();
    var tableData = [];
    rankedIngreds.forEach(ingred => {
        const ingredName = ingred[0];
        const score = ingred[1];
        const recipes = ingred[2];
        const rowData = { "0": ingredName, "1": score, "2": recipes };
        tableData.push(rowData);
    });

    table.rows.add(tableData).draw();

    /* const rankedIngredsDiv = document.querySelector('#r-ingreds');

    rankedIngreds.forEach(ingred => {
        const btn = document.createElement('button');
        btn.setAttribute('type', 'button');
        btn.setAttribute('class', 'r-ingred btn btn-outline-primary btn-sm');
        btn.setAttribute('value', ingred);
        btn.innerText = ingred;
        rankedIngredsDiv.appendChild(btn)
    });

    <button type="button"
    class="r-ingred btn btn-outline-primary btn-sm" name="r_ingred"
    value="{{r_ingred.0}}">Add</button>

    */
}

function createAddBtn(ingredName) {
    const btn = document.createElement('button');
    btn.setAttribute('class', 'r-ingred btn btn-outline-primary btn-sm');
    btn.setAttribute('name', 'r_ingred');
    btn.setAttribute('value', ingredName);
    btn.textContent = 'Add';
    return btn
}

function createRecipes(recipes, curIngreds) {
    const recipesSec = document.querySelector('#recipes');
    const recipesTitleDiv = createRecipesTitle(recipes, curIngreds);
    const recipesBodyDiv = createRecipesBody(recipes);

    recipesSec.appendChild(recipesTitleDiv);
    recipesSec.appendChild(recipesBodyDiv);
}

function createRecipesTitle(recipes, curIngreds) {
    const titleSpan = document.createElement('span');

    appendRecipesTitleIntro(titleSpan, recipes, curIngreds);
    appendRecipesTitleIngreds(titleSpan, recipes, curIngreds);

    return titleSpan
}

function appendRecipesTitleIntro(titleSpan, recipes, curIngreds) {
    /* Append title intro text to titleSpan of the form 'Recipes' or
    '1 recipe with ' or '5 recipes with 'depending on length of input arrays. */
    const introSpan = document.createElement('span');
    introSpan.setAttribute('class', 'recipe-intro');
    titleSpan.append(introSpan);

    const withSpan = document.createElement('span');
    withSpan.setAttribute('class', 'recipe-prep');
    withSpan.innerText = 'with '

    if (curIngreds.length == 0) {
        introSpan.innerText = 'Recipes'
    } else if (curIngreds.length > 0 && recipes.length == 1) {
        introSpan.innerText = `${recipes.length} recipe `;
        titleSpan.insertBefore(withSpan, introSpan.nextSibling);
    } else if (curIngreds.length > 0 && recipes.length != 1) {
        introSpan.innerText = `${recipes.length} recipes `;
        titleSpan.insertBefore(withSpan, introSpan.nextSibling);
    }
}

function appendRecipesTitleIngreds(titleSpan, recipes, curIngreds) {
    /* Append ingred text to titleSpan of the form 'butter' or
    'butter & garlic' or 'butter, garlic, & lemon' depending on
    length of input arrays. */
    const ingredSpan = document.createElement('span');
    ingredSpan.setAttribute('class', 'recipe-ingred');
    titleSpan.appendChild(ingredSpan);

    if (curIngreds.length == 1) {
        ingredSpan.innerText = curIngreds;
    } else if (curIngreds.length > 1) {
        const ampersandSpan = document.createElement('span');
        ampersandSpan.setAttribute('class', 'recipe-prep');
        const finalIngredSpan = document.createElement('span');
        finalIngredSpan.setAttribute('class', 'recipe-ingred');

        // Get all but last ingred and separate with commas
        ingredSpan.innerText = curIngreds.slice(0, curIngreds.length - 1).join(', ');
        if (curIngreds.length == 2) {
            ampersandSpan.innerText = ' & ';
        } else {
            ampersandSpan.innerText = ', & ';
        }
        finalIngredSpan.innerText = curIngreds.slice(curIngreds.length - 1);

        titleSpan.insertBefore(ampersandSpan, ingredSpan.nextSibling);
        titleSpan.insertBefore(finalIngredSpan, ampersandSpan.nextSibling);

        if (recipes.length == 0) {
            const noRecipesSpan = document.createElement('span');
            noRecipesSpan.setAttribute('class', 'recipe-prep');
            noRecipesSpan.innerText = '. Bummer dude!'
            titleSpan.insertBefore(noRecipesSpan, finalIngredSpan.nextSibling);
        }
    }
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


