// ---- WebSocket ---- //
var ws;

function init_ws() {
	uninit_ws();
	ws = new WebSocket("ws://localhost:8005/");
	ws.onopen = function() { console.log("ws opened."); }
	ws.onclose = function() { console.log("ws closed."); }
	ws.onmessage = function(e) {
		// if e.data contains position of points, draw them
		// else it is a text message, display it
		try {
			obj = JSON.parse(e.data);
			clickX = obj["x"];
			clickY = obj["y"];
			clickDrag = obj["drag"];
			redraw();
		} catch (err) {
			console.log("message: " + e.data);
		}
	}
}

function uninit_ws() {
	if (typeof ws === undefined && ws instanceof WebSocket)
		ws.close();
}

// ---- Guess word ---- //
function guess_word() {
	word=document.getElementById('le_word_tf').value;
	ws.send(word);
}
