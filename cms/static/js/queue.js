function refreshQueue() {
    $.get(`/blog/${blog_id}/queue-button`, function(data) {
        $("#queue-button").replaceWith(data);
    })
}