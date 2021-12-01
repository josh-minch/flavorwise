$.fn.DataTable.ext.pager.numbers_length = 9;
const ingredTablePercent = 0.75;
const ingredTableUsableHeight = ingredTablePercent * window.innerHeight;
const numIngredTableRows = Math.round(ingredTableUsableHeight / 50);
const numRecipeTableRows = 4;
$('#ingred-table').DataTable({
    dom: "<if>t<lp>",
    deferRender: true,
    ajax: {
        url: "/init_r_ingred_data",
        dataSrc: "",
    },
    autoWidth: false,
    columnDefs: [
        { width: '19%', targets: 2 },
        { width: '14%', targets: 3 },
        { className: "pl-0", "targets": [0] },
        { className: "text-right pr-0", "targets": [3] },
        { orderable: false, targets: [0, 3] },
        { orderSequence: ["desc", "asc"], targets: [1, 2] },
        {
            targets: -1,
            render: function (data, type, row) {
                let btn = '<button type="button" class="r-ingred-btn btn btn-outline-primary" name="r_ingred" value="' + row[0] + '">Add</button>';
                return btn;
            }
        }
    ],
    order: [[1, "desc"]],
    pageLength: numIngredTableRows,
    lengthChange: false,
    language: {
        emptyTable: " ",
        info: "_TOTAL_ results",
        infoEmpty: "0 results",
        search: "_INPUT_",
        searchPlaceholder: 'Filter results',
        infoFiltered: "(filtered)",
        zeroRecords: "No recommendations match your search filter. Bummer dude!",
        paginate: {
            previous: "Prev"
        }
    },
    initComplete: function () {
        hideTableIfEmpty($('#ingred-table'));
    }
});

console.time("recipes")
let recipesTable = $('#recipe-table').DataTable({
    dom: "<if>t<lp>",
    deferRender: true,
    ajax: {
        url: "/init_recipe_data",
        dataSrc: "",
        cache: true
    },
    autoWidth: false,
    columns: [
        { width: '100%' }
    ],
    columnDefs: [
        {
            visible: false,
            targets: [1, 2],
            searchable: false
        },
        { className: "pl-0", "targets": [0] },
        {
            targets: 0,
            render: function (data, type, row) {
                if (data) {
                    const recipe_card = `
                        <div class="media position-relative">
                            <img src="" data-src="${row[2]}" class="recipe-image">
                            <div class="media-body">
                                <h6 class="recipe-title"><span class="">${row[0]}</span></h6>
                                <span class="recipe-link-row">
                                    <i class="link-icon bi bi-arrow-up-right-square"></i>
                                    <a href="${row[1]}" class="stretched-link recipe-link text-primary">
                                        Recipe at ${row[3]}
                                    </a>
                                </span>
                            </div>
                        </div>
                        `;
                    return recipe_card;
                }
            }
        }
    ],
    pageLength: numRecipeTableRows,
    lengthChange: false,
    language: {
        emptyTable: "Add ingredients to see recipes",
        info: "_TOTAL_ results",
        infoEmpty: "0 results",
        infoFiltered: "(filtered)",
        search: "_INPUT_",
        searchPlaceholder: 'Filter results',
        zeroRecords: "No recipes match your search filter. Bummer dude!",
        paginate: {
            previous: "Prev"
        }
    },
    rowCallback: function (row, data) {
        setRecipeHover()
    },
    drawCallback: function (settings) {
        $("#recipe-table img:visible").unveil();
        setRecipeHover()
    },
    initComplete: function () {
        hideTableIfEmpty($('#recipe-table'));
    }
});
console.timeEnd("recipes")

function setRecipeHover() {
    $(".recipe-link").hover(
        function () {
            const hoverBorderColor = 'rgb(77, 77, 77)';
            $(this).parent().siblings(".recipe-title").children().css('text-decoration', 'underline');
            $(this).siblings(".link-icon").css('color', 'rgb(0, 86, 179)');
            $(this).parent().parent().siblings(".recipe-image").css('border-color', hoverBorderColor);
            $(this).parent().parent().parent().css('border-color', hoverBorderColor);
            $(this).parent().parent().parent().toggleClass('drop-shadow');
        }, function () {
            const borderColor = '#dee2e6';
            $(this).parent().siblings(".recipe-title").children().css('text-decoration', 'none');
            $(this).siblings(".link-icon").css('color', '#007bff');
            $(this).parent().parent().siblings(".recipe-image").css('border-color', borderColor);
            $(this).parent().parent().parent().css('border-color', borderColor);
            $(this).parent().parent().parent().toggleClass('drop-shadow');
        }
    );
}

// Remove bootstrap class from datatable filters for easier custom styling
const tableFilters = document.querySelectorAll('.dataTables_filter label input');
tableFilters.forEach(filter => {
    filter.classList.remove("form-control", "form-control-sm")
});

let checkboxes = document.querySelectorAll("input[type='checkbox']");
setRemoveButtonState()
checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', setRemoveButtonState)
});

function setRemoveButtonState() {
    let checkboxes = document.querySelectorAll("input[type='checkbox']");
    let numChecked = 0;
    checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
            numChecked++;
        }
    });

    let selectedIngredText = document.getElementById('selected-ingred-text');
    selectedIngredText.textContent = numChecked + " selected"

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

function hideTableIfEmpty(table) {
    if (table.find('tbody tr td').first().hasClass('dataTables_empty')) {
        table.hide();
        // hide table's pagination also
        table.parent().find('div.dataTables_paginate').hide();
    } else {
        table.show();
        table.parent().find('div.dataTables_paginate').show();
    }
}

function toggleTableOnDataChange(table) {
    table.on('DOMNodeInserted DOMNodeRemoved', function () {
        hideTableIfEmpty(table);
    });
}

toggleTableOnDataChange($('#ingred-table'));
toggleTableOnDataChange($('#recipe-table'));

const search = document.getElementById('search');
search.addEventListener('submit', searchAddIngred);

/* When selecting a dropdown ingredient, add ingredient to current ingredients,
close dropdown, and clear search field. */
$('.typeahead').on('typeahead:selected', function (ev, ingred) {
    addDropdownIngred(ingred);
    $('.typeahead').typeahead('close');
    $('.typeahead').typeahead('val', '');
})

const relatedIngreds = document.getElementById('r-ingreds');
relatedIngreds.addEventListener('click', addRelatedIngred);

const remove = document.getElementById('cur-ingreds');
remove.addEventListener('submit', removeIngred);

function searchAddIngred(ev) {
    fetchPathEvent(new FormData(this), ev, '/search')
    // Clear search field after adding ingred
    this.reset();
}

function addDropdownIngred(ingred) {
    var formData = new FormData();
    formData.append('ingred_to_add', ingred)

    fetch('/add_dropdown_ingred', {
        method: 'POST',
        body: formData
    })
        .then(parseJSON)
        .then(updateDisplay);
}

function addRelatedIngred(ev) {
    const isButton = ev.target.nodeName === 'BUTTON';
    if (!isButton) {
        return;
    }
    var formData = new FormData();
    formData.append('search', String(ev.target.value))
    fetchPathEvent(formData, ev, '/search');
    // Clear table filters
    $('#ingred-table').DataTable().search('').draw();
    $('#recipe-table').DataTable().search('').draw();
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

function removeCurIngreds() {
    curIngreds = document.querySelectorAll('.cur-ingred');
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
    let table = $('#ingred-table').DataTable();

    table.clear();

    if (rankedIngreds == undefined || rankedIngreds.length == 0) {
        table.draw();
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

    table.rows.add(tableData).draw();
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
    recipesTable.clear();
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
    recipesTable.rows.add(tableData);
    console.timeEnd("add");

    console.time('draw');
    recipesTable.draw(false);
    console.timeEnd('draw');
}