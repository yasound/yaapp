$(document).ready(function() {
	soundManager.url = '/media/js/sm/swf/'; // directory where SM2 .SWFs live
	soundManager.preferFlash = true;
	soundManager.useHTML5Audio = true;
	soundManager.debugMode = true;
	var mySound = undefined;
	soundManager.onready(function(){
	  mySound = soundManager.createSound({
	    id: 'soundManagerObject1',
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
	  });
	  $('#play').click();
   	  $('#volume-position').css("width", mySound.volume + "%");
	  
	});

	soundManager.ontimeout(function(){
		alert('Error, cannot load stream, please reload page');
	});

	$('#play').click(function() {
	  if (mySound.playState == 1) {
		  mySound.stop();
	  } else {
		  mySound.play();
	  }
	});
	
	$('#inc').click(function() {
		if (mySound.volume <= 90) {
			$('#volume-position').css("width", mySound.volume+10 + "%");
			mySound.setVolume(mySound.volume+10);
		} else {
			$('#volume-position').css("width", "100%");
			mySound.setVolume(100);
		}	
	})
	$('#dec').click(function() {
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
		getData();
	});
	getData();
	
	
	$('#volume-control').click(function(event) {
		var $volumeControl = $('#volume-control');
		var position = event.pageX;
		var left = $volumeControl.position().left;
		var width = $volumeControl.width();
		
		var relativePosition = position - left;
		var soundVolume = Math.floor(relativePosition * 100 / width)
		var percentage = soundVolume + "%";
		$('#volume-position').css("width", percentage);

		mySound.setVolume(soundVolume);
		
	});
});
