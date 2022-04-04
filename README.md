Flockwave protocol specification
================================

This repository contains the documentation of the Flockwave communication
protocol in [CollMot Robotics][1]'s distributed UAV flock system that allows
multiple ground control consoles (clients) to monitor and control an airborne
flock of UAVs via a central ground station (server).

The ``doc`` folder contains a human-readable documentation of the protocol.
Formal [JSON Schema][2] specifications of most of the message that are used
in the protocol are stored in the ``src/flockwave/spec`` folder, starting
from the top-level ``message.json`` file.

[1]: https://collmot.com
[2]: https://json-schema.org

License
-------

`flockwave-spec` is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

`flockwave-spec` is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.
