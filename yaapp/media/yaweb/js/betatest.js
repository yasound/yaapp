jQuery(document).ready(function() {
    var registerInfos = $('#id_registered').parent().parent().parent().next().hide();
    var macInfo = $('#id_mac').parent().parent().next().hide();
    var pcInfo = $('#id_pc').parent().parent().next().hide();
    var iPhoneInfo = $('#id_iphone').parent().parent().next().hide();
    var iPodInfo = $('#id_ipod').parent().parent().next().hide();
    var androidInfo = $('#id_android').parent().parent().next().hide();
    
    $('#id_registered').click(function() {
        registerInfos.slideToggle();
    });
    
    $('#id_mac').click(function() {
        macInfo.slideToggle();    
    });
    $('#id_pc').click(function() {
        pcInfo.slideToggle();    
    });
    $('#id_iphone').click(function() {
        iPhoneInfo.slideToggle();    
    });
    $('#id_ipod').click(function() {
        iPodInfo.slideToggle();    
    });
    $('#id_android').click(function() {
        androidInfo.slideToggle();    
    });
});