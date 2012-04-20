jQuery(document).ready(function() {
    if (top.location != self.location) {
        jQuery('#unlightbox').show();
    } else {
        jQuery('#unlightbox').hide();
    }
    
    jQuery("#unlightbox a").click(function() {
        top.location = self.location;
    })
    
});