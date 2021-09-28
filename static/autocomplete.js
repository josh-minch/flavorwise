var all_ingreds = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: 'static/all_ingreds_filtered.json'
});

$('#bloodhound .typeahead').typeahead({
    hint: true,
    highlight: true,
    minLength: 0,
    autoselect: true
},
    {
        name: 'all_ingreds',
        source: all_ingreds,
        limit: Infinity
    });

// Autofocus on typeahead search field
$('.typeahead').focus();