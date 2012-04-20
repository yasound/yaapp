jQuery(document).ready(function() {
    var f = jQuery("a.boxed").fancybox({
        'speedIn'       :   200, 
        'speedOut'      :   200,
        'width'         :   1517,
        'height'        :   817,          
        'overlayShow'   :   true
    });
    
    jQuery("a.boxed").trigger('click');

    jQuery(window).resize(function() {
        jQuery.fancybox.resize();
    });
});