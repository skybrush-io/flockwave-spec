# `UAV` --- UAV-related messages

## `UAV-INF` --- Basic status information of one or more UAVs

A client sends this request to the server to obtain basic status information about one or more UAVs currently known to the server.

This message may also be broadcast as a notification by the server on its own volition to all connected Flockwave clients to notify them about a status change of one of the UAVs.

**Request fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
`ids` | yes | list of strings | The list of UAV IDs that the client is interested in

**Response and notification fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
`status` | no | object | Object mapping UAV IDs to the corresponding status information. The structure of this object is described by the [`UAVStatusInfo`](../types.md#uavstatusinfo) complex type.
`failure` | no | list of strings | List containing the UAV IDs for which the status information could not have been retrieved.
`reasons` | no | object | Object mapping UAV IDs to reasons why the corresponding status information could not have been retrieved.

All the UAV IDs that were specified in the request MUST appear *either* in the `status` list or in the `failure` list. When this message is sent as a notification, only the `status` field SHOULD be present.

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
        "1": {
            "id": "1",
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
                "yaw": 90
            },
            "velocity": {
                "north": 2.0,
                "east": 2.0,
                "down": -1.0
            },
            "timestamp": "2015-12-08T08:17:41.000Z",
            "debug": "MEJBRENBRkU=",
            "error": [42]
        }
    },
    "failure": ["spam"],
    "reasons": {
        "spam": "No such UAV."
    }
}
```

## `UAV-HALT` --- Initiate immediate shutdown

A client send this request to the server to initiate an immediate shutdown of an UAV in case of an emergency. Note that the UAV will *not* attempt to land - typically it will stop the rotors even in mid-air. Use this message only in emergencies.

The server responds with two lists: the first list contains the IDs of the UAVs where a shutdown attempt was *started* (in the sense that the UAV has been notified that they should land now), and the second list contains the IDs where such an attempt was not started. (Possible reasons for failure could be: invalid UAV ID, UAV does not support forced shutdown and so on). The server MAY decide to include more detailed information about failed attempts in the response.

Clients interested in whether the shutdown attempts have succeeded should keep an eye on [`UAV-INF`](#uav-inf-basic-status-information) messages and watch the status flags of the UAVs.

**Request fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
`ids` | yes | list of strings | The list of UAV IDs to target with this message

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
`success` | no | list of strings | The list of UAV IDs to which the request was sent
`failure` | no | list of strings | The list of UAV IDs to which the request was *not* sent
`reasons` | no | object | Object mapping UAV IDs to explanations about why the request failed for these UAVs.

All the UAV IDs that were specified in the request MUST appear *either* in the `success` list or in the `failure` list.

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

## `UAV-LAND` --- Initiate unsupervised landing

A client send this request to the server to initiate unsupervised landing on one or more UAVs. The server responds with two lists: the first list contains the IDs of the UAVs where an unsupervised landing attempt was *started* (in the sense that the UAV has been notified that they should land now), and the second list contains the IDs where such an attempt was not started. (Possible reasons for failure could be: invalid UAV ID, UAV does not support unsupervised landing and so on). The server MAY decide to include more detailed information about failed attempts in the response.

Clients interested in whether the landing attempts have succeeded should keep an eye on [`UAV-INF`](#uav-inf-basic-status-information) messages and watch the status flags of the UAVs.

**Request fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
`ids` | yes | list of strings | The list of UAV IDs to target with this message

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
`success` | no | list of strings | The list of UAV IDs to which the request was sent
`failure` | no | list of strings | The list of UAV IDs to which the request was *not* sent
`reasons` | no | object | Object mapping UAV IDs to explanations about why the request failed for these UAVs.

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

## `UAV-LIST` --- List of all the UAVs known by the server

A client sends this request to the server to request the list of all UAVs currently known by the server. The semantics of "knowing" a UAV is left up to the server implementation and configuration; typically, the server will return an UAV ID in the response if it has received a status message from the given UAV recently, typically in the last few minutes.

**Request fields**

This request has no fields.

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
`ids` | yes | list of strings | The list of UAV IDs that the server knows

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

## `UAV-RTH` --- Initiate return to home position

A client send this request to the server to request some of the UAVs to return to their home positions.

The server responds with two lists: the first list contains the IDs of the UAVs where an unsupervised landing attempt was *started* (in the sense that the UAV has been notified that they should return to their home positions now), and the second list contains the IDs where such an attempt was not started. (Possible reasons for failure could be: invalid UAV ID, UAV does not know the concept of a home position and so on). The server MAY decide to include more detailed information about failed attempts in the response.

Clients interested in whether the targeted UAVs have returned to their home positions should keep an eye on [`UAV-INF`](#uav-inf-basic-status-information) messages and watch the GPS coordinates of the UAVs.

**Request fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
`ids` | yes | list of strings | The list of UAV IDs to target with this message

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
`success` | no | list of strings | The list of UAV IDs to which the request was sent
`failure` | no | list of strings | The list of UAV IDs to which the request was *not* sent
`reasons` | no | object | Object mapping UAV IDs to explanations about why the request failed for these UAVs.

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

## `UAV-TAKEOFF` --- Initiate unsupervised take-off

A client send this request to the server to initiate unsupervised take-off on one or more UAVs. The server responds with two lists: the first list contains the IDs of the UAVs where an unsupervised take-off was *started* (in the sense that the UAV has been notified that they should take off now), and the second list contains the IDs where such an attempt was not started. (Possible reasons for failure could be: invalid UAV ID, UAV does not support unsupervised take-off and so on). The server MAY decide to include more detailed information about failed attempts in the response.

Clients interested in whether the take-off attempts have succeeded should keep an eye on [`UAV-INF`](#uav-inf-basic-status-information) messages and watch the status flags of the UAVs.

**Request fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
`ids` | yes | list of strings | The list of UAV IDs to target with this message

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
`success` | no | list of strings | The list of UAV IDs to which the request was sent
`failure` | no | list of strings | The list of UAV IDs to which the request was *not* sent
`reasons` | no | object | Object mapping UAV IDs to explanations about why the request failed for these UAVs.

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


