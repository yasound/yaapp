jQuery(document).ready(function() {
    var registerInfos = $('#id_registered').parent().parent().parent().next();
    var macInfo = $('#id_mac').parent().parent().next();
    var pcInfo = $('#id_pc').parent().parent().next();
    var iPhoneInfo = $('#id_iphone').parent().parent().next();
    var iPodInfo = $('#id_ipod').parent().parent().next();
    var androidInfo = $('#id_android').parent().parent().next();

    if (!$('#id_registered').attr('checked')) {
        registerInfos.hide();
    }
    
    if (!$('#id_mac').attr('checked')) {
        macInfo.hide();
    }
    if (!$('#id_pc').attr('checked')) {
        pcInfo.hide();
    }
    if (!$('#id_iphone').attr('checked')) {
        iPhoneInfo.hide();
    }
    if (!$('#id_ipod').attr('checked')) {
        iPodInfo.hide();
    }
    if (!$('#id_android').attr('checked')) {
        androidInfo.hide();
    }
    
    
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