# Flockwave protocol description

## Table of contents

[TOC]

## Synopsis

**Flockwave** is a [JSON][1]-based communication protocol in [CollMot Robotics][4]'s distributed UAV flock system that allows multiple ground control consoles (clients) to monitor and control an airborne flock of UAVs via a central ground station (server).

This document describes the key actors in the system and specifies the communication protocol in detail. The document assumes familiarity with [JSON][1] and standard networking concepts such as TCP streams, the Hypertext Transfer Protocol (HTTP) and WebSockets. Details of the [JSON][1] format can be found in [RFC 4627][2] and [ECMA 404][3].

[1]: http://json.org/
[2]: http://www.ietf.org/rfc/rfc4627.txt
[3]: http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf
[4]: http://www.collmot.com

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119][5].

[5]: http://www.ietf.org/rfc/rfc2119.txt

## Definitions

Flockwave client
:   An application that can be used to monitor the status of the UAV flock on a map and/or send commands to individual UAVs or groups of UAVs. A Flockwave client may be implemented as a standalone desktop application, a web application running in a desktop or mobile browser, a native mobile application (typically on Android or iOS) or even as a command-line application. Flockwave clients talk to a *Flockwave server* that is responsible for relaying commands and status information between the drones in the flock and the clients.

Flockwave server
:   A headless server application that can accept connections from *Flockwave clients* and maintains one or several additional connections to the UAVs and other data sources (for instance, DGPS data providers).

UAV (abbr.)
:   Unmanned aerial vehicle; typically a quad-, hexa- or octocopter that is equipped with the necessary onboard computer, software and communication equipment that enables it to participate in an UAV flock. Even though it is called an *aerial* vehicle, not all UAVs are required to be airborne. (See also: *beacon*).

Beacon
:    A subtype of *UAV* that is not capable of moving on its own but can broadcast its position to other UAVs in the flock.

## General protocol description

The **Flockwave** protocol is concerned with the communication between a *Flockwave server* (hereinafter: server) and one or more *Flockwave clients* (hereinfter: clients). In particular, the communication between the UAVs and the server is outside the scope of this document; we simply assume that the server is receiving regular updates about the position and status of the UAVs, typically via a radio link.

**Flockwave** is a bidirectional, point-to-point protocol between a server and a single client, consisting of [JSON][1] messages. Messages can be divided into the following classes based on their direction and purpose:

* **Requests** are sent from a client to the server. Each request MUST have a unique identifier. The server MUST send an appropriate *response* to each request, and the original identifier of the request will be included in the response so the client can correlate the responses of the server to the original requests that were sent. Request identifiers MAY be recycled, but the client MUST NOT re-use a request identifier for which the server has not sent an appropriate response yet.

* **Responses** are sent from the server to a client in response to an earlier request. Responses MUST have a unique identifier as well. Even though response IDs are not used in further messages, the IDs can be used by clients to filter duplicate messages if the transport layer does not ensure that each message is delivered exactly once. As stated above, the identifier of the original request MUST also be included in the response.

*  **Notifications** are sent from the server to a client to inform the client about a state change in the server that might be of potential interest to the client. Notifications MUST also have a unique identifier to allow clients to filter duplicate notifications. Responses MUST NOT refer to the identifiers of notifications, and in general the server SHOULD NOT expect a response to a notification.

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
:    The body of the message. When the body is present, the message MUST NOT contain an ``error`` part.

error (object, optional)
:    The error condition conveyed in the message. When the error is present, the message MUST NOT contain a ``body`` part.
:    Errors consist of an error code and a human-readable error message. At least one of the error code or the error message must be present.

Message objects MAY contain other top-level keys to convey additional metadata. Top-level keys starting with ``$`` are reserved for future extensions of this protocol.

All messages in the Flockwave protocol MUST use the same envelope format as described above. The only parts of a message that vary for different message types are the `body` and `error` objects. By convention, the `body` object always contains a string property named `type` that describes the type of the message. Message types are similar to the ones used in the [uBlox protocol][6]: they consist of a major and a minor subtype, both of which are short uppercase strings consisting of 2-8 characters. For instance, a message that queries the Flockwave server for its version number (``SYS-VER``) looks like this[^1]:

```js
{
    "$fw.version": "1.0",
    "id": "03a5ca70-9e69-11e5-8994-feff819cdc9f",
    "body": {
        "type": "SYS-VER"
    }
}
```

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

[^1]: More complex messages usually contain additional properties besides `type` in the body of the message.

[6]: https://www.u-blox.com/sites/default/files/products/documents/u-blox6_ReceiverDescrProtSpec_%28GPS.G6-SW-10018%29_Public.pdf

## Known message types

This section is an exhaustive reference of all the message types supported by the Flockwave protocol. The examples provided in this section contain the message body only; each body object must be wrapped by an appropriate [message envelope](#the-envelope-of-a-message).

### `ACK` --- Acknowledgment messages

The messages in this section are always used as responses; no request is ever sent with these message types.

#### `ACK-ACK` --- Positive acknowledgment

Sent by the server to the client in response to requests that have been executed successfully and where it is not necessary for the response to convey any more detailed information.

**Response fields**
This response has no fields.

**Example response**
```js
{
    "type": "ACK-ACK"
}
```

#### `ACK-NAK` --- Negative acknowledgment

Sent by the server to the client in response to requests that the server has either attempted to execute but failed to do so, or to requests that have been rejected outright by the server.

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``reason`` | no | string | Human-readable description of the reason for the negative acknowledgment.

**Example response**
```js
{
    "type": "ACK-NAK",
    "reason": "I'm sorry, Dave, I'm afraid I can't do that."
}
```

### `CLK` --- Clock and timer-related messages

Flockwave servers may manage a set of clocks (timers); these timers may be displayed on the user interface in a Flockwave client or may be broadcast to UAVs in the range of the Flockwave server for synchronization purposes.

The clocks are assumed to count the number of *clock ticks* that have elapsed since a specified or an unknown *epoch* in the past. Each clock is able to report how many clock ticks correspond to a second in "wall clock time". When the epoch of a clock is known, the epoch, the number of ticks per second and the number of ticks since the epoch can be used to map the state of the clock into wall clock time. Clocks with unknown epochs can only be mapped into the number of seconds that have elapsed since the epoch by multiplying the tick count with the number of ticks per second.

Clocks are identified by unique string identifiers (just like UAVs or connections). The following reserved clock IDs are defined in the Flockwave protocol:

* `system` corresponds to the internal clock of the server. It MUST be measured in seconds since the Unix epoch (one tick per second) and it must be expressed in UTC even if the operating system of the server is set up to display the internal clock in a different timezone.
* `gps` corresponds to time as reported by a GPS receiver. It MUST be measured in seconds since the Unix epoch. Note that this is true irrespectively of the fact that GPS time is different from UTC time (because GPS time is not perturbed by leap seconds), so if you have the number of seconds from the GPS epoch as reported by a GPS receiver, you must correct it not only by the difference between the GPS epoch (6 Jan 1980) and the Unix epoch (1 Jan 1970) but also by the number of leap seconds since the GPS epoch. Typically, GPS receivers also report the exact difference between GPS and UTC time so this should not be a problem.
* `mtc` corresponds to a clock that expresses MIDI time code in a given framerate (typically 24, 25 or 30 frames per second). In most cases it has no known epoch (although it may have one) and it is typically used to synchronize the movement and lighting of drones in a drone show with an external time source.

Any other clock ID not listed explicitly above is free to be used for any purpose.

#### `CLK-INF` --- Retrieve status of a timer

A client sends this request to the server to retrieve the status of one or more clocks or timers managed by the server.

This message may also be broadcast as a notification by the server on its own volition to all connected Flockwave clients to notify them about a status change of one of the clocks. This may happen if a clock is started or stopped or if the value of the clock has drifted or has been adjusted significantly.

**Request fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``ids`` | yes | list of strings | The list of clock IDs that the client is interested in

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``status`` | no | object | Object mapping clock IDs to the corresponding status information. The structure of this object is described by the [`ClockInfo`](#clockinfo) complex type.
``failure`` | no | list of strings | List containing the clock IDs for which the status information could not have been retrieved.
``reasons`` | no | object | Object mapping clock IDs to reasons why the corresponding status information could not have been retrieved.

All the clock IDs that were specified in the request MUST appear *either* as keys in the ``status`` object or in the ``failure`` list.

**Example request**
```js
{
    "type": "CLK-INF",
    "ids": [
        "gps", "mtc", "beer_can"
    ]
}
```

**Example response**
```js
{
    "type": "CLK-INF",
    "status": {
        "gps": {
            "id": "gps",
            "timestamp": 1462891061.824093,
            "retrievedAt": "2016-05-10T14:33:21Z",
            "epoch": "unix",
            "running": true
        },
        "mtc": {
            "id": "mtc",
            "timestamp": 4221,
            "retrievedAt": "2016-05-10T14:33:21Z",
            "ticksPerSecond": 30,
            "running": true
        }
    },
    "failure": ["beer_can"],
    "reasons": {
        "beer_can": "Sorry, no alcoholic beverages are allowed on the premises."
    }
}
```

#### `CLK-LIST` --- List of all the clocks and timers managed by the server

A client sends this request to the server to obtain the list of all the clocks and timers currently managed by the server.

**Request fields**
This request has no fields.

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``ids`` | yes | list of strings | The list of clock IDs for all the clocks that the server manages
 
**Example request**
```js
{
    "type": "CLK-LIST"
}
```

**Example response**
```js
{
    "type": "CLK-LIST",
    "ids": ["gps", "system", "mtc"]
}
```

### `CMD` --- Direct command execution on UAVs

#### `CMD-INF` --- Retrieve execution status of a command

A client sends this request to the server to retrieve the execution status of one or more command requests dispatched earlier.

The execution of a command has the following stages:

* First, the command is *sent* by the server to the UAV.
* Next, the receipt of the command MAY be *acknowledged* by the UAV.
* After an optional acknowledgment, the UAV starts the actual execution of the command.
* During the execution, the UAV MAY post *progress updates* to the server.
* Finally, the execution of the command is *finished* on the UAV and the response is sent back to the server.

The time when the request is sent to the UAV is stored by the server and returned in the execution status record. The time when the server receives an acknowledgment is also recorded, as well as the time when the last progress update was received. Finally, when the command finishes execution, the date when the execution was finished is also recorded by the server.

**Request fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``ids`` | yes | list of strings | The list of receipts for the command execution requests that the client is interested in

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``status`` | no | object | Object mapping receipts to the corresponding status information. The structure of this object is described by the [`CommandExecutionStatus`](#commandexecutionstatus) complex type.
``failure`` | no | list of strings | List containing the connection IDs for which the status information could not have been retrieved.
``reasons`` | no | object | Object mapping connection IDs to reasons why the corresponding status information could not have been retrieved.

All the receipts that were specified in the request MUST appear *either* as keys in the ``status`` object or in the ``failure`` list.

**Example request**
```js
{
    "type": "CMD-INF",
    "ids": [
        "0badcafe-deadbeef:1",
        "0badcafe-deadbeef:3"
    ]
}
```

**Example response**
```js
{
    "type": "CMD-INF",
    "status": {
        "0badcafe-deadbeef:1": {
            "sent": "2016-04-03T08:07:22.000Z",
            "acknowledged": "2016-04-03T08:07:22.471Z",
            "updated": "2016-04-03T08:07:23.811Z",
            "progress": 0.8,
        }
    },
    "failure": ["0badcafe-deadbeef:3"],
    "reasons": {
        "0badcafe-deadbeef:3": "No such receipt"
    }
}
```

#### `CMD-REQ` --- Send a command execution request to a UAV

A client sends this request to the server to ask the server to forward a command to one or more UAVs. The interpretation of the command string depends entirely on the UAV; for instance, a UAV running our `flockctrl` software will accept `flockctrl` console commands and respond appropriately. The server merely acts as a forwarder between the client and the UAV.

Depending on the protocol that the targeted UAV speaks, it may accept a raw command string only, or a command string with positional and/or keyword arguments. Positional arguments are passed as a single array. Keyword arguments are passed as a JSON object that maps the names of the arguments to their values. It is the responsibility of the caller to ensure that the command and its arguments use the appropriate syntax.

Sending and executing a command typically takes some time (especially because there is usually a slower radio link involved between the ground station and the UAV). To keep things running smoothly, the server will not wait for the responses of the UAVs to arrive - it will respond with a `UAV-CMD` response packet as soon as it has attempted to send the command to all the UAVs. The response packet will list the IDs of the UAVs for which the transmission failed, as well as a mapping that maps the IDs of the UAVs for which the command was sent successfully to unique *receipts* that can be used by the client to retrieve the progress of execution for these commands using a [CMD-INF](#cmd-inf-retrieve-execution-status-of-a-command) command. The actual response of a command request (sent by a targeted UAV) will be relayed back to the client that initiated the command in a [CMD-RESP](#cmd-resp-response-to-a-command-request) notification.

**Request fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``ids`` | yes | list of strings | The list of UAV IDs that the command should be sent to
``command`` | yes | string | The command to send to the UAVs
``args`` | no | array | The positional arguments of the command
``kwds`` | no | object | The keyword arguments of the command

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``receipts`` | no | object  | Object that maps the UAV IDs for which the command was sent successfully to the corresponding receipts that can be used to track the progress of execution of the command until the actual response is received. Each receipt is a string; its format is unspecified and it is the responsibility of the server to ensure its uniqueness.
``failure`` | no | list of strings | List containing the UAV IDs for which the status information could not have been retrieved.
``reasons`` | no | object | Object mapping UAV IDs to reasons why the corresponding status information could not have been retrieved.

All the connection IDs that were specified in the request MUST appear *either* in the ``receipts`` mapping as keys or in the ``failure`` list.

**Example request**
```js
{
    "type": "CMD-REQ",
    "ids": ["1", "17", "31", "spam"],
    "command": "algo"
}
```

**Example response**
```js
{
    "type": "CMD-REQ",
    "receipts": {
        "1": "0badcafe-deadbeef:1",
        "17": "0badcafe-deadbeef:2"
    },
    "failure": ["31", "spam"],
    "reasons": {
        "31": "Command execution not supported.",
        "spam": "No such UAV."
    }
}
```

#### `CMD-RESP` --- Response to a command request

A server sends a notification of this type to a client when an earlier command execution request sent by the client has been completed by one of the UAVs the request was targeted to.

**Notification fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``id`` | yes | string | The receipt identifier that tells the client which response sent which UAV is being relayed in this notification.
``response`` | yes | string | The response sent by the UAV.

**Example notification**
```js
{
    "type": "CMD-RESP",
    "id": "0badcafe-deadbeef:1",
    "response": "Hello there!"
}
```

#### `CMD-TIMEOUT` --- Command request timeout notification

A server sends a notification of this type to a client when an earlier command execution request sent by the client has timed out (i.e. the UAV the command was targeted to failed to return a response in time).

**Notification fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``ids`` | yes | list of strings | The list of receipts for the command execution requests that have timed out

**Example notification**
```js
{
    "type": "CMD-TIMEOUT",
    "ids": ["0badcafe-deadbeef:1", "0badcafe-deadbeef:2"]
}
```

### `CONN` --- Connection-related messages

#### `CONN-INF` --- Basic status information of one or more connections

A client sends this request to the server to obtain basic status information about one or more connections (e.g., radio links, DGPS streams) currently managed by the server.

This message may also be broadcast as a notification by the server on its own volition to all connected Flockwave clients to notify them about a status change of one of the managed connections.

**Request fields**
Name | Required? | Type | Description
---- | --------- | ---- | -----------
``ids`` | yes | list of strings | The list of connection IDs that the client is interested in

**Response and notification fields**
Name | Required? | Type | Description
---- | --------- | ---- | -----------
``status`` | no | object | Object mapping connection IDs to the corresponding status information. The structure of this object is described by the [`ConnectionInfo`](#connectioninfo) complex type.
``failure`` | no | list of strings | List containing the connection IDs for which the status information could not have been retrieved.
``reasons`` | no | object | Object mapping connection IDs to reasons why the corresponding status information could not have been retrieved.

All the connection IDs that were specified in the request MUST appear *either* in the ``status`` list or in the ``failure`` list. When this message is sent as a notification, only the ``status`` field SHOULD be present.

**Example request**
```js
{
    "type": "CONN-INF",
    "ids": ["xbee", "dgps", "beer_can"]
}
```

**Example response**
```js
{
    "type": "CONN-INF",
    "status": {
        "xbee": {
            "id": "xbee",
            "purpose": "uavRadioLink",
            "description": "Upstream XBee radio link",
            "status": "connected",
            "timestamp": "2015-12-14T17:31:18.000Z"
        },
        "dgps": {
            "id": "dgps",
            "purpose": "dgpsStream",
            "description": "DGPS data from BUTE0",
            "status": "connecting"
        }
    },
    "failure": ["beer_can"],
    "reasons": {
        "beer_can": "Sorry, no alcoholic beverages are allowed on the premises."
    }
}
```

#### `CONN-LIST` --- List of all the connections managed by the server

A client sends this request to the server to obtain the list of all the connections (e.g., radio links, DGPS streams) currently managed by the server. The list of connections will *not* include connections to Flockwave clients.

**Request fields**
This request has no fields.

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``ids`` | yes | list of strings | The list of connection IDs for all the connections that the server manages
 
**Example request**
```js
{
    "type": "CONN-LIST"
}
```

**Example response**
```js
{
    "type": "CONN-LIST",
    "ids": ["dgps", "xbee"]
}
```

### `SYS` --- System information

#### `SYS-PING` --- Check whether a connection is alive

Either party in the connection may send a `SYS-PING` message to the other party to test whether the connection is still alive. Parties receiving a `SYS-PING` message are expected to respond with an [`ACK-ACK`](#ack-ack-positive-acknowledgment) message as soon as it is practical to do so.

Note that each party may decide whether it wants to send `SYS-PING` messages over the wire periodically. Typically, the message is used to implement "heartbeating" to detect broken connections. If the transport protocol used to convey Flockwave messages implements heartbeating on its own, there is no additional benefit to firing `SYS-PING` messages. However, when Flockwave messages are transmitted over a plain TCP connection, `SYS-PING` messages may be used by either side to detect when the connection was dropped.

**Request fields**
This request has no fields.

**Response fields**
Responses should not be sent with this type; use [`ACK-ACK`](#ack-ack-positive-acknowledgment) instead.

**Example request**
```js
{
    "type": "SYS-PING"
}
```

#### `SYS-VER` --- Version number of the server

A `SYS-VER` request retrieves the version number of the server.

**Request fields**
This request has no fields.

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``name`` | no | string | The name of the server. May be used to distinguish between multiple servers running concurrently so the operators know that they are connecting to the right server from the client.
``revision`` | no | string | The revision number of the server, if known. This field is optional and can be used to convey more detailed version information than what the `version` field allows; for instance, one could provide the Git hash of the last commit in the server's repository.
``software`` | yes | string | The name of the server implementation.
``version`` | yes | string | The version number of the server, in major.minor.patch format. The patch level is optional and may be omitted.

**Example request**
```js
{
    "type": "SYS-VER"
}
```

**Example response**
```js
{
    "type": "SYS-VER",
    "name": "CollMot test server",
    "software": "flockwave-server",
    "version": "1.0",
    "revision": "1.0+git:e2a0dc5"
}
```

### `UAV` --- UAV-related messages

#### `UAV-INF` --- Basic status information of one or more UAVs

A client sends this request to the server to obtain basic status information about one or more UAVs currently known to the server.

This message may also be broadcast as a notification by the server on its own volition to all connected Flockwave clients to notify them about a status change of one of the UAVs.

**Request fields**
Name | Required? | Type | Description
---- | --------- | ---- | -----------
``ids`` | yes | list of strings | The list of UAV IDs that the client is interested in

**Response and notification fields**
Name | Required? | Type | Description
---- | --------- | ---- | -----------
``status`` | no | object | Object mapping UAV IDs to the corresponding status information. The structure of this object is described by the [`UAVStatusInfo`](#uavstatusinfo) complex type.
``failure`` | no | list of strings | List containing the UAV IDs for which the status information could not have been retrieved.
``reasons`` | no | object | Object mapping UAV IDs to reasons why the corresponding status information could not have been retrieved.

All the UAV IDs that were specified in the request MUST appear *either* in the ``status`` list or in the ``failure`` list. When this message is sent as a notification, only the ``status`` field SHOULD be present.

**Example request**
```js
{
    "type": "UAV-INF",
    "ids": ["1", "spam"]
}
```

**Example response**
```js
{
    "type": "UAV-INF",
    "status": {
        "1": { TODO }
    },
    "failure": ["spam"],
    "reasons": {
        "spam": "No such UAV."
    }
}
```

#### `UAV-HALT` --- Initiate immediate shutdown

A client send this request to the server to initiate an immediate shutdown of an UAV in case of an emergency. Note that the UAV will *not* attempt to land - typically it will stop the rotors even in mid-air. Use this message only in emergencies.

The server responds with two lists: the first list contains the IDs of the UAVs where a shutdown attempt was *started* (in the sense that the UAV has been notified that they should land now), and the second list contains the IDs where such an attempt was not started. (Possible reasons for failure could be: invalid UAV ID, UAV does not support forced shutdown and so on). The server MAY decide to include more detailed information about failed attempts in the response.

Clients interested in whether the shutdown attempts have succeeded should keep an eye on [`UAV-INF`](#uav-inf-basic-status-information) messages and watch the status flags of the UAVs.

**Request fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``ids`` | yes | list of strings | The list of UAV IDs to target with this message

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``success`` | no | list of strings | The list of UAV IDs to which the request was sent
``failure`` | no | list of strings | The list of UAV IDs to which the request was *not* sent
``reasons`` | no | object | Object mapping UAV IDs to explanations about why the request failed for these UAVs.

All the UAV IDs that were specified in the request MUST appear *either* in the ``success`` list or in the ``failure`` list.

**Example request**
```js
{
    "type": "UAV-HALT",
    "ids": ["1", "17", "31", "spam"]
}
```

**Example response**
```js
{
    "type": "UAV-HALT",
    "success": ["1", "17"],
    "failure": ["31", "spam"],
    "reasons": {
        "31": "UAV does not support forced shutdown.",
        "spam": "No such UAV."
    }
}
```

#### `UAV-LAND` --- Initiate unsupervised landing

A client send this request to the server to initiate unsupervised landing on one or more UAVs. The server responds with two lists: the first list contains the IDs of the UAVs where an unsupervised landing attempt was *started* (in the sense that the UAV has been notified that they should land now), and the second list contains the IDs where such an attempt was not started. (Possible reasons for failure could be: invalid UAV ID, UAV does not support unsupervised landing and so on). The server MAY decide to include more detailed information about failed attempts in the response.

Clients interested in whether the landing attempts have succeeded should keep an eye on [`UAV-INF`](#uav-inf-basic-status-information) messages and watch the status flags of the UAVs.

**Request fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``ids`` | yes | list of strings | The list of UAV IDs to target with this message

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``success`` | no | list of strings | The list of UAV IDs to which the request was sent
``failure`` | no | list of strings | The list of UAV IDs to which the request was *not* sent
``reasons`` | no | object | Object mapping UAV IDs to explanations about why the request failed for these UAVs.
 
**Example request**
```js
{
    "type": "UAV-LAND",
    "ids": ["1", "17", "31", "spam"]
}
```

**Example response**
```js
{
    "type": "UAV-LAND",
    "success": ["1", "17"],
    "failure": ["31", "spam"],
    "reasons": {
        "31": "UAV is a beacon.",
        "spam": "No such UAV."
    }
}
```

#### `UAV-LIST` --- List of all the UAVs known by the server

A client sends this request to the server to request the list of all UAVs currently known by the server. The semantics of "knowing" a UAV is left up to the server implementation and configuration; typically, the server will return an UAV ID in the response if it has received a status message from the given UAV recently, typically in the last few minutes.

**Request fields**
This request has no fields.

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``ids`` | yes | list of strings | The list of UAV IDs that the server knows
 
**Example request**
```js
{
    "type": "UAV-LIST"
}
```

**Example response**
```js
{
    "type": "UAV-LIST",
    "ids": ["1", "17", "31"]
}
```

#### `UAV-RTH` --- Initiate return to home position

A client send this request to the server to request some of the UAVs to return to their home positions.

The server responds with two lists: the first list contains the IDs of the UAVs where an unsupervised landing attempt was *started* (in the sense that the UAV has been notified that they should return to their home positions now), and the second list contains the IDs where such an attempt was not started. (Possible reasons for failure could be: invalid UAV ID, UAV does not know the concept of a home position and so on). The server MAY decide to include more detailed information about failed attempts in the response.

Clients interested in whether the targeted UAVs have returned to their home positions should keep an eye on [`UAV-INF`](#uav-inf-basic-status-information) messages and watch the GPS coordiates of the UAVs.

**Request fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``ids`` | yes | list of strings | The list of UAV IDs to target with this message

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``success`` | no | list of strings | The list of UAV IDs to which the request was sent
``failure`` | no | list of strings | The list of UAV IDs to which the request was *not* sent
``reasons`` | no | object | Object mapping UAV IDs to explanations about why the request failed for these UAVs.
 
**Example request**
```js
{
    "type": "UAV-RTH",
    "ids": ["1", "17", "31", "spam"]
}
```

**Example response**
```js
{
    "type": "UAV-RTH",
    "success": ["1", "17"],
    "failure": ["31", "spam"],
    "reasons": {
        "31": "UAV is a beacon.",
        "spam": "No such UAV."
    }
}
```

#### `UAV-TAKEOFF` --- Initiate unsupervised take-off

A client send this request to the server to initiate unsupervised take-off on one or more UAVs. The server responds with two lists: the first list contains the IDs of the UAVs where an unsupervised take-off was *started* (in the sense that the UAV has been notified that they should take off now), and the second list contains the IDs where such an attempt was not started. (Possible reasons for failure could be: invalid UAV ID, UAV does not support unsupervised take-off and so on). The server MAY decide to include more detailed information about failed attempts in the response.

Clients interested in whether the take-off attempts have succeeded should keep an eye on [`UAV-INF`](#uav-inf-basic-status-information) messages and watch the status flags of the UAVs.

**Request fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``ids`` | yes | list of strings | The list of UAV IDs to target with this message

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``success`` | no | list of strings | The list of UAV IDs to which the request was sent
``failure`` | no | list of strings | The list of UAV IDs to which the request was *not* sent
``reasons`` | no | object | Object mapping UAV IDs to explanations about why the request failed for these UAVs.
 
**Example request**
```js
{
    "type": "UAV-TAKEOFF",
    "ids": ["1", "17", "31", "spam"]
}
```

**Example response**
```js
{
    "type": "UAV-TAKEOFF",
    "success": ["1", "17"],
    "failure": ["31", "spam"],
    "reasons": {
        "31": "UAV is a beacon.",
        "spam": "No such UAV."
    }
}
```

## Data types used in messages

This section describes the complex data types and structures that are used in Flockwave messages. These data types were referenced from the [Known message types](#known-message-types) section above.

### Dates and times

![The preferred date and time format of Flockwave](http://imgs.xkcd.com/comics/iso_8601.png)

Dates, times and durations MUST always be expressed in UTC using an appropriate [ISO 8601][7] format (see also [RFC 3339][8], especially section 5.6 if you don't like paywalls). Unless stated otherwise, the following formats should be used:

* Dates should be expressed as *YYYY*-*MM*-*DD* (ISO 8601 extended format).
* Times should be expressed as *HH*:*mm*:*ss*.*sss* (ISO 8601 extended format). The millisecond part may be omitted if not relevant.
* Dates and times should be expressed as the date, followed by a literal `T`, followed by the time, followed by `Z`, where the `T` is the standard ISO 8601 separator between dates and times, and `Z` is the ISO 8601 marker for UTC (Zulu time).

[7]: http://www.iso.org/iso/home/standards/iso8601.htm
[8]: https://tools.ietf.org/html/rfc3339

### Angles

Angles are always expressed in degrees because radians are for mathematicians. Depending on the context, angles may either be expressed in the half-open interval [0, 360)[^2], or in the half-open interval [-180, 180) or [-90, 90). For instance, latitudes, longitudes, roll and pitch are naturally expressed in an interval centered around zero, while heading and yaw information is typically presented as a non-negative number. When in doubt, look at the formal JSON schema specification for the allowed range of an angle.

[^2]: Even though it is common in aviation to indicate 360 degrees instead of zero degree, we always transmit zero degree instead of 360 degrees in messages because it comes naturally from the way computers handle modulo arithmetics. The user interface may still opt to present zero degree as 360 degrees if the user prefers that.

### Byte arrays

The JSON format does not support the transmission of raw byte arrays directly since the JSON string type is a sequence of Unicode characters and not a sequence of raw bytes. When a raw byte array has to be transmitted in JSON, the typical solution is to send a base64-encoded representation as a string (see [RFC4648](https://tools.ietf.org/html/rfc4648)). This representation is approximately 33% longer than the corresponding raw byte array, but is still much shorter than the representation of the byte array as a JSON array of integers.

### `Altitude`

An `Altitude` object describes the altitude of a UAV relative to a baseline described by an [AltitudeReference](#altitudereference) value.

**Fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
reference | yes | [AltitudeReference](#altitudereference) | the baseline that defines what "zero altitude" means
value | yes | float | the value of the altitude, in meters, relative to the baseline. The altitude axis always points from the ground up.

**Example**

```js
{
    "reference": "msl",
    "value": 20
}
```
(meaning 20 meters above mean sea level)

### `AltitudeReference`

Enumeration type that describes the known reference points of an altitude value. Currently the following values are defined:

`home`
: The altitude value is relative to the home position of the UAV

`msl`
: The altitude value is relative to the mean sea level

### `Attitude`

An `Attitude` object describes the orientation of a UAV using the standard roll, pitch and yaw angles. See the section about [angles](#angles) for more information about how the angles are expressed.

**Fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
roll | yes | [angle](#angles) | the roll angle in degrees, in the range [-90, 90)
pitch | yes | [angle](#angles) | the pitch angle in degrees, in the range [-90, 90)
yaw | yes | [angle](#angles) | the yaw angle in degrees, in the range [0, 360)

**Example**

```js
{
    "roll": 0,
    "pitch": 0,
    "yaw": 90
}
```

### `ClockEpoch`

A `ClockEpoch` object describes the epoch of a clock or timer that the Flockwave server manages. It is either a [datetime](#dates-and-times) string or one of the following string values:

`unix`
: The UNIX epoch, i.e. midnight on 1 Jan 1970 UTC.
  
### `ClockInfo`

A `ClockInfo` object describes the current state of a clock or timer that the Flockwave server manages (e.g., a clock that reports the local time, the GPS time or a MIDI timecode coming from an external MIDI device connected to the server).

**Fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
id | yes | string | the unique identifier of the clock
epoch | no | [ClockEpoch](#clockepoch) | the epoch from which the current timestamp of the clock is to be measured, if that makes sense for the clock. When the epoch is omitted, the clock is assumed to be ticking since an unspecified instant in the past.
retrievedAt | yes | [datetime](#dates-and-times) | the time according to the internal clock server when the state of the clock was retrieved. If the internal clock of the server and the client is synchronized, this can be used by the client to compensate for the time it takes for the server to transmit the clock status message to the client.
running | yes | boolean | whether the clock is running at the moment
ticksPerSecond | no | float | the number of clock ticks per second. Must be larger than zero. When omitted, it is assumed to be equal to 1.
timestamp | yes | float | the current timestamp of the clock, i.e. the number of ticks that have elapsed on the clock

**Example**

```js
{
    "id": "mtc",
    "timestamp": 4221,
    "retrievedAt": "2016-05-10T14:33:21Z",
    "ticksPerSecond": 30,
    "running": true
}
```

### `CommandExecutionStatus`

A `CommandExecutionStatus` object describes the execution status of a command that was relayed from a client to a UAV by the server.

**Fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
sent | yes | [datetime](#dates-and-times) | time when the command request was sent to the UAV
acknowledged | no | [datetime](#dates-and-times) | time when the UAV acknowledged the receipt of the request (explicitly or implicitly, i.e. by sending a status update or a response)
updated | no | [datetime](#dates-and-times) | time when the UAV updated the progress of the request (explicitly or implicitly, i.e. by sending the completed response)
finished | no | [datetime](#dates-and-times) | time when the final response was fully received by the server
progress | no | float | the progress of the execution of the command, expressed as a real value between 0 and 1 (inclusive)

**Example**
```js
{
    "sent": "2016-04-03T08:07:22.000Z",
    "acknowledged": "2016-04-03T08:07:22.471Z",
    "updated": "2016-04-03T08:07:23.811Z",
    "progress": 0.8,
}
```

### `ConnectionInfo`

A `ConnectionInfo` object describes the purpose and current state of a connection that the Flockwave server manages (e.g., a radio link or a DGPS stream).

**Fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
id | yes | string | the unique identifier of the connection
purpose | yes | [ConnectionPurpose](#connectionpurpose) | the purpose of the connection (i.e. what sort of data it provides)
description | no | string | human-readable description of the connection
status | yes | [ConnectionStatus](#connectionstatus) | the current status of the connection
timestamp | no | [datetime](#dates-and-times) | time when the last packet was received from the connection, or if it is not available, the time when the connection changed status the last time

**Example**
```js
{
    "id": "xbee",
    "purpose": "uavRadioLink",
    "description": "Upstream XBee radio link",
    "status": "connected",
    "timestamp": "2015-12-08T08:17:41.000Z"
}
```
 
### `ConnectionPurpose`

Enumeration type that describes the purpose of a connection. Currently the following values are defined:

`debug`
: A connection that is meant for debugging purposes only.

`dgpsStream`
: A connection whose purpose is to receive DGPS correction packets from an external DGPS stream (e.g., an NTRIP data source or a serial link to a DGPS device).

`time`
: A connection whose purpose is to connect to a service or device that provides time-related information. Examples are connections to an NTP server or a MIDI timecode provider.

`uavRadioLink`
: A connection whose purpose is to receive status information from UAVs and send commands to them.

`other`
: A connection whose purpose does not fit into the above categories. It is advised to use a human-readable description for these connections.

### `ConnectionStatus`

Enumeration type that describes the possible states of a connection. A connection may be in exactly one of the following five states at any time:

`disconnected`
: The connection is not alive and no connection attempt is currently in progress.

`connecting`
: The connection is not alive yet, but a connection or reconnection attempt is currently in progress.

`connected`
: The connection is alive.

`disconnecting`
: The connection is not alive any more, but it has not been properly shut down yet.

`unknown`
: The status of the connection is unknown (typically because we have received no status information from the connection yet).

The value of a field of type `ConnectionStatus` is always a string with one of the five values above.
 
### `GPSCoordinate`

This type represents a coordinate given by a GPS in the usual "latitude, longitude, altitude above mean sea level" format using the WGS 84 reference system.

Latitude and longitude should be specified with at least eight digits' precision if possible.

**Fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
lat | yes | float | The latitude, in degrees, in the range [-90,90)
lon | yes | float | The longitude, in degrees, in the range [-180,180)
alt | no | [`Altitude`](#altitude) | The altitude

**Example**

```js
{
    "lat": 51.99765972,
    "lon": -0.74068634,
    "alt": {
        "reference": "msl",
        "value": 93.765
    }
}
```

### `UAVStatusInfo`

TODO

**Fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
id | yes | string | The unique identifier of the UAV
algorithm | no | string | The name of the algorithm that the UAV is running (if applicable).
position | yes | [GPSCoordinate](#gpscoordinate) | The position of the UAV
heading | no | [angle](#angles) | The heading of the UAV, i.e. the direction the UAV is pointing, projected to the local tangent plane, if known. The range of this angle is [0; 360).
attitude | no | [Attitude](#attitude) | The attitude of the UAV.
velocity | no | [VelocityNED](#velocityned) | The velocity of the UAV, expressed in the NED (North, East, Down) coordinate system.
timestamp | yes | [datetime](#dates-and-times) | Time when the last status update was received from the UAV
debug | no | [byte array](#byte-arrays) | Debug information provided by the algorithm running on the UAV (if applicable).

**Example**

```js
{
    "id": "17",
    "algorithm": "flocking",
    "position": {
        "lat": 51.9976597,
        "lon": -0.7406863,
        "alt": {
            "reference": "msl",
            "value": 93.765
        }
    },
    "heading": 90,
    "attitude": {
        "roll": 0,
        "pitch": 0,
        "yaw": 90
    },
    "velocity": {
        "north": 2.0,
        "east": 2.0,
        "down": -1.0
    },
    "timestamp": "2015-12-08T08:17:41.000Z",
    "debug": "MEJBRENBRkU="
}
```

The debug information in the above example is then decoded to `0BADCAFE` using base64.

### `VelocityNED`

This type represents the velocity of an airborne object (typically a UAV) in the NED coordinate system (also called local tangent plane). The default unit for the components is m/s (metres per second). For instance, a UAV moving northeast with ~2.82 m/s (2.82 = sqrt(8)) while ascending with 1 m/s is expressed by a velocity vector where north=2, east=2 and down=-1.

**Fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
north | yes | number | The "north" component of the velocity vector, in m/s
east | yes | number | The "east" component of the velocity vector, in m/s
down | yes | number | The "down" component of the velocity vector, in m/s

**Example**

```js
{
    "north": 2.0,
    "east": 2.0,
    "down": -1.0
}
```


## Transport layer

### Standard TCP streams

### WebSocket + Socket.io

## Security issues

## FAQ
