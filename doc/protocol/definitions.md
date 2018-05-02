# Definitions

Flockwave client
:   An application that can be used to monitor the status of the UAV flock on a map and/or send commands to individual UAVs or groups of UAVs. A Flockwave client may be implemented as a standalone desktop application, a web application running in a desktop or mobile browser, a native mobile application (typically on Android or iOS) or even as a command-line application. Flockwave clients talk to a *Flockwave server* that is responsible for relaying commands and status information between the drones in the flock and the clients.

Flockwave server
:   A headless server application that can accept connections from *Flockwave clients* and maintains one or several additional connections to the UAVs and other data sources (for instance, DGPS data providers).

UAV (abbr.)
:   Unmanned aerial vehicle; typically a quad-, hexa- or octocopter that is equipped with the necessary onboard computer, software and communication equipment that enables it to participate in an UAV flock. Even though it is called an *aerial* vehicle, not all UAVs are required to be airborne. (See also: *beacon*). Each UAVs consists of a set of *devices* and *channels* that are organised in a tree-like structure. See [UAV devices and channels](devices.md) for more information.

Beacon
:    A subtype of *UAV* that is not capable of moving on its own but can broadcast its position to other UAVs in the flock.

Device
:    A hardware component, an external peripheral or a virtual software component attached to a UAV that provides real-time measurement data via a set of *channels*. For instance, a UAV may have a device named `battery` that provides the voltage of the battery of the UAV via a single numeric channel named `voltage`. See [UAV devices and channels](devices.md) for more information.
