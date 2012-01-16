soundManager.url = '/media/js/sm/swf/'; // directory where SM2 .SWFs live
soundManager.onready(function(){
  var mySound = soundManager.createSound({
    id: 'soundManagerObject1',
    url: g_radio_url,
    stream: true
  });
  mySound.play();
});

soundManager.ontimeout(function(){
	alert('Error, cannot load stream, please reload page');
});
