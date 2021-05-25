var notificationTimeout;

function showNotification(_, notification) {
    clearTimeout(notificationTimeout);
    n = $("#notifications");
    n.html(notification);
    n.fadeIn(complete = function() { notificationTimeout = setTimeout(clearNotification, 3000); });
}

function clearNotification() {
    n = $("#notifications");
    n.fadeOut(complete = function() { n.html(""); });
}

function resetNotification() {
    n = $("#notifications");
    n.html("");
    n.hide();
}

function showOk(notification) {
    showNotification('',
        '<div class="alert alert-success" role="alert">' + notification + '</div>'
    )
}

function showFail(notification) {
    showNotification('',
        '<div class="alert alert-danger" role="alert">' + notification + '</div>'
    )
}