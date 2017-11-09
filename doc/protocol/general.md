# General protocol description

The **Flockwave** protocol is concerned with the communication between a *Flockwave server* (hereinafter: server) and one or more *Flockwave clients* (hereinafter: clients). In particular, the communication between the UAVs and the server is outside the scope of this document; we simply assume that the server is receiving regular updates about the position and status of the UAVs, typically via a radio link.

**Flockwave** is a bidirectional, point-to-point protocol between a server and a single client, consisting of [JSON][1] messages. Messages can be divided into the following classes based on their direction and purpose:

* **Requests** are sent from a client to the server. Each request MUST have a unique identifier. The server MUST send an appropriate *response* to each request, and the original identifier of the request will be included in the response so the client can correlate the responses of the server to the original requests that were sent. Request identifiers MAY be recycled, but the client MUST NOT re-use a request identifier for which the server has not sent an appropriate response yet.

* **Responses** are sent from the server to a client in response to an earlier request. Responses MUST have a unique identifier as well. Even though response IDs are not used in further messages, the IDs can be used by clients to filter duplicate messages if the transport layer does not ensure that each message is delivered exactly once. As stated above, the identifier of the original request MUST also be included in the response.

*  **Notifications** are sent from the server to a client to inform the client about a state change in the server that might be of potential interest to the client. Notifications MUST also have a unique identifier to allow clients to filter duplicate notifications. Responses MUST NOT refer to the identifiers of notifications, and in general the server SHOULD NOT expect a response to a notification.

[1]: http://json.org/

## The envelope of a message

Each message has a fixed structure that contains the version of the protocol, the identifier of the message (if any) and the payload or error condition of the message in a fixed format. The actual message class (request, response or notification) can be deduced from the presence or absence of a message identifier, a reference to the original request, and the direction of the message (server to client or client to server). The standard structure of a message looks like the following JSON object:

```js
{
    "$fw.version": "1.0",
    "id": "58d5e212-165b-4ca0-909b-c86b9cee0111",
    "correlationId": "03a5ca70-9e69-11e5-8994-feff819cdc9f",
    "body": {
        ...
    },
    "error": {
        "code": 1234,
        "message": "Some error message."
    }
}
```

This is called the *envelope* of a message. The parts of the envelope are as follows:

$fw.version (string, required)
:    The major and minor version number of the Flockwave protocol. Flockwave messages can be recognized by the presence of this field.

id (string, required)
:    The identifier of the message. The above example uses a UUID identifier, but the protocol does not prescribe any particular identifier format.

correlationId (string, optional)
:    The identifier of the original request to which this message responds. The presence of this field indicates that the message is a response; otherwise it is a request or a notification.

body (object, optional)
:    The body of the message. When the body is present, the message MUST NOT contain an `error` part.

error (object, optional)
:    The error condition conveyed in the message. When the error is present, the message MUST NOT contain a `body` part.
:    Errors consist of an error code and a human-readable error message. At least one of the error code or the error message must be present.

Message objects MAY contain other top-level keys to convey additional metadata. Top-level keys starting with `$` are reserved for future extensions of this protocol.

All messages in the Flockwave protocol MUST use the same envelope format as described above. The only parts of a message that vary for different message types are the `body` and `error` objects. By convention, the `body` object always contains a string property named `type` that describes the type of the message. Message types are similar to the ones used in the [uBlox protocol][6]: they consist of a major and a minor subtype, both of which are short uppercase strings consisting of 2-8 characters. For instance, a message that queries the Flockwave server for its version number (`SYS-VER`) looks like this:

```js
{
    "$fw.version": "1.0",
    "id": "03a5ca70-9e69-11e5-8994-feff819cdc9f",
    "body": {
        "type": "SYS-VER"
    }
}
```

More complex messages usually contain additional properties besides `type` in the body of the message.

A typical response from the server to the above message will look like this:

```js
{
    "$fw.version": "1.0",
    "id": "41fc2e92-058b-4fa3-b30f-eec14db8ee39",
    "correlationId": "03a5ca70-9e69-11e5-8994-feff819cdc9f",
    "body": {
        "type": "SYS-VER",
        "name": "CollMot test server",
        "software": "flockctrl-server",
        "version": "4.17"
    }
}
```

For sake of clarity, the message envelope will be omitted in most examples throughout the rest of the document, and only the body of the message will be shown.

[6]: https://www.u-blox.com/sites/default/files/products/documents/u-blox6_ReceiverDescrProtSpec_%28GPS.G6-SW-10018%29_Public.pdf

