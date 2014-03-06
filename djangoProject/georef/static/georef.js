var map;
var imagemap;

var peruskartta;
var ilmakuvat;

var gps = [];
var pps = [];

function createMap(){
	map = new L.Map('map', {
	    crs: etrstm35,
	    continuousWorld: true,
	    worldCopyJump: false
	});
	map.on('click', addGP);
	map.setView([60.1476, 25.0364], 11);
	
	peruskartta = L.tileLayer.wms('http://tiles.kartat.kapsi.fi/peruskartta', {
        layers: 'peruskartta',
        format: 'image/png',
        attribution: 'MML',
        continuousWorld: true
	}).addTo(map);
	
	var timeInterval = '1925-07-20T00:00:00.000Z/1925-07-30T00:00:00.000Z';
	ilmakuvat = L.tileLayer.wms('http://localhost:8080/geoserver/georef/wms',
			{layers: 'georef:tausta_mosaic',
	    format: 'image/png',
	    continuousWorld: true,
	    transparent: true,
	    time: timeInterval,
	    attribution: 'SA'}).addTo(map);
	
	L.control.layers({'Peruskartta': peruskartta}, {'Ilmakuvat':ilmakuvat}).addTo(map);
}

function createImagemap(){
	imagemap = L.map('imagemap', {
		  crs: L.CRS.EPSG404000,
		  continuousWorld: true,
		  worldCopyJump: false,
		  maxZoom :7
		}).setView([kuvaWidth/2,kuvaHeight/2], 3);
	
	var southWest = imagemap.unproject([0, kuvaWidth], imagemap.getMaxZoom());
	var northEast = imagemap.unproject([kuvaHeight, 0], imagemap.getMaxZoom());
	//imagemap.setMaxBounds(new L.LatLngBounds(southWest, northEast));
	
	var kuva = L.tileLayer.wms('http://localhost:8080/geoserver/gwc/service/wms',
			{layers: 'georef:'+gsName,
	    format: 'image/jpeg',
	    continuousWorld: true,
	    //transparent: true,
	    attribution: 'SA'}).addTo(imagemap);
	
	imagemap.on('click', addPP);
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
