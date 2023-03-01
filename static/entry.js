$(function() {
    $('#search-yelp').on('click', searchYelp)
    $('#results').on('click', '.result', selectBusiness)
    $('#delete-btn').on('submit', deleteEntry)
    $('.yelp-param').on('keypress', onYelpParamEnter)
});

function deleteEntry(e) {
    const result = confirm("Are you sure you want to delete?")
    if (!result) {
        e.preventDefault()
    }
}

function selectBusiness(e) {
    $('#search-yelp-modal').modal('hide')
    const selected = e.target.closest('.result')
    const yelp_id = selected.dataset.yelp_id
    const yelp_name = selected.dataset.yelp_name
    $('#yelp_id').val(yelp_id)
    $('#name').val(yelp_name)
}

function onYelpParamEnter(e) {
    if (e.which == '13') {
        e.preventDefault()
        searchYelp(e)
    }
}

async function searchYelp(e) {
    e.preventDefault()
    $('#results').empty()
    $('#search-yelp-modal').modal('show')
    let response = null;
    let error = null;
    try {
        response = await getRestaurants($('#name').val(), $('#location').val())
    } catch(err) {
        error = err.response.data
    }
    
    if (!error && response.data.length == 0)
        error = "No results found"

    $('#spinner').hide()
    $('#results').show()
    if (error) {
        $('#results').append($('<span>', {text: error}))
    } else {
        for (business of response.data) {
            $('<div>', {class:'my-1 btn btn-outline-success d-block text-start result'}).attr({'data-yelp_id': business.id, 'data-yelp_name':business.name}).append([
                    $('<p>', {class:'fw-bold', text:business.name}),
                    $('<p>', {html:business.address})
                ]).appendTo($('#results'))
        }
    }
}

async function getRestaurants(term, location) {
    const url = `${window.location.protocol + "//" + window.location.host}/yelp-search?term=${term}&location=${location}`;
    const response = await axios.get(url);
    return response;
}