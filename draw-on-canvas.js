var clickX = new Array();
var clickY = new Array();
var clickDrag = new Array();

var canvas = document.getElementById("drawing_canvas");
var ctx = canvas.getContext("2d");

function redraw() {
	canvas.width = canvas.width; // Clears the canvas

	ctx.strokeStyle = "#df4b26";
	ctx.lineJoin = "round";
	ctx.lineWidth = 3;

	for(var i=0; i < clickX.length; i++) {
		ctx.beginPath();
		if(clickDrag[i] && i)
			ctx.moveTo(clickX[i-1], clickY[i-1]);
		else
			ctx.moveTo(clickX[i]-1, clickY[i]);

		ctx.lineTo(clickX[i], clickY[i]);
		ctx.closePath();
		ctx.stroke();
	}
}
