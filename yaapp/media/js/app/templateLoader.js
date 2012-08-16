window.ich.loadRemoteTemplate = function (path, name, callback) {
    if (!ich.templates[name]) {
        jQuery.get("/app/tpl/" + path + "/", function (data) {
            window.ich.addTemplate(name, data);
            callback();
        });
    } else {
        callback();
    }
};