var map;
var imagemap;

var peruskartta;
var ilmakuvat;

var gps = [];
var pps = [];

function createMap(){
	peruskartta = L.tileLayer.wms('http://tiles.kartat.kapsi.fi/peruskartta', {
        layers: 'peruskartta',
        format: 'image/png',
        attribution: 'MML',
        continuousWorld: true
	});
	var timeInterval = '1925-07-20T00:00:00.000Z/1925-07-30T00:00:00.000Z';
	ilmakuvat = L.tileLayer.wms('http://localhost:8080/geoserver/pomelo/wms',
			{layers: 'pomelo:mil_mosaic',
	    format: 'image/png',
	    continuousWorld: true,
	    transparent: true,
	    time: timeInterval,
	    attribution: 'SA'});

	map = new L.Map('map', {
	    crs: etrstm35,
	    continuousWorld: true,
	    worldCopyJump: false,
	    layers: [peruskartta, ilmakuvat]
	});
	//map.on('click', addGP);
	map.setView([60.1476, 25.0364], 11);
	
	L.control.layers({'Peruskartta': peruskartta}, {'Ilmakuvat':ilmakuvat}).addTo(map);
}

function createImagemap(){
	var kuva = L.tileLayer.wms('http://localhost:8080/geoserver/gwc',
			{layers: 'mil:19300527_0950',
	    format: 'image/jpeg',
	    continuousWorld: true,
	    transparent: true,
	    time: timeInterval,
	    attribution: 'SA'});
	
	imagemap = L.map('imagemap', {
		  maxZoom: 15,
		  crs: L.CRS.EPSG404000,
		  continuousWorld: true,
		  worldCopyJump: false,
		  layers: [kuva]
		}).setView([0, 0], 1);
	//imagemap.on('click', addPP);

	var southWest = imagemap.unproject([0, kuvaHeight], imagemap.getMaxZoom());
	var northEast = imagemap.unproject([kuvaWidth, 0], imagemap.getMaxZoom());
	var imagebounds = new L.LatLngBounds(southWest, northEast);
	/*
	imagemap.setMaxBounds(imagebounds);
	*/
	
	#L.imageOverlay(kuvaUrl, imagebounds).addTo(imagemap);
}

function addGP(e){
	var newMarker = new L.marker(e.latlng).addTo(map);
	gps.push(newMarker);
}

function  addPP(e){
	var newMarker = new L.marker(e.latlng).addTo(imagemap);
	pps.push(newMarker);
}

$(function() {
	createMap();
	createImagemap();
	
	
	
});
