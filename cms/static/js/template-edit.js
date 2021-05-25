function getEditorHeight() {
    wheight = parseInt($(window).height());
    wtop = parseInt($("#template-text-div").offset().top);
    return wheight - wtop - 16;
}

function resizeEditor() {
    $("#template_text").css("height", getEditorHeight() + "px")
}

function saveTemplate() {
    form = $("#templateeditorform").serialize();
    $("#save-indicator").text("\u23F3 ")
    resetNotification();
    $.post(
        "save",
        form
    ).done(function (data) {
        data = JSON.parse(data)
        $("#save-indicator").text("");
        showNotification("success", $(data)[1]);
        $("#sidebar-column").html($(data)[0]);
        initSidebarButtons();
        $("#template_text").data("dirty",false);
        popup = data[2];
        if (popup.length > 0) {
            var win = window.open(popup);
            win.focus();
        }
    }).fail(function (data) {
        $("#save-indicator").text("\u26d4")
        showNotification("danger", data);
    })
}

function initSidebarButtons() {

    $('.save-action').on("click", function () {
        $("#save_action").val($(this).data("action"));
        saveTemplate();
    });

    $('#preview_button').on("click", function(e){
        e.preventDefault();
        preview_id = $('#preview_id').val();
        if (preview_id) {
            preview_id = "/"+preview_id;
        }            
        window.open('preview'+preview_id);
    })

}

function initEditor(){
    $("#template_text").data("dirty",false);
    $("#template_text").on("change", function(){
        $("#template_text").data("dirty",true);
    })
    window.addEventListener('beforeunload', function (e) {
        if ($("#template_text").data("dirty")) {
            e.preventDefault();
            e.returnValue = '';
        }
    });    
}

$(document).ready(function () {
    initEditor();
    resizeEditor();
    initSidebarButtons();
    $(window).on("resize", resizeEditor);
})