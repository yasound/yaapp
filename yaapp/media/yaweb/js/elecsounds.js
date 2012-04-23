jQuery(document).ready(function() {
    var isIpad = (navigator.userAgent.match(/iPhone/i)) || (navigator.userAgent.match(/iPod/i)) || (navigator.userAgent.match(/iPad/i));

    var f = jQuery("a.boxed").fancybox({
        'speedIn' : 200,
        'speedOut' : 200,
        'width' : 1517,
        'height' : 817,
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