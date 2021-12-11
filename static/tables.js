$.fn.DataTable.ext.pager.numbers_length = 9;
const ingredTablePercent = 0.75;
const ingredTableUsableHeight = ingredTablePercent * window.innerHeight;
const numIngredTableRows = Math.round(ingredTableUsableHeight / 70);
const numRecipeTableRows = 4;

let ingredTable = $('#ingred-table').DataTable({
    dom: "<if>t<lp>",
    deferRender: true,
    ajax: {
        url: "/init_r_ingred_data",
        dataSrc: "",
    },
    autoWidth: false,
    columnDefs: [
        { visible: false, targets: 2 },
        { width: '15%', targets: 3 },
        { className: "pl-0", "targets": [0] },
        { className: "text-right pr-0", "targets": [3] },
        { orderable: false, targets: [0, 3] },
        { orderSequence: ["desc", "asc"], targets: [1] },
        {
            targets: 0,
            render: function (data, type, row) {
                // Add s to end of "recipe" if recipe != 1
                const recipeEndingChar = row[2] != 1 ? 's' : '';
                const numRecipesText = `${row[2]} recipe${recipeEndingChar}`
                let ingred = `<div class="ingred-name">${row[0]}</div>
                <div class="num-recipes"><span class="with">with</span> ${numRecipesText}</div>`;
                return ingred;
            }
        },
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
    processing: true,
    initComplete: function () {
        hideTablesIfCurIngredsEmpty($('#ingred-table'));
    }
});

let recipeTable = $('#recipe-table').DataTable({
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
    processing: true,
    rowCallback: function (row, data) {
        setRecipeHover()
    },
    drawCallback: function (settings) {
        $("#recipe-table img:visible").unveil();
        setRecipeHover()
    },
    initComplete: function () {
        hideTablesIfCurIngredsEmpty($('#recipe-table'));
    }
});

toggleTableOnDataChange($('#ingred-table'));
toggleTableOnDataChange($('#recipe-table'));

// Remove bootstrap class from datatable filters for easier custom styling
const tableFilters = document.querySelectorAll('.dataTables_filter label input');
tableFilters.forEach(filter => {
    filter.classList.remove("form-control", "form-control-sm")
});

function toggleTableOnDataChange(table) {
    table.on('DOMNodeInserted DOMNodeRemoved', function () {
        hideTablesIfCurIngredsEmpty();
    });
}

function hideTablesIfCurIngredsEmpty() {
    /* Show tables and related info and hide empty table descriptions based
    if user has selected ingredients. Check current ingreds list length to
    see this  */
    if (document.getElementById('cur-ingreds-list').children.length > 0) {
        displayElementsByClassName('dataTable', 'd-table');
        displayElementsByClassName('dataTables_info', 'd-block');
        displayElementsByClassName('dataTables_paginate', 'd-block');
        displayElementById('r-ingreds', 'd-block');
        displayElementById('recipes', 'd-block');
        displayElementsByClassName('table-description', 'd-block');
        hideElementsByClassName('empty-table-description', 'd-block');
    } else {
        hideElementsByClassName('dataTable', 'd-table');
        hideElementsByClassName('dataTables_info', 'd-block');
        hideElementsByClassName('dataTables_paginate', 'd-block');
        hideElementById('r-ingreds', 'd-block');
        hideElementById('recipes', 'd-block');
        hideElementsByClassName('table-description', 'd-block');
        displayElementsByClassName('empty-table-description', 'd-block');
    }
}

function hideElementById(id, type) {
    element = document.getElementById(id);
    element.classList.add('d-none');
    element.classList.remove(type);
}

function displayElementById(id, type) {
    element = document.getElementById(id);
    element.classList.remove('d-none');
    element.classList.add(type);
}

function hideElementsByClassName(className, type) {
    elements = document.getElementsByClassName(className);
    Array.from(elements).forEach(element => {
        element.classList.add('d-none');
        element.classList.remove(type);
    });
}

function displayElementsByClassName(className, type) {
    elements = document.getElementsByClassName(className);
    Array.from(elements).forEach(element => {
        element.classList.remove('d-none');
        element.classList.add(type);
    });
}

function setRecipeHover() {
    $('.recipe-link').hover(
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