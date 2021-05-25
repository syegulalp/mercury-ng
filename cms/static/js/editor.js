var tagSearch = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
        url: `${tagFetchLink}/%QUERY`,
        wildcard: '%QUERY'
    }
});

function getEditorHeight() {
    wheight = parseInt($(window).height());
    wtop = parseInt($("#post-text-div").offset().top);
    return wheight - wtop - 16;
}


function resizeEditor() {
    tinymce.activeEditor.editorContainer.style.height = getEditorHeight() + "px"
}

function cleanText() {
    txt = tinymce.activeEditor.getContent();
    txt = txt.replace(/\u00A0/g, " ");
    tinymce.activeEditor.setContent(txt);

}

function mediaListInit() {
    $('.media-list-img').on('click', function() {
        id = $(this).data('media-id');
        selectImageTemplate(id);
    })


}

function openImageBrowser() {
    $('#modal-body').modal('hide');
    $('#modal-container').html('');
    $.get(mediaInsertLink).done(function(data) {
        $('#modal-container').html(data);
        $('#modal-body').modal('show');
        mediaListInit();
    })
}

function selectImageTemplate(image_id) {
    $('#modal-body').modal('hide');
    $('#modal-container').html('');
    $.get(`${mediaTemplatesLink}/${image_id}`).done(function(data) {
        $('#modal-container').html(data);
        $('#modal-body').modal('show');
        $('.media-list-template').on('click', function() {
            template_id = $(this).data('template-id');
            $.get(mediaRenderLink + '/' + image_id + '/' + template_id).done(function(data) {
                tinymce.activeEditor.insertContent(data);
                $('#modal-body').modal('hide');
            });
        })
    });
}

function initEditor() {
    tinymce.init({
        selector: '#post_text',
        plugins: 'link fullscreen code lists pagebreak wordcount',
        browser_spellcheck: true,
        menubar: false,
        convert_urls: false,
        content_css: `${blogPermalink}/_static/css/editor.css`,
        entity_encoding: 'raw',
        pagebreak_separator: "<!-- pagebreak -->",
        height: getEditorHeight(),
        style_formats: [{
            title: 'Custom',
            items: [
                { title: 'Small', inline: 'small' }
            ]
        }, ],
        style_formats_merge: true,
        init_instance_callback: function(editor) {
            editor.on("keydown", function(e) {
                if (e.ctrlKey) {
                    if (e.code == 'KeyS') {
                        e.preventDefault();
                        $('#save-button').click();
                    }
                }
            });
        },
        toolbar: 'savebutton | styleselect | ' +
            'bold italic | alignleft aligncenter ' +
            'alignright alignjustify | bullist numlist | outdent indent blockquote pagebreak image | ' +
            'removeformat | link | fullscreen | code | undo redo | cleanup |',
        setup: (editor) => {
            editor.ui.registry.addButton('savebutton', {
                text: 'Save',
                icon: "save",
                onAction: () => $('#save-button').click()
            });
            editor.ui.registry.addButton('image', {
                icon: "image",
                onAction: () => openImageBrowser()
            });
            editor.ui.registry.addButton('cleanup', {
                text: 'Clean',
                onAction: () => cleanText()
            });
        },

    });
}

function savePost() {
    tinymce.activeEditor.save();
    form = $("#texteditorform").serialize();
    $("#save-indicator").text("\u23F3 ")
    resetNotification();
    resetDropMessage();
    $.post(
        "save",
        form
    ).done(function(data) {
        $("#save-indicator").text("");
        data = JSON.parse(data)
        showNotification("success", data[1]);
        $("#sidebar-column").html(data[0]);
        initSidebarButtons();
        redir = data[3];
        if (redir.length > 0) {
            window.location = redir;
        }
        popup = data[2];
        if (popup.length > 0) {
            var win = window.open(popup, $('#post-basename').val());
            win.focus();
        }
        queue_button = data[4];
        $("#queue-button").replaceWith(queue_button);
    }).fail(function(data) {
        $("#save-indicator").text("\u26d4")
        showNotification("danger", data);
    })
}

function refreshQueue() {
    $.get(`/blog/${blog_id}/queue-button`, function(data) {
        $("#queue-button").replaceWith(data);
    })
}

function addTag(item) {
    tag_to_add = $(item).typeahead('val');
    $.post(
        addTagLink,
        $.param({ tag: tag_to_add })
    ).done(function(data) {
        console.log(data)
        $('#tag-list').html(data);
        $(item).typeahead('val', '');
        $(item).typeahead('close');
        setTagActions();
    })
}

function removeTag(item) {
    tag_to_remove = $(item).data('tag');
    $.post(
        removeTagLink,
        $.param({ tag: tag_to_remove })
    ).done(function(data) {
        console.log(data)
        $('#tag-list').html(data);
        setTagActions();
    })
}

function setTagActions() {
    $('.tag-remove').on('click', function(e) {
        e.preventDefault();
        removeTag(this);
    })
}


function refreshMediaList() {
    $.get(`${mediaInsertLink}/refresh`).done(function(data) {
        $('#sidebar-media-list').html(data);
        mediaListInit();
    })
}

function initEnterBehaviors() {
    $(".enter-to-save").each(function() {
        $(this).on('keydown', function(e) {
            if (e.originalEvent.key == 'Enter') {
                console.log(e);
                e.preventDefault();
                $('#save-button').click();
                $('#save-new-button').click();
            }

        })
    })
}

function initSidebarButtons() {
    $("#save-new-button").on("click", function() {
        $("#texteditorform").submit();
    });

    $('.save-action').on("click", function() {
        $("#save_action").val($(this).data("action"));
        savePost();
    });

    $('#close_edit').on("click", function() {
        $("#save_action").val("Close and release edit lock");
        savePost();
    })

    $('#tag-input').typeahead({
        autoselect: true,
        highlight: true,
        minLength: 2,

    }, {
        name: 'tag-suggestions',
        source: tagSearch,
        display: 'value',
    });

    setTagActions();

    $('#tag-input').bind('typeahead:select', function() {
        addTag(this);
    });

    $('#tag-input').bind('typeahead:asyncrequest', function(obj, query, dataset) {
        $('#tag-progress').text(' \u23F3');
    });

    $('#tag-input').bind('typeahead:asyncreceive', function(obj, query, dataset) {
        $('#tag-progress').text('');
    });

    $('#tag-input').bind('typeahead:asynccancel', function(obj, query, dataset) {
        $('#tag-progress').text('');
    });

    $('#tag-input').on('keydown', function(e) {
        if (e.originalEvent.key == "Enter") {
            e.preventDefault();
            addTag(this);
            if ($('#tag-input_listbox').css("display") == "none") {

            }
        }
    })

    mediaListInit();

    metadataListInit();

    $('#add_media_button').on("click", function() {
        media_id = $('#add_media_id').val();
        $.post(
            "add-media-ref", { media_id: media_id }
        ).done(function() {
            showOk(`Media item ${media_id} added.`);
            $('#add_media_id').val('');
            refreshMediaList();
        }).fail(function() {
            showFail(`Media item ${media_id} not found.`);
        })
    })

    $('#remove_media_button').on("click", function() {
        media_id = $('#add_media_id').val();
        $.post(
            "remove-media-ref", { media_id: media_id }
        ).done(function() {
            showOk(`Media item ${media_id} removed.`);
            $('#add_media_id').val('');
            refreshMediaList();
        }).fail(function() {
            showFail(`Media item ${media_id} not found.`);
        })
    })

    $('#regenerate_basename').on("click", function() {
        $.post(
            'regen-basename', {
                title: $('#post_title').val(),
                basename: $('#post-basename').val()
            }
        ).done(function(data) {
            console.log(data);
            $('#post-basename').val(data);
            $('#regenerate_basename').hide();
        })
    })

    $('#post-basename-addon').on("click", function() {
        $('#post-basename').prop('disabled', false);
        $('#regenerate_basename').show();
    })

    initEnterBehaviors();

}

$(document).ready(function() {
    initEditor();
    initSidebarButtons();
    $(window).on("resize", resizeEditor);
    window.addEventListener('beforeunload', function(e) {
        var isDirty = tinymce.activeEditor.isDirty()
        if (isDirty) {
            e.preventDefault();
            e.returnValue = '';
        }
    });
    window.setInterval(refreshQueue, 60000);
})