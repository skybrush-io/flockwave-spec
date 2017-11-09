# `CMD` --- Direct command execution on UAVs

## `CMD-INF` --- Retrieve execution status of a command

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
`ids` | yes | list of strings | The list of receipts for the command execution requests that the client is interested in

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
`status` | no | object | Object mapping receipts to the corresponding status information. The structure of this object is described by the [`CommandExecutionStatus`](../types.md#commandexecutionstatus) complex type.
`failure` | no | list of strings | List containing the connection IDs for which the status information could not have been retrieved.
`reasons` | no | object | Object mapping connection IDs to reasons why the corresponding status information could not have been retrieved.

All the receipts that were specified in the request MUST appear *either* as keys in the `status` object or in the `failure` list.

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

## `CMD-REQ` --- Send a command execution request to a UAV

A client sends this request to the server to ask the server to forward a command to one or more UAVs. The interpretation of the command string depends entirely on the UAV; for instance, a UAV running our `flockctrl` software will accept `flockctrl` console commands and respond appropriately. The server merely acts as a forwarder between the client and the UAV.

Depending on the protocol that the targeted UAV speaks, it may accept a raw command string only, or a command string with positional and/or keyword arguments. Positional arguments are passed as a single array. Keyword arguments are passed as a JSON object that maps the names of the arguments to their values. It is the responsibility of the caller to ensure that the command and its arguments use the appropriate syntax.

Sending and executing a command typically takes some time (especially because there is usually a slower radio link involved between the ground station and the UAV). To keep things running smoothly, the server will not wait for the responses of the UAVs to arrive - it will respond with a `UAV-CMD` response packet as soon as it has attempted to send the command to all the UAVs. The response packet will list the IDs of the UAVs for which the transmission failed, as well as a mapping that maps the IDs of the UAVs for which the command was sent successfully to unique *receipts* that can be used by the client to retrieve the progress of execution for these commands using a [CMD-INF](#cmd-inf-retrieve-execution-status-of-a-command) command. The actual response of a command request (sent by a targeted UAV) will be relayed back to the client that initiated the command in a [CMD-RESP](#cmd-resp-response-to-a-command-request) notification.

**Request fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
`ids` | yes | list of strings | The list of UAV IDs that the command should be sent to
`command` | yes | string | The command to send to the UAVs
`args` | no | array | The positional arguments of the command
`kwds` | no | object | The keyword arguments of the command

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
`receipts` | no | object  | Object that maps the UAV IDs for which the command was sent successfully to the corresponding receipts that can be used to track the progress of execution of the command until the actual response is received. Each receipt is a string; its format is unspecified and it is the responsibility of the server to ensure its uniqueness.
`failure` | no | list of strings | List containing the UAV IDs for which the status information could not have been retrieved.
`reasons` | no | object | Object mapping UAV IDs to reasons why the corresponding status information could not have been retrieved.

All the connection IDs that were specified in the request MUST appear *either* in the `receipts` mapping as keys or in the `failure` list.

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

## `CMD-RESP` --- Response to a command request

A server sends a notification of this type to a client when an earlier command execution request sent by the client has been completed by one of the UAVs the request was targeted to.

**Notification fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
`id` | yes | string | The receipt identifier that tells the client which response sent which UAV is being relayed in this notification.
`response` | yes | string | The response sent by the UAV.

**Example notification**
```js
{
    "type": "CMD-RESP",
    "id": "0badcafe-deadbeef:1",
    "response": "Hello there!"
}
```

## `CMD-TIMEOUT` --- Command request timeout notification

A server sends a notification of this type to a client when an earlier command execution request sent by the client has timed out (i.e. the UAV the command was targeted to failed to return a response in time).

**Notification fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
`ids` | yes | list of strings | The list of receipts for the command execution requests that have timed out

**Example notification**
```js
{
    "type": "CMD-TIMEOUT",
    "ids": ["0badcafe-deadbeef:1", "0badcafe-deadbeef:2"]
}
```


