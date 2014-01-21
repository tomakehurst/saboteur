Breakbox
========

Breakbox is a network fault injection tool that aims to simplify resilience and stability testing.
Its core component is an agent that accepts commands over HTTP and configures its host's network stack
for various common fault scenarios.

Currently these include:
-   Total network partition
-   Remote service dead (not listening on the expected port)
-   Delays
-   Packet loss
-   TCP connection timeout (as often happens when two systems are separated by a stateful firewall)

An RPM package is available for the agent. See [Releases](https://github.com/tomakehurst/breakbox/releases "Releases").

Adding faults
-------------
Breakbox has a simple JSON over HTTP API. To add a new rule, simply POST to the agent process on port 6660 e.g.

``
    $ curl -X POST -d '{ "name": "packet-loss-to-app-server",
    "type": "PACKET_LOSS",
    "direction": "IN",
    "to_port": 8080,
    "probability": 0.2,
    "correlation": 25 }' http://192.168.2.11:6660/
``

See [breakbox-tests.py](https://github.com/tomakehurst/breakbox/blob/master/agent/breakbox-tests.py "breakbox-tests.py")
for more examples of valid commands.

Resetting
---------
To reset all faults, send a DELETE request to the root path e.g.

``
    $ curl -X DELETE http://192.168.2.11:6660/
``
