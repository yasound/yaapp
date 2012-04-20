jQuery(document).ready(function() {
    if (top.location != self.location) {
        jQuery('#unlightbox').show();
    } else {
        jQuery('#unlightbox').hide();
    }
    
    jQuery("#unlightbox a").click(function() {
        top.location = self.location;
    })
    
    jQuery("#nicolas").click(function() {
        window.open('https://api.yasound.com/listen/6fa46bfa1f824879b503e2aebbff7411');
    });
    
});