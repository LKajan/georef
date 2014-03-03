var etrstm35 = new L.Proj.CRS('EPSG:3067',
        '+proj=utm +zone=35 +ellps=GRS80 +units=m +no_defs +towgs84=0,0,0,0,0,0,0',
        {
                resolutions: [
                        8192, 4096, 2048, 1024, 512, 256, 128,
                        64, 32, 16, 8, 4, 2, 1, 0.5
                ],
                origin: [0, 0]
        });

proj4.defs('EPSG:3067', '+proj=utm +zone=35 +ellps=GRS80 +units=m +no_defs +towgs84=0,0,0,0,0,0,0');

L.Projection.Kuva = {
		project: function (latlng) {
			return new L.Point(latlng.lng, latlng.lat);
		},

		unproject: function (point) {
			return new L.LatLng(point.y, point.x);
		},

		bounds: L.bounds([0,0], [32768,32768])
};

L.CRS.EPSG404000 = L.extend({}, L.CRS, {
	code: 'EPSG:404000',
	projection: L.Projection.Kuva,
	transformation: new L.Transformation(1, 0, -1, 0),

	scale: function (zoom) {
		return Math.pow(2, zoom);
	},

	distance: function (latlng1, latlng2) {
		var dx = latlng2.lng - latlng1.lng,
		    dy = latlng2.lat - latlng1.lat;

		return Math.sqrt(dx * dx + dy * dy);
	},

	infinite: true
});