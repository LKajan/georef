
function paivitaKuvalista(data){
	var ul = $( "#kuvalista" );
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
		
		$("<p>")
			.text("paikannettu: "+ (this.georef ? "Kyllä" : "Ei"))
			.appendTo(thumbnail);
		
		$("<div>").addClass("col-sm-6").addClass("col-md-4")
		.append(thumbnail)
		.appendTo(ul);
	});
}