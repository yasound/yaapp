/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.NativeBridge');

Yasound.NativeBridge.Call = function (method, arg) {
    if (method === 'loginCompleted') {
        if (console.loginCompleted) {
            // cocoa call
            console.loginCompleted(arg);
        } else {
            Yasound.NativeBridge.CallUIKit(method, arg);
        }
    }
};


Yasound.NativeBridge.CallUIKit = function(method, arg) {
    // iOS call
    var iframe = document.createElement("IFRAME");
    iframe.setAttribute("src", "js-frame:" + method + ":" + arg);
    document.documentElement.appendChild(iframe);
    iframe.parentNode.removeChild(iframe);
    iframe = null;
};
