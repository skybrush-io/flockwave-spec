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

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119][1].

[1]: http://www.ietf.org/rfc/rfc2119.txt

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

[1]: http://json.org

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

All messages in the Flockwave protocol MUST use the same envelope format as described above. The only parts of a message that vary for different message types are the `body` and `error` objects. By convention, the `body` object always contains a string property named `type` that describes the type of the message. Message types are similar to the ones used in the [uBlox protocol][1]: they consist of a major and a minor subtype, both of which are short uppercase strings consisting of 2-8 characters. For instance, a message that queries the Flockwave server for its version number (``SYS-VER``) looks like this[^1]:

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

[1]: https://www.u-blox.com/sites/default/files/products/documents/u-blox6_ReceiverDescrProtSpec_%28GPS.G6-SW-10018%29_Public.pdf

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

#### `CONN-LIST` --- List of all the connections maintained by the server

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

#### `SYS-VER` --- Version number of the server

A `SYS-VER` request retrieves the version number of the server.

**Request fields**
This request has no fields.

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``name`` | no | string | The name of the server. May be used to distinguish between multiple servers running concurrently so the operators know that they are connecting to the right server from the client.
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
    "version": "1.0"
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
    "ids": ["1", "17", "31", "spam"]
}
```

**Example response**
```js
{
    "type": "UAV-INF",
    "status": {
        "1": { TODO },
        "17": { TODO },
        "31": { TODO }
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
``success`` | yes | list of strings | The list of UAV IDs to which the request was sent
``failure`` | yes | list of strings | The list of UAV IDs to which the request was *not* sent
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

The server responds with two lists: the first list contains the IDs of the UAVs where an unsupervised landing attempt was *started* (in the sense that the UAV has been notified that they should land now), and the second list contains the IDs where such an attempt was not started. (Possible reasons for failure could be: invalid UAV ID, UAV does not know the concept of a home position and so on). The server MAY decide to include more detailed information about failed attempts in the response.

Clients interested in whether the targeted UAVs have returned to their home positions should keep an eye on [`UAV-INF`](#uav-inf-basic-status-information) messages and watch the GPS coordiates of the UAVs.

**Request fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``ids`` | yes | list of strings | The list of UAV IDs to target with this message

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
``success`` | yes | list of strings | The list of UAV IDs to which the request was sent
``failure`` | yes | list of strings | The list of UAV IDs to which the request was *not* sent
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

## Data types used in messages

This section describes the complex data types and structures that are used in Flockwave messages. These data types were referenced from the [Known message types](#known-message-types) section above.

### Dates and times

![The preferred date and time format of Flockwave](http://imgs.xkcd.com/comics/iso_8601.png")

Dates, times and durations MUST always be expressed in UTC using an appropriate [ISO 8601][1] format (see also [RFC 3339][2] if you don't like paywalls). Unless stated otherwise, the following formats should be used:

* Dates should be expressed as *YYYY*-*MM*-*DD* (ISO 8601 extended format).
* Times should be expressed as *HH*:*mm*:*ss*.*sss* (ISO 8601 extended format). The millisecond part may be omitted if not relevant.
* Dates and times should be expressed as the date, followed by a literal `T`, followed by the time, followed by `Z`, where the `T` is the standard ISO 8601 separator between dates and times, and `Z` is the ISO 8601 marker for UTC (Zulu time).

[1]: http://www.iso.org/iso/home/standards/iso8601.htm
[2]: https://tools.ietf.org/html/rfc3339

### Angles

Angles are always expressed in degrees because radians are for mathematicians.

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
```json
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

`dgpsStream`
: A connection whose purpose is to receive DGPS correction packets from an external DGPS stream (e.g., an NTRIP data source or a serial link to a DGPS device).

`uavRadioLink`
: A connection whose purpose is to receive status information from UAVs and send commands to them.

`other`
: A connection whose purpose does not fit into the above categories. It is advised to use a human-readable description for these connections.

### `ConnectionStatus`

Enumeration type that describes the possible states of a connection. A connection may be in exactly one of the following four states at any time:

`disconnected`
: The connection is not alive and no connection attempt is currently in progress.

`connecting`
: The connection is not alive yet, but a connection or reconnection attempt is currently in progress.

`connected`
: The connection is alive.

`disconnecting`
: The connection is not alive any more, but it has not been properly shut down yet.

The value of a field of type `ConnectionStatus` is always a string with one of the four values above.
 
### `GPSCoordinate`

This type represents a coordinate given by a GPS in the usual "latitude, longitude, altitude above mean sea level" format using the WGS 84 reference system.

Latitude and longitude should be specified with at least eight digits' precision if possible.

**Fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
lat | yes | float | The latitude, in degrees
lon | yes | float | The longitude, in degrees
amsl | no | float | Altitude above mean sea level, if known, in metres. Positive axis points from the ground up.

**Example**

```js
{
    "lat": 51.99765972,
    "lon": -0.74068634,
    "amsl": 93.765
}
```

### `UAVStatusInfo`

TODO

**Example**

```js
{
    "id": "17",
    "algorithm": "flocking",
    "position": {
        "lat": 51.9976597,
        "lon": -0.7406863,
        "amsl": 93.765
    },
    "heading": 90,
    "attitude": {
        "roll": 0,
        "pitch": 0,
        "yaw": 0
    },
    "velocity": {
        "north": 0,
        "east": 0,
        "down": 0
    },
    "timestamp": "2015-12-08T08:17:41.000Z",
    "debug": "0BADCAFE"
}
```

## Transport layer

### Standard TCP streams

### WebSocket + Socket.io

## Security issues

## FAQ


> Written with [StackEdit](https://stackedit.io/).