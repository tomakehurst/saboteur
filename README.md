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

A CLI is also available as an RPM under releases, or you can just download and use it directly from source https://raw.github.com/tomakehurst/breakbox/master/cli/bbox.

Using the CLI
-------------
The command line interface supports three types of action:
* Define a new client/service
* Add a fault
* Reset all faults

A client or service must first be defined before faults can be added or reset. You should define a client when the breakbox agent is running on the same host as client to a remote service. For instance if my application on host app01 connects to a database cluster on hosts db01 and db02 (listening on port 3306) and the breakbox agent is running on app01, I'd define a client:

``
    $ bbox define-client db --hosts db01,db02 --to_port 3306
``

Then I can add some delay onto packets between my app the the DB nodes:

``
    $ bbox add db --fault_type DELAY --delay 200 --variance 50 --distribution normal
``

When I want to put everything back to normal I can issue a reset:

``
    $ bbox reset db
``

Using the HTTP API directly
---------------------------
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

To reset all faults, send a DELETE request to the root path e.g.

``
    $ curl -X DELETE http://192.168.2.11:6660/
``
