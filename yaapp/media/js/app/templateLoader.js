window.ich.loadRemoteTemplate = function (path, name, callback, data) {
    if (data) {
        delete window.ich[name];
        delete window.ich.templates[name];
        jQuery.get("/app/tpl/" + path + "/", data, function (data) {
            window.ich.addTemplate(name, data); 
            callback();
        });
        return;
    }

    if (!ich.templates[name]) {
    } else {
        callback();
    }
};