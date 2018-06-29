# Transport layer

## TCP streams

The Flockwave protocol can simply be implemented on top of TCP streams by encoding Flockwave messages in JSON format and separating the messages with newlines. Due to the nature of the JSON encoding, it can be guaranteed that the encoding of a Flockwave message does not contain a newline character (since newlines within JSON strings are escaped as `\n`). Flockwave message receivers can simply read chunks of data from the TCP stream until a newline is encountered, then attempt to parse the chunks up to the last newline character as JSON. Should the parsing fail, the entire chunk can be thrown away and the parsing can resume from the next character after the last newline.

## UDP datagrams

Flockwave messages can also be sent in UDP datagrams; in such cases, we can simply assume that a single UDP datagram conveys a single Flockwave message. Here we neglect the fact that *in theory* a Flockwave message can be larger than the maximum allowed length of a UDP datagram as such messages are unlikely to appear in practice.

Since UDP is a connectionless protocol, handling Flockwave notifications over UDP is a bit problematic: in case of notification broadcasts, the server would not know which UDP host-port combinations should be targeted with a specific message. There are at least two ways to resolve this:

* The server could send Flockwave notifications to a designated UDP broadcast address and port; it is then the responsibility of the Flockwave client to listen to the broadcast address as well as its own address.
* The server could also send Flockwave notifications to all UDP host-port combinations that it has received a message from in the last X seconds. The advantage is that there is no need to listen for a separate broadcast address and port on the client side, but then it is the responsibility of the client to ensure that a keepalive message (e.g., `SYS-PING`) is sent to the server frequently enough such that the connection is not broken even if some of the keepalive messages are lost. A good rule of thumb is to set the connection timeout to 60 seconds and then request clients to send keepalive messages every 10 seconds - this way the connection is broken only if six consecutive keepalive messages are lost.

## WebSocket + Socket.io

The Flockwave protocol can also be implemented on top of a WebSocket connection
augmented with [Socket.io](https://socket.io/). In this scenario, the Flockwave
server provides a lightweight HTTP web server that supports upgrading an HTTP
connection targeting a designated URL and all its subpaths to a WebSocket
connection. The WebSocket connection is then used to send Socket.io frames, and
the actual Flockwave messages are sent to a designated Socket.io namespace
(typically named `fw`). The Socket.io protocol takes care of falling back to
long polling if WebSockets are not supported on the client.

Code example for a Flockwave client implemented in JavaScript:

```js
const io = require('socket.io')
const connection = io.connect('http://flockwave.collmot.com')

connection.on('connect', () => {
  console.log('Connected to server')
})

connection.on('fw', msg => {
  console.log('Received message:', msg)
})
```

