// ---- WebSocket ---- //
var ws;

function init_ws() {
	uninit_ws();
	ws = new WebSocket("ws://localhost:8005/");
	ws.onopen = function() { console.log("ws opened."); }
	ws.onclose = function() { console.log("ws closed."); }
	ws.onmessage = function(e) { console.log("message: " + e.data); }
}

function uninit_ws() {
	if (typeof ws === undefined && ws instanceof WebSocket)
		ws.close();
}

// ---- Draw ---- //
var isPainting;

function addClick(x, y, dragging) {
	clickX.push(x);
	clickY.push(y);
	clickDrag.push(dragging);
}

canvas.onmousedown = function(event){
	var mouseX = event.pageX - this.offsetLeft;
	var mouseY = event.pageY - this.offsetTop;

	isPainting = true;
	addClick(event.pageX - this.offsetLeft, event.pageY - this.offsetTop);
	redraw();
};
canvas.onmousemove = function(event){
	if(isPainting){
		addClick(event.pageX - this.offsetLeft, event.pageY - this.offsetTop, true);
		redraw();
	}
};
canvas.onmouseup = function(event){
	isPainting = false;
	// send the fucking points to the guesser.
	ws.send(JSON.stringify({"x":clickX , "y":clickY, "drag":clickDrag}))
};
canvas.onmouseleave = function(event){
	isPainting = false;
};

// ---- Set word ---- //
function set_word() {
	word = document.getElementById('le_word_tf').value;
	ws.send(word);
	console.log('drawer set word to: ' + word);
	canvas.style.display = 'block';
}
