jQuery(document).ready(function() {
    var isIpad = (navigator.userAgent.match(/iPhone/i)) || (navigator.userAgent.match(/iPod/i)) || (navigator.userAgent.match(/iPad/i));

    var f = jQuery("a.boxed").fancybox({
        'speedIn' : 200,
        'speedOut' : 200,
        'padding': 0,
        'margin': 0,
        'width' : 728,
        'height' : 300,
        'scrolling': 'no',
        'overlayShow' : true,
        onStart : function() {
            if (isIpad) {
                jQuery('object').hide();
            }
        },
        onClosed : function() {
            if (isIpad) {
                jQuery('object').show();
            }
        }
    });

    jQuery("a.boxed").trigger('click');

    jQuery(window).resize(function() {
        jQuery.fancybox.resize();
    });

    if ((navigator.userAgent.match(/iPhone/i)) || (navigator.userAgent.match(/iPod/i)) || (navigator.userAgent.match(/iPad/i))) {
    }
});