
/* some small functionality for search */
function initialize() {
	var searchTypes = '',
		markers = [],
		logged = is_logged();
	var mapOptions = {
		center: new google.maps.LatLng(-33.8688, 151.2195),
		zoom: 13,
		disableDefaultUI:true
	};
	var map = new google.maps.Map(document.getElementById('map-canvas'),mapOptions);

	var input = /** @type {HTMLInputElement} */(document.getElementById('pac-input'));

	var types = document.getElementById('type-selector');
	map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);
	map.controls[google.maps.ControlPosition.TOP_LEFT].push(types);

	var autocomplete = new google.maps.places.Autocomplete(input);
	autocomplete.bindTo('bounds', map);

	var infowindow = new google.maps.InfoWindow();
	var marker = new google.maps.Marker({
		map: map,
		anchorPoint: new google.maps.Point(0, -29)
	});

	var place = autocomplete.getPlace();
	google.maps.event.addListener(autocomplete, 'place_changed', function() {
		// infowindow.close();
		// marker.setVisible(false);
		var place = autocomplete.getPlace();
		console.log(place);
		if (!place.geometry) {
		  return;
		}

		// If the place has a geometry, then present it on a map.
		if (place.geometry.viewport) {
		  map.fitBounds(place.geometry.viewport);
		} else {
		  map.setCenter(place.geometry.location);
		  map.setZoom(17);  // Why 17? Because it looks good.
		}

		var request = {
			location: place.geometry.location,
			radius: '500000',
			types: searchTypes
		};
		service = new google.maps.places.PlacesService(map);
		service.search(request,callback);
	});
	function setupClickListener(id, types) {
		var radioButton = document.getElementById(id);
		var places = new Array('entertainment','utilities');
		places['utilities'] = ['gas_station','hospital'];
		places['entertainment'] = ['restaurant','amusement_park','park','rv_park','movie_theater','shopping_mall'];
		places[''] = '';
		google.maps.event.addDomListener(radioButton, 'click', function() {
			clearMarkers();
			deleteMarkers();
			searchTypes = places[types];
			jQuery('#result').empty();
			google.maps.event.trigger(autocomplete, 'place_changed');
		});
	}

	function callback(results, status) {
	  if (status == google.maps.places.PlacesServiceStatus.OK) {
		for (var i = 0; i < results.length; i++) {
			var place = results[i];
			var request = {reference:place.reference}
			service = new google.maps.places.PlacesService(map);
			if(logged === 'Logged!')
				service.getDetails(request, callback_place_logged);
			else
				service.getDetails(request, callback_place);
		}
	  }
	}
	function createMarkerLogged(place) {
		var placeLoc = place.geometry.location;
		var marker = new google.maps.Marker({
			map: map,
			position: place.geometry.location
		});
		google.maps.event.addListener(marker, 'click', function() {
			infowindow.setContent(place.name);
			infowindow.open(map, this);
		});
		markers.push(marker);
		console.log(place);
		var ul_parent = jQuery('#result');
		ul_parent.append('<li><span class="image"><img height="35px" width="35px" src="'+place.icon+'"/></span><span class="title">'+place.name+'</span><span class="adress">'+place.formatted_address+'</span><span class="link"><a href="/view/'+place.reference+'">View full page</a></span></li>');

	}
	function createMarker(place) {
		var placeLoc = place.geometry.location;
		var marker = new google.maps.Marker({
			map: map,
			position: place.geometry.location
		});
		google.maps.event.addListener(marker, 'click', function() {
			infowindow.setContent(place.name);
			infowindow.open(map, this);
		});
		markers.push(marker);
		console.log(place);
		var ul_parent = jQuery('#result');
		ul_parent.append('<li><span class="image"><img height="35px" width="35px" src="'+place.icon+'"/></span><span class="title">'+place.name+'</span><span class="adress">'+place.formatted_address+'</span></li>');

	}

	function callback_place(place, status) {
	  if (status == google.maps.places.PlacesServiceStatus.OK) {
		if(place.website)
			createMarker(place);
	  }
	}
	function callback_place_logged(place, status) {
	  if (status == google.maps.places.PlacesServiceStatus.OK) {
		createMarkerLogged(place);
	  }
	}
	// Sets the map on all markers in the array.
	function setAllMap(map) {
	  for (var i = 0; i < markers.length; i++) {
		markers[i].setMap(map);
	  }
	}

	// Removes the markers from the map, but keeps them in the array.
	function clearMarkers() {
	  setAllMap(null);
	}

	// Shows any markers currently in the array.
	function showMarkers() {
	  setAllMap(map);
	}

	// Deletes all markers in the array by removing references to them.
	function deleteMarkers() {
	  clearMarkers();
	  markers = [];
	}

	setupClickListener('changetype-all', []);
	setupClickListener('changetype-entertainment', 'entertainment');
	setupClickListener('changetype-utilities', 'utilities');
}
function is_logged(){
	var result = '';
	jQuery.ajax({
		url : '/ajax_actions',
		async : false,
		data: {'method':'islogged','id':1},
		success: function(data){
			console.log(data);
			result = data.trim();
		}
	});
	return result;
}
google.maps.event.addDomListener(window, 'load', initialize);