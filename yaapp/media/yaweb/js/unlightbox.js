jQuery(document).ready(function() {
    var isIpad = (navigator.userAgent.match(/iPhone/i)) || (navigator.userAgent.match(/iPod/i)) || (navigator.userAgent.match(/iPad/i));

    
    if (top.location != self.location) {
        jQuery('#unlightbox').show();
    } else {
        jQuery('#unlightbox').hide();
        jQuery('a#logo').attr('href', '/');
    }
    
    if (isIpad && top.location != self.location) {
        top.location = self.location
    }
    
    jQuery("#unlightbox a").click(function() {
        top.location = self.location;
    })
    
    
    
});