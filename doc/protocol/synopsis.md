# Synopsis

**Flockwave** is a [JSON][1]-based communication protocol in [CollMot Robotics][4]'s distributed UAV flock system that allows multiple ground control consoles (clients) to monitor and control an airborne flock of UAVs via a central ground station (server).

This document describes the key actors in the system and specifies the communication protocol in detail. The document assumes familiarity with [JSON][1] and standard networking concepts such as TCP streams, the Hypertext Transfer Protocol (HTTP) and WebSockets. Details of the [JSON][1] format can be found in [RFC 4627][2] and [ECMA 404][3].

[1]: http://json.org/
[2]: http://www.ietf.org/rfc/rfc4627.txt
[3]: http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf
[4]: http://www.collmot.com

# Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119][5].

[5]: http://www.ietf.org/rfc/rfc2119.txt

