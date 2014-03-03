var map;

var peruskartta = L.tileLayer.wms('http://tiles.kartat.kapsi.fi/peruskartta', {
        layers: 'peruskartta',
        format: 'image/png',
        attribution: 'MML',
        continuousWorld: true
});

var timeInterval = '1925-07-20T00:00:00.000Z/1925-07-30T00:00:00.000Z';
var mil = L.tileLayer.wms('http://localhost:8080/geoserver/pomelo/wms',
		{layers: 'pomelo:mil_mosaic',
    format: 'image/png',
    continuousWorld: true,
    transparent: true,
    time: timeInterval,
    attribution: 'SA'});   

var jcarousel = $('.jcarousel');

function aftermove(e){
	var bounds = map.getBounds();
	var sw = crs.project(bounds.getSouthWest());
	var ne = crs.project(bounds.getNorthEast());
	$.getJSON(kuvaUrl+"?bbox="+sw.x+","+sw.y+","+ne.x+","+ne.y, function (data) {
		geojsonLayer.addData(data);
		jcarousel
			.html(
				$("<div>")
					.addClass("loading")
					.text("Ladataan kartalla olevia kuvia...")
				);
		$('#kuvaInfo').empty();
		var ul = $( "<ul>" );
		$.each( data.features, function() {
			var kuva = this.properties.thumbnail;
			var clickHandler = onclikKuva(this.properties.id);
			var li = $( "<li>" )
				.html($( "<img>" )
				        .attr( "src",  kuva)
				        .click(clickHandler)
				        )
				.appendTo(ul);
	      });
		jcarousel.html(ul);
	    jcarousel.jcarousel('reload');
	});
};

function onclikKuva(kuvaId){
	var kuvaId = kuvaId;
	return function(){
		$('#kuvaInfo').html("Ladataan kuvan tietoja ...");
		$('#kuvaInfo').load('/kuvat/kuva/'+kuvaId);
	}
};

var emptyGeoJson = {
	"type": "FeatureCollection",
	 "crs": {
    	"type": "name",
    	"properties": {
        	"name": "urn:ogc:def:crs:EPSG::3067"
      	}
    },
    "features": [{"type":"Feature"}]
    };
	  
var geojsonLayer = L.Proj.geoJson(emptyGeoJson, {
	attribution: 'kuvalaueet',
	  'pointToLayer': function(feature, latlng) {
		  var marker = L.marker(latlng);
		  return marker
	  }
});

$(function() {
	map = new L.Map('map', {
	    crs: etrstm35,
	    continuousWorld: true,
	    worldCopyJump: false,
	    layers: [peruskartta, mil]
	});
	map.on('load', aftermove);
	map.on('move', aftermove);

	L.control.layers({'peruskartta': peruskartta}, {'mil':mil}).addTo(map);
	map.setView([60.1476, 25.0364], 11);
	
	geojsonLayer.addTo(map);
});


