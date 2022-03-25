const WS = require( 'ws' );

const wss = new WS.WebSocketServer({ port: 8001 });

wss.on('connection', function connection(ws) {
  ws.on('message', function message(data) {
    ws.send( data.toString() )
  });
});
