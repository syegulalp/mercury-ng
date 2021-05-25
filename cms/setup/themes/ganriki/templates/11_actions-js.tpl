function hidemenu() {
    /* $("#newarticles").collapse('hide'); */
}

function no_cookie(id) {

    var date = new Date();
    days = 30;
    date.setTime(+ date + (days * 86400000));
    document.cookie = 'no-' + id + '=yes;path=/;expires=' + date.toGMTString();

}

window.onload = function () {

    global = {};
    global.menu = false;

    $("img.lazy").lazyload({
        effect: "fadeIn",
        skip_invisible: false,
        failure_limit: 128
    });

    $(document).delegate('*[data-toggle="lightbox"]', 'click', function (event) {
        event.preventDefault();
        $(this).ekkoLightbox();
    });

    if (document.cookie.indexOf("no-patreon") >= 0) {
        $("#patreon-alert").hide();
    }
    else {
        xx = setTimeout(function () { $("#patreon-alert").fadeIn(); }, 1000);
    }

    if (document.cookie.indexOf("no-comment-alert") >= 0) {
        $("#comment-alert").hide();
    }

    $('.carousel').carousel({
        interval: 5000
    });

    $('.tooltip-social').tooltip({
        selector: "a[data-toggle=tooltip]"
    });

}