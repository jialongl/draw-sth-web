As said, this is just an html5+websocket port-over of "Draw Something", for practice and kicks.

Tested on Linux Google Chrome 18.0.1025.142 (129054), which supports (only?)
[hybi-17](http://tools.ietf.org/html/draft-ietf-hybi-thewebsocketprotocol-17), where Sec-WebSocket-Version = 13.

**How to run:**

<code>
$ python ws-server.py<br />
$ google-chrome drawer.html (tab A)<br />
$ google-chrome guesser.html (tab B)
</code>

In tab A: Set the word by typing it and the Enter key; Draw stuff. (But don't draw before you set the answer) <br>
In tab B: You see the drawing coming out in the canvas; Guess the word by typing it and the Enter key.

In the whole process, have "DevTools" open, as I implemented the notifications as "console.log()"s.

This is the simplest form it can go.

**Known "Issues":**

* No defensive programmin applied, for better illustration of concept.
* minimum UI stuff (You must have already noticed -- even notifications are in JS console).
