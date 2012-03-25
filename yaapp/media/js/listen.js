$(document).ready(function() {
	soundManager.url = '/media/js/sm/swf/'; // directory where SM2 .SWFs live
	soundManager.preferFlash = true;
	soundManager.useHTML5Audio = true;
	soundManager.debugMode = true;
	var mySound = undefined;
	var soundConfig = {
	    id: 'yasoundMainPlay',
	    url: g_radio_url,
	    stream: true,
	    onplay: function() {
	    	$('#play i').removeClass('icon-pause');
	    	$('#play i').addClass('icon-stop');
	    },
	    onstop: function() {
	    	$('#play i').removeClass('icon-stop');
	    	$('#play i').addClass('icon-play');
	    }
	}
	soundManager.onready(function(){
	  mySound = soundManager.createSound(soundConfig);
	  mySound.play();
   	  $('#volume-position').css("width", mySound.volume + "%");
	});

	soundManager.ontimeout(function(){
		alert('Error, cannot load stream, please reload page');
	});

	$('#play').click(function() {
	  if (typeof mySound === "undefined") {
		  mySound = soundManager.createSound(soundConfig);
		  mySound.play();
	   	  $('#volume-position').css("width", mySound.volume + "%");
	  } else {
		  mySound.destruct();
		  mySound = undefined;
	  }
	});
	
	$('#inc').click(function() {
		if (typeof mySound === "undefined") {
			return;
		}		
		if (mySound.volume <= 90) {
			$('#volume-position').css("width", mySound.volume+10 + "%");
			mySound.setVolume(mySound.volume+10);
		} else {
			$('#volume-position').css("width", "100%");
			mySound.setVolume(100);
		}	
	})
	$('#dec').click(function() {
		if (typeof mySound === "undefined") {
			return;
		}		
		if (mySound.volume >= 10) {
			$('#volume-position').css("width", mySound.volume-10 + "%");
			mySound.setVolume(mySound.volume-10);
		} else {
			$('#volume-position').css("width", "0%");
			mySound.setVolume(0);
		}
	})

	var getData = function() {
		// get last events
		$.ajax({
			  url: '/api/v1/radio/' + g_radio_id + '/current_song/',
			  dataType: 'json',
			  data: undefined,
			  success: function(data) {
				  if (data) {
					  var name = data.name;
					  var artist = data.artist;
					  var album = data.album;
					  var cover = data.cover;
					  
					  $('#track-name').text(name);
					  $('#track-artist').text(artist);
					  $('#track-album').text(album);
					  
					  if (cover) {
						  $('#track-image').attr("src", cover);
					  } else {
						  $('#track-image').attr("src", '/media/images/default_image.png');
					  }
 					  
				  }
			  }
			});
	}
	
	$(document).everyTime(10*1000, 'event_timer', function (x) {
		if (typeof mySound === "undefined") {
			return;
		}		
		getData();
	});
	getData();
	
	
	var resizeVolumeBar = function(event) {
		if (typeof mySound === "undefined") {
			return;
		}		
		$('body').css('cursor','pointer');
		var $volumeControl = $('#volume-control');
		var position = event.pageX;
		var left = $volumeControl.position().left;
		var width = $volumeControl.width();
		
		var relativePosition = position - left;
		var soundVolume = Math.floor(relativePosition * 100 / width)
		var percentage = soundVolume + "%";
		$('#volume-position').css("width", percentage);

		mySound.setVolume(soundVolume);
	}
	
	var volumeMouseDown = false;
	$('#volume-control').mousedown(function(event) {
		volumeMouseDown = true;
		resizeVolumeBar(event);
	});
	$(document).mouseup(function(event) {
		if (volumeMouseDown) {
			$('body').css('cursor','auto');
			volumeMouseDown = false;
		}
	});
	
	
	$(document).mousemove(function(event) {
		if (!volumeMouseDown) {
			return;
		}
		resizeVolumeBar(event);
	});
	
	$('#player').height($('#radio').height());
});
