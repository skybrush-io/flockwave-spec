# UAV devices and channels

Each UAV in the Flockwave system may consist of an arbitrary number of
*devices*. Devices usually correspond to real, tangible hardware components of
a UAV (such as a CPU, a battery, a LED or a camera), but they may also
represent virtual components implemented purely in software. Each device may
contain additional sub-devices (sub-sub-devices and so on), and each device (or
sub-device) may also provide a set of *channels* through which information
(e.g., measurement data) can be retrieved from and sent to the device. Channels
have a *type* that defines what sort of information one can read from the
channel, or what sort of information one can write to the channel. The UAV, its
devices, sub-devices and channels form a tree-like structure that is rooted at
the UAV itself, and each UAV, device, sub-device and channel can be uniquely
identified by the path leading from the tree root to the object being
considered. These paths are called *device paths* (when they terminate at
a device) or *channel paths* (when they terminate at a channel), or,
collectively, they may be referred to as *device tree paths*. When a path is
represented as a string, a forward slash (`/`) must be used to separate the
path components; for example, `/UAV-17/rotors/rotor1/rpm` can represent the
channel providing the rotations per minute (rpm) for the first rotor of
a quadrocopter.

As an example, consider a quadrocopter that consists of four rotors, a battery,
a CPU, a status LED, an on-board RGBW LED strip and a camera. In this setup, we
can identify the following devices, sub-devices and channels:

* *Rotors* (device)
    * *Rotor 1* (sub-device)
        * Rotations per minute (numeric channel, read only)
    * *Rotor 2* (sub-device)
        * Rotations per minute (numeric channel, read only)
    * *Rotor 3* (sub-device)
        * Rotations per minute (numeric channel, read only)
    * *Rotor 4* (sub-device)
        * Rotations per minute (numeric channel, read only)
* *Battery* (device)
    * Voltage (numeric channel, read only)
    * Charge percentage (numeric channel, read only)
    * Estimated remaining time (duration channel, read only)
* *Lighting system* (device)
    * *Status LED* (sub-device)
        * Is the LED turned on? (Boolean channel, read/write)
    * *RGBW LED strip* (sub-device)
        * Duty cycle of red (R) channel (numeric channel, read/write)
        * Duty cycle of green (G) channel (numeric channel, read/write)
        * Duty cycle of blue (B) channel (numeric channel, read/write)
        * Duty cycle of white (W) channel (numeric channel, read/write)
* *CPU* (device)
    * *CPU load* (numeric channel, read only)
    * *Reset switch* (Boolean channel, write only)
* *Camera* (device)
    * *Manufacturer ID* (string channel, read only)
    * *Video stream* (video channel, read only)

The example above contains almost all of the channel types and configurations
supported by the Flockwave protocol:

Boolean channels
: Boolean channels provide a single binary value (zero or one, yes or no, true or false). Typical use-case: turning a certain component on and off, sending a RESET signal etc.

Numeric channels
: Numeric channels provide a single floating-point value. Due to the usage of JSON as the transport protocol, numeric values provided by the channel must be representable as an IEEE-754 double-precision floating point number. Typical use-case: sending or retrieving measurement data.

String channels
: String channels provide a character string encoded in UTF-8. Typical use-case: sending version strings, manufacturer IDs, or human-readable debug information.

Byte array channels
: Byte array channels provide a sequence of raw bytes. Typical use-case: sending machine-readable debug information, raw measurements that are too complex for a single numeric channel, or serialized objects using a non-JSON format.

Color channels
: Color channels provide an array of three or four bytes, encoding a color in 8-bit RGB, RGBA or RGBW format. Typical use-case: color of a LED strip.

Time channels
: Time channels provide a time instant, expressed as the number of seconds elapsed since the UNIX epoch in UTC. Typical use-case: reporting the time of certain important events (e.g., when a UAV was turned on, when a packet of a certain type was received the last time and so on).

Duration channels
: Duration channels provide the length of a time interval, expressed as the number of seconds elapsed since the beginning of the time interval. Typical use-case: uptime, flight duration, time left until a certain event and so on.

Object channels
: Object channels provide complex structured or unstructured information in the form of JSON-encoded objects.

Audio and video channels
: Audio and video channels provide real-time audio or video data. In practice, reading an audio or video channel typically yields a URL; the client wishing to read the actual audio or video data must then connect to this URL separately to obtain the audio or video stream.

Channels may be *read only*, *write only* or *bidirectional* (i.e. readable and writable).

