jQuery(document).ready(function() {
    jQuery("a.boxed").fancybox({
        'speedIn'       :   200, 
        'speedOut'      :   200,
        'width'         :   1517,
        'height'        :   817,          
        'overlayShow'   :   true
    });
    
    jQuery("a.boxed").trigger('click');

});