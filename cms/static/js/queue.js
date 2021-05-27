function refreshQueue() {
    $.get(`/blog/${blog_id}/queue-badge`, function(data) {
        $("#queue-badge").replaceWith(data);
    })
}