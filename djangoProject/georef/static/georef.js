var map;
var imagemap;

var peruskartta;
var ilmakuvat;

var gcpManager = new GcpManager();

function createMap(){
	map = new L.Map('map', {
	    crs: etrstm35,
	    continuousWorld: true,
	    worldCopyJump: false
	});
	map.on('click', gcpManager.addGP);
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
		    attribution: 'SA'}
	).addTo(map);
	
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
	
	imagemap.on('click', gcpManager.addIP);
}


function P(id, type){
	var _this = this;
	this.set = false;
	this.id = id;
	this.type = type;
	if (type == 'ground'){
		this.map = map;
	} else if (type == 'image'){
		this.map = imagemap;
	}
	this.input = $('<input>').attr('type', 'hidden')
	.attr('id', 'id_gcps-'+this.id+'-'+this.type)
    .attr('name', 'gcps-'+this.id+'-'+this.type);
	
	this.marker = L.marker([], {draggable: true, title: id});
	this.marker.on('dragend', function(event){
        var marker = event.target;
        var ll = marker.getLatLng();
        _this.input.val('POINT('+ll.lng+' '+ll.lat+')');
	});
}
P.prototype.fromInput = function(id){
	this.input = $('#id_gcps-'+id+'-'+this.type);
	
	var pointPattern = /(\d+(\.\d+)?) (\d+(\.\d+)?)/;
	var coords = pointPattern.exec(this.input.val());
	this.marker.setLatLng([coords[3], coords[1]]);
	this.marker.addTo(this.map);
	this.set = true;
}
P.prototype.fromClick = function(e){
	this.marker.setLatLng(e.latlng);
	this.marker.addTo(this.map);
	
	var ll = this.marker.getLatLng();
	this.input.val('POINT('+ll.lng+' '+ll.lat+')');
	
	this.set = true;
}

function GCP(id){
	this.id = id;
	
	this.ground = new P(this.id, 'ground');
	this.image = new P(this.id, 'image');
}
GCP.prototype.fromInput = function(id, del){
	this.id_input = id;
	this.del_input = del;
	this.ground.fromInput(this.id);
	this.image.fromInput(this.id);
}

GCP.prototype.addGP = function(e){
	this.ground.fromClick(e);

	if (this.image.set){
		this.write()
	}
}
GCP.prototype.addIP = function(e){
	this.image.fromClick(e);
	if (this.ground.set){
		this.write()
	}
}
GCP.prototype.write = function(){
	this.id_input = $('<input>').attr('type', 'hidden')
	.attr('id', 'id_gcps-'+this.id+'-id')
    .attr('name', 'gcps-'+this.id+'-id');

	this.id_input.insertBefore( "#btnTallenna" );
	this.image.input.insertBefore( "#btnTallenna" );
	this.ground.input.insertBefore( "#btnTallenna" );
}
GCP.prototype.del = function(){
	if (typeof this.del_input !== 'undefined'){
		this.del_input.prop( "checked", true );
	} else {
		this.id_input.remove();
		this.i_input.remove();
		this.g_input.remove();
	}
}

function GcpManager(){
	var _this = this;
	this.addGP = function(e){
		var gcp = _this.getNextEmptyG();
		gcp.addGP(e);
	}
	this.addIP = function(e){
		var gcp = _this.getNextEmptyI();
		gcp.addIP(e);
	}
	
	this.gcps = [];
	
	this.total;
	this.nextG = 0;
	this.nextI = 0;
}
GcpManager.prototype.getGcp = function(i) {
	var gcp = this.gcps[i];
	if (typeof gcp == 'undefined'){
		gcp = new GCP(i);
		this.addGCP(i, gcp);
	}
	return gcp;
}
GcpManager.prototype.getNextEmptyG = function(){
	var gcp = this.getGcp(this.nextG);
	this.nextG++;
	return gcp;
}
GcpManager.prototype.getNextEmptyI = function(){
	var gcp = this.getGcp(this.nextI);
	this.nextI++;
	return gcp;
}


GcpManager.prototype.addGCP = function(i, gcp){
	this.gcps[i] = gcp;
	this.total.val(this.gcps.length);
}

GcpManager.prototype.readGCPs = function(){
	this.total = $('#id_gcps-TOTAL_FORMS');
	var i=0;
	while (true) {
		var id_input = $('#id_gcps-'+i+'-id');
		if (id_input.length == 0){
			break;
		}
		var del_input = $('#id_gcps-'+i+'-DELETE');
		var gcp = new GCP(i);
		gcp.fromInput(id_input, del_input);
		this.nextG++;
		this.nextI++;
		this.addGCP(i, gcp);
		
		i++;
	}
}

function tallenna(){
	if (gps.length < 3){
		alert("Kiintopisteitä oltava vähintään kolme.");
	}
	
	return true;
}

function paivitaTalletettu(){
	console.log("Tallennettu");
}

$(function() {
	createMap();
	createImagemap();

	gcpManager.readGCPs();
	
	$('#btnTallenna').submit(tallenna);
});
