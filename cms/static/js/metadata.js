function editMetadata(item) {
    $(item).toggleClass('kv-active')
    $('#kv_id').val($(item).data("metadata-id"));
    $('#kv_new_key_name').val($(item).data("key"));
    $('#kv_new_key_value').val($(item).data("value"));
    setMetadataEditorToSave();
}

function clearMetadata(item) {
    $('#kv_' + $('#kv_id').val()).toggleClass('kv-active');
    $('#kv_id').val('');
    $('#kv_new_key_name').val('');
    $('#kv_new_key_value').val('');
    setMetadataEditorToAdd()
}

function addMetadata() {
    $.post(
        addMetadataLink,
        $.param({
            key: $('#kv_new_key_name').val(),
            value: $('#kv_new_key_value').val()
        })
    ).done(function (data) {
        $('#kv_listing').html(data);
        clearMetadata();
        metadataListInit();
    })
}

function removeMetadata() {
    $.post(
        removeMetadataLink,
        $.param({
            key: $('#kv_new_key_name').val(),
        })
    ).done(function (data) {
        $('#kv_listing').html(data);
        clearMetadata();
        metadataListInit();
    })
}

function setMetadataEditorToSave() {
    $('#kv_add_button').text('Save');
    $('#kv_delete_button').show();
}

function setMetadataEditorToAdd() {
    $('#kv_add_button').text('Add');
    $('#kv_delete_button').hide();
}

function metadataListInit() {
    $('.metadata-item').on('click', function () {
        editMetadata(this);
    });
    $('#kv_add_button').on('click', function () {
        addMetadata();
    })
    $('#kv_delete_button').on('click', function () {
        removeMetadata();
    })

}