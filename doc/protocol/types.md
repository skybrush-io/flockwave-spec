# Data types used in messages

This section describes the complex data types and structures that are used in
Flockwave messages. These data types were referenced from the **Known message
types** section above.

## Dates and times

![The preferred date and time format of Flockwave](http://imgs.xkcd.com/comics/iso_8601.png)

Dates, times and durations MUST always be expressed in UTC using an appropriate [ISO 8601][7] format (see also [RFC 3339][8], especially section 5.6 if you don't like paywalls). Unless stated otherwise, the following formats should be used:

* Dates should be expressed as *YYYY*-*MM*-*DD* (ISO 8601 extended format).
* Times should be expressed as *HH*:*mm*:*ss*.*sss* (ISO 8601 extended format). The millisecond part may be omitted if not relevant.
* Dates and times should be expressed as the date, followed by a literal `T`, followed by the time, followed by `Z`, where the `T` is the standard ISO 8601 separator between dates and times, and `Z` is the ISO 8601 marker for UTC (Zulu time).

[7]: http://www.iso.org/iso/home/standards/iso8601.htm
[8]: https://tools.ietf.org/html/rfc3339

## Angles

Angles are always expressed in degrees because radians are for mathematicians. Depending on the context, angles may either be expressed in the half-open interval [0, 360), or in the half-open interval [-180, 180) or [-90, 90). For instance, latitudes, longitudes, roll and pitch are naturally expressed in an interval centered around zero, while heading and yaw information is typically presented as a non-negative number. When in doubt, look at the formal JSON schema specification for the allowed range of an angle.

**Note**: Even though it is common in aviation to indicate 360 degrees instead of zero degree, we always transmit zero degree instead of 360 degrees in messages because it comes naturally from the way computers handle modulo arithmetics. The user interface may still opt to present zero degree as 360 degrees if the user prefers that.

## Byte arrays

The JSON format does not support the transmission of raw byte arrays directly since the JSON string type is a sequence of Unicode characters and not a sequence of raw bytes. When a raw byte array has to be transmitted in JSON, the typical solution is to send a base64-encoded representation as a string (see [RFC4648](https://tools.ietf.org/html/rfc4648)). This representation is approximately 33% longer than the corresponding raw byte array, but is still much shorter than the representation of the byte array as a JSON array of integers.

## `Attitude`

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

## `ChannelOperation`

Enumeration type that describes the possible operations that may be performed on a channel of a device (real or virtual) on a UAV. See [UAV devices and channels](devices.md) for more information. Currently the following values are defined:

`read`
: Represents the act of reading the current value of the channel.

`write`
: Represents the act of writing a new value to the channel.

## `ChannelType`

Enumeration type that describes the possible types of channels of a device (real or virtual) on a UAV. See [UAV devices and channels](devices.md) for more information. Currently the following values are defined:

`audio`
: A channel that provides a URL to an audio stream.

`boolean`
: A channel that provides a single Boolean value

`bytes`
: A channel that provides an array of raw bytes.

`color`
: A channel that provides a color in 8-bit RGB, RGBA or RGBW format. The color is typically expressed as an array of three or four bytes, each byte ranging from 0 to 255.

`duration`
: A channel that provides the duration of a time window, expressed as the number of seconds elapsed since the start of the time window. Fractional seconds are allowed.

`number`
: A channel that provides a single double-precision floating-point number.

`object`
: A channel that provides a complex JSON object.

`string`
: A channel that provides a UTF-8 encoded string.

`time`
: A channel that provides a time instant, expressed as the number of seconds elapsed since the UNIX epoch in UTC. Fractional seconds are allowed.

`video`
: A channel that provides a URL to a video stream.

## `ClockEpoch`

A `ClockEpoch` object describes the epoch of a clock or timer that the Flockwave server manages. It is either a [datetime](#dates-and-times) string or one of the following string values:

`unix`
: The UNIX epoch, i.e. midnight on 1 Jan 1970 UTC.

## `ClockInfo`

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

## `CommandExecutionStatus`

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

## `CommandResponse`

A `CommandResponse` object stores the response given by a particular UAV to a command
sent to it using a `CMD-REQ` request, along with a type annotation that tells the
receiver how the response should be interpreted.

Currently the Flockwave protocol defines the following response types:

`plain`
:    Plain text response that should be formatted on the receiver side as is.

`markdown`
:    Markdown-formatted text response that should be interpreted by a Markdown
:    processor before it is displayed to the user.

Additional response types may be defined by the user as needed.

**Example**

```js
{
    "type": "markdown",
	"data": "# Heading\n\nHello world!"
}
```

## `ConnectionInfo`

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

## `ConnectionPurpose`

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

## `ConnectionStatus`

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

## `DeviceClass`

Enumeration type that describes the possible classes (i.e. types) of devices ina  device tree. Device classes may be used by user interfaces talking to a Flockwave server to provide some feedback to the user about the type of a device (e.g., it could show batteries with a different icon). Currently the following values are registered:

`accelerometer`
: The device is an accelerometer.

`altimeter`
: The device is an altimeter (e.g., pressure sensor, radar altimeter, sonic altimeter).

`battery`
: The device is a battery.

`camera`
: The device is a camera (consumer-grade, infrared, security camera or anything else).

`cpu`
: The device is the CPU of a UAV.

`cpuCore`
: The device is one particular CPU core of the CPU of a UAV.

`gps`
: The device is a GPS receiver.

`group`
: The device represents a logical grouping of other devices. For instance, the rotors of a UAV may be grouped in a `rotor` group.

`gyroscope`
: The device is a gyroscope.

`led`
: The device is a single LED or a LED strip.

`magnetometer`
: The device is a magnetometer.

`microphone`
: The device is a microphone.

`misc`
: The device does not fall into any of the predefined device classes.

`radio`
: The device is a radio receiver or transmitter (e.g., an XBee radio).

`rc`
: The device is an RC receiver.

`rotor`
: The device is a rotor.

`sensor`
: The device is a generic sensor that cannot be categorised more precisely into any of the other classes.

`speaker`
: The device is a speaker.

## `DeviceTreeNode`

This type represents a single node of the device tree. The node may represent a UAV, an onboard (real or virtual) device of a UAV, or a channel of a device. (See [UAV devices and channels](#uav-devices-and-channels) for more details).

**Fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
type | yes | [`DeviceTreeNodeType`](#devicetreenodetype) | The type of the node
subType | no | [`ChannelType`](#channeltype) | The type of the channel if the node is a channel node. This field is required for channel nodes and forbidden for other types of nodes.
class | no | [`DeviceClass`](#deviceclass) | The type of the device that this node represents. This field is optional for device nodes and forbidden for other types of nodes. Its value may be used by Flockwave clients to represent the device in a different way on the UI or to hide certain types of devices.
children | no | object of [`DeviceTreeNode`](#devicetreenode) | Object mapping names of child nodes to their descriptions
operations | no | list of [`ChannelOperation`](#channeloperation) | The list of operations supported by the channel. This field is required for channel nodes and forbidden for other types of nodes.
unit | no | string | The unit in which the value of the channel is represented. This field is optional for channel nodes (typically makes sense for numeric channels) and forbidden for other types of nodes.

## `DeviceTreeNodeType`

Enumeration type that describes the type of a device tree node (see [`DeviceTreeNode`](#devicetreenode). Currently the following values are defined:

`root`
: This is the root node of the device tree. The node has no parent by definition. The children of the root node must be nodes of type `uav`.

`uav`
: This is a tree node that represents a UAV in the flock. The parent of a `uav` node is always a `root` node. The children of the UAV nodes must be nodes of type `device`.

`device`
: This is a tree node that represents a device of a UAV, or a sub-device of another device. The parent of a `device` node is either a `uav` node or another `device` node.

`channel`
: This is a tree node that represents a channel of a device. The parent of a `channel` node is always a `device` node.

## `ErrorList`

This type is simply an array of numbers, where each number represents a possible error condition. See [Error codes](#error-codes) for a detailed listing of all the error codes that are currently defined in the Flockwave protocol.

## `GPSCoordinate`

This type represents a coordinate given by a GPS in the usual "latitude, longitude, altitude above mean sea level, altitude above ground level" format using the WGS 84 reference system.

Latitude and longitude should be specified with at least seven digits' precision if possible. (More than seven digits is usually not necessary because consumer GPS receivers are

**Fields**

Name | Required? | Type | Description
---- | --------- | ---- | -----------
lat | yes | float | The latitude, in degrees, in the range [-90,90)
lon | yes | float | The longitude, in degrees, in the range [-180,180)
amsl | no | float | The altitude, in metres, above mean sea level
agl | no | float | The altitude, in metres, above ground level

**Example**

```js
{
    "lat": 51.99765972,
    "lon": -0.74068634,
    "amsl": 93.765
}
```

## `UAVStatusInfo`

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
error | no | [ErrorList](#errorlist) | The list of error codes currently applicable for the UAV. When omitted, it means that there are no errors.
debug | no | [byte array](#byte-arrays) | Debug information provided by the algorithm running on the UAV (if applicable).

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
```

The debug information in the above example is then decoded to `0BADCAFE` using base64.

## `VelocityNED`

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


# Error codes

Error codes are typically small non-negative integers, divided into seven groups as follows:

No error (code 0)
:   Code zero is reserved for the "no error" condition. Since [UAVStatusInfo](#uavstatusinfo) structures contain a *list* of error codes, this error code is typically not used because it is enough to send an empty list to declare that there is no error.

Informational messages (codes 1-63)
:   These messages contain information that the UAV operators should be aware of, but that do not represent danger to the normal operation of the UAV. For instance, a UAV may use this code range to indicate that coordinate logging has stopped due to low disk space.

Warnings (codes 64-127)
:   These codes should be used for conditions that do not present *immediate* danger to the normal operation of the UAV but that will become a problem in the near future if left unhandled. For instance, low battery warnings belong to this category.

Error conditions (codes 128-191)
:   These codes should be used in cases when the UAV has detected a problem that prevents it from continuing normal operation, but the situation is not severe enough to warrant an immediate landing attempt. UAVs typically switch to an automatic "return to home" or "loitering" mode when they detect such a condition.

Fatal errors (codes 192-255)
:   These codes should be used when the UAV has detected a severe malfunction that triggers an immediate landing attempt (if such an attempt is feasible) or an uncontrolled shutdown in the worst case.

UAV-specific error codes (codes 256-32767)
:   These codes will be used in the future for custom, UAV-specific error conditions should such error codes become necessary. The range will be divided into blocks of 256 error codes, each of which can be allocated for a specific UAV type that future versions of this protocol will support.

User-defined error codes (codes 32768 and above)
:   Custom, unofficial extensions of the Flockwave protocol are free to use this range for any purpose.

Note that for error codes less than 256, `(errorCode & 0xFF) >> 6` will simply return the severity class of the error code (class 0: informational messages, class 1: warnings, class 2: errors, class 3: fatal errors). Ideally, this property should be kept also for codes above 256 whenever possible to make it easier for Flockwave GUI clients to derive the severity of an error message even if the actual semantics of the error message is not known to the GUI client.

The following tables list all the commonly used error codes in [ErrorList](#errorlist) members typically found in [UAVStatusInfo](#uavstatusinfo) structures.

## Informational messages (codes 1-63)

Code | Description
---- | -----------
   1 | Logging deactivated.<br>This message is shown when logging-capable UAVs are not able to write entries to their logs for some reason.

## Warnings (codes 64-127)

Code | Description
---- | -----------
  64 | Low disk space.<br>This message is shown by UAVs having an internal storage (e.g., an SD card) in cases when they are running out of free space on the storage device.
  65 | RC signal lost.<br>Use this error code only if the UAV can deal with this situation (e.g., when it is running an algorithm that does not require external control in normal conditions); otherwise use code 131.
  66 | Battery low.<br>Use this error code only if the UAV is still safe to continue its current mission with the current battery charge; otherwise use code 134 or 199.

## Errors (codes 128-191)

Code | Description
---- | -----------
 128 | Autopilot communication timeout.<br>High-level control algorithms failed to communicate with a lower-level autopilot component. The autopilot will probably attempt RTH or switch to loiter mode.
 129 | Autopilot acknowledgment timeout.<br>A lower-level autopilot component did not acknowledge a command sent to it by a higher-level control algorithm.
 130 | Autopilot communication protocol error.<br>High-level control algorithms failed to parse a message sent by the lower-level autopilot component or vice versa. The autopilot will probably attempt RTH or switch to loitering mode.
 131 | Prearm check failure.<br>One of the pre-flight checks has failed.
 132 | RC signal lost.<br>Use this error code only if the UAV can not deal with this situation and will RTH or land; otherwise use code 65.
 133 | GPS error or GPS signal lost.<br>Use this error code only if loitering is probably still possible with the remaining sensors; otherwise use code 197.
 134 | Battery low.<br>Use this error code only if the UAV is not safe to continue its current mission with the current battery charge but can safely attempt RTH or loitering; otherwise use code 66 or 199.
 135 | Target not found.<br>The UAV does not find the target waypoint or beacon that it should attempt to follow.
 136 | Target is too far.<br>The target of the UAV is outside the allowed safety distance.
 188 | Simulated error.<br>Use this error code to trigger a simulated RTH or loitering in the absence of any other error, for testing purposes.
 189 | Error in control algorithm.<br>Use this error when the higher-level control algorithm that drives the autopilot of the UAV failed to produce sensible input for the autopilot.
 190 | Other, unspecified sensor failure that does not prevent RTH or loitering.
 191 | Other, unspecified error that does not prevent RTH or loitering.

## Critical errors (codes 192-255)


Code | Description
---- | -----------
 192 | Incompatible hardware or software.<br>Some hardware or software components are not compatible with each other; e.g., using a PixHawk-based autopilot with an incompatible FlockCtrl software.
 193 | Magnetic sensor error.
 194 | Gyroscope error.
 195 | Accelerometer error.
 196 | Pressure sensor or altimeter error.
 197 | GPS error or GPS signal lost.<br>Use this error code only if loitering will not be attempted by the UAV with the remaining sensors; otherwise use code 133.
 198 | Motor malfunction.
 199 | Battery critical.<br>Use this error code only if the UAV is not safe to continue its current mission or to attempt RTH or loitering; otherwise use code 66 or 134.
 200 | No GPS home position.
 201 | Geofence violation (out of flying zone).<br>When leaving the designated flying zone, it is generally assumed that the UAV does not (and can not) know how to navigate back to the flying zone so it will attempt to land where it currently is.
 202 | Internal clock error.<br>This code should be used if one of the internal clocks of the UAV is not set properly. Use code 203 for external clocks.
 203 | External clock error.<br>This code should be used if one of the external clocks required for the operation of the UAV is not set properly. Use code 202 for internal clocks.
 204 | Required hardware component missing.<br>The UAV can not communicate with one of the hardware components that it needs to use during its mission.
 253 | Simulated critical error.<br>Use this error code to trigger an emergency landing in the absence of any other critical error, for testing purposes.
 254 | Other, unspecified sensor failure that triggers an immediate landing attempt.
 255 | Other, unspecified fatal error that triggers an immediate landing attempt.



