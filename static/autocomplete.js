import { distance } from "./fastest-levenshtein.1.0.12.min.js";

let all_ingreds = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: 'static/all_ingreds_filtered.json',
    sorter: function (a, b) {
        let input_string = document.getElementById('search-input').value
        return distance(a, input_string) - distance(b, input_string);
    }
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