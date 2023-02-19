$(function() {
    $('#search-yelp').on('click', searchYelp)
    $('#results').on('click', '.result', selectBusiness)
    $('#delete-btn').on('submit', deleteEntry)
});

function deleteEntry(e) {
    const result = confirm("Are you sure you want to delete?")
    if (!result) {
        e.preventDefault()
    }
}

function selectBusiness(e) {
    $('#search-yelp-modal').modal('hide')
    const yelp_id = e.target.closest('.result').dataset.yelp_id
    $('#yelp_id').val(yelp_id)
}

async function searchYelp(e) {
    $('#results').empty()
    $('#search-yelp-modal').modal('show')
    let response = null;
    let error = null;
    try {
        response = await getRestaurants($('#name').val(), $('#location').val())
    } catch(err) {
        error = err.response.data
    }
    
    $('#spinner').hide()
    $('#results').show()
    if (error) {
        $('#results').append($('<span>', {text: error}))
    } else {
        for (business of response.data) {
            $('<div>', {class:'my-1 btn btn-outline-success d-block text-start result'}).attr('data-yelp_id', business.id).append([
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