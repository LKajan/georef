function readPage(page){
	var pagenum;
	if (typeof page=="number"){
		pagenum = page;
	} else {
		pagenum = $(this).text();
	}
	$.getJSON(imageJsonUrl+"&page="+pagenum, paivitaKuvalista);
}

function paivitaKuvalista(data){
	var ul = $( "#kuvalista" );
	ul.empty();
	$.each( data, function() {
		var thumbnail = $("<div>")
			.addClass("thumbnail");
		
		$("<a>").attr("href", '/georef/kuva/'+this.id)
			.html(
				$("<img>")
				.attr("src", this.thumbnail)
			)
			.appendTo(thumbnail);
		
		$("<h4>")
			.text(this.name)
			.appendTo(thumbnail);
		
		var globe = $("<object>", {
				'type': "image/svg+xml",
				'data': globeUrl,
				'class': 'globe'
				})
				.text("Your browser does not support SVG")
		.appendTo(thumbnail);
		
		
		$("<p>")
			.text("paikannettu: "+ (this.georef ? "Kyllä" : "Ei"))
			.appendTo(thumbnail);
		
		$("<div>").addClass("col-sm-6").addClass("col-md-4")
		.append(thumbnail)
		.appendTo(ul);
	});
}

$(function() {
	$("#pagination span").click(readPage);
	readPage(1);
});