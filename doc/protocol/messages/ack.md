# `ACK` --- Acknowledgment messages

The messages in this section are always used as responses; no request is ever sent with these message types.

## `ACK-ACK` --- Positive acknowledgment

Sent by the server to the client in response to requests that have been executed successfully and where it is not necessary for the response to convey any more detailed information.

**Response fields**

This response has no fields.

**Example response**
```js
{
    "type": "ACK-ACK"
}
```

## `ACK-NAK` --- Negative acknowledgment

Sent by the server to the client in response to requests that the server has either attempted to execute but failed to do so, or to requests that have been rejected outright by the server.

**Response fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
`reason` | no | string | Human-readable description of the reason for the negative acknowledgment.

**Example response**
```js
{
    "type": "ACK-NAK",
    "reason": "I'm sorry, Dave, I'm afraid I can't do that."
}
```

