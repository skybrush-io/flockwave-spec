# `CONN` — Connection-related messages

## `CONN-INF` — Basic status information of one or more connections

A client sends this request to the server to obtain basic status information about one or more connections (e.g., radio links, DGPS streams) currently managed by the server.

This message may also be broadcast as a notification by the server on its own volition to all connected Flockwave clients to notify them about a status change of one of the managed connections.

**Request fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
`ids` | yes | list of strings | The list of connection IDs that the client is interested in

**Response and notification fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
`status` | no | object | Object mapping connection IDs to the corresponding status information. The structure of this object is described by the [`ConnectionInfo`](../types.md#connectioninfo) complex type.
`failure` | no | list of strings | List containing the connection IDs for which the status information could not have been retrieved.
`reasons` | no | object | Object mapping connection IDs to reasons why the corresponding status information could not have been retrieved.

All the connection IDs that were specified in the request MUST appear *either* in the `status` list or in the `failure` list. When this message is sent as a notification, only the `status` field SHOULD be present.

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
            "purpose": "dgps",
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

## `CONN-LIST` — List of all the connections managed by the server

A client sends this request to the server to obtain the list of all the connections (e.g., radio links, DGPS streams) currently managed by the server. The list of connections will *not* include connections to Flockwave clients.

**Request fields**

This request has no fields.

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
`ids` | yes | list of strings | The list of connection IDs for all the connections that the server manages

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
