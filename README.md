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

Currently it is Linux only, but support may be added for OSX in future.

An RPM package is available for the agent. See [Releases](https://github.com/tomakehurst/breakbox/releases "Releases").

A CLI is also available as an RPM under releases, or you can just download and use it directly from source https://raw.github.com/tomakehurst/breakbox/master/cli/bbox.

Installing the agent
--------------------
Currently the agent installs from an RPM only (DEB package to follow). It's only dependency is Python 2.6.6+, so if this is already installed you can install the RPM directly:

``
    $ rpm -ivh https://github.com/tomakehurst/breakbox/releases/download/v0.2/breakbox-agent-0.2-1.noarch.rpm
``

After installation, start the agent daemon in the usual way:

``
    $ service breakbox-agent start
``


Using the CLI
-------------
The command line interface supports three types of action:
* Define a new client/service
* Add a fault
* Reset all faults

A client or service must first be defined before faults can be added or reset. You should define a client when the breakbox agent is running on the same host as client to a remote service. For instance if my application on host app01 connects to a database cluster on hosts db01 and db02 (listening on port 3306) and the breakbox agent is running on app01, I'd define a client:

``
    $ bbox define-client db --hosts app01 --to_port 3306
``

Then I can add some delay onto packets between my app and anything listening on port 3306:

``
    $ bbox add db --fault_type DELAY --delay 200 --variance 50 --distribution normal
``

When I want to put everything back to normal I can issue a reset:

``
    $ bbox reset db
``

When running the breakbox agent on the host of the service being depended on, define a service instead. If the agent is running on the database hosts from the previous example, define the service this way:

``
    $ bbox define-service db --hosts db01,db02 --to_port 3306
``

Typing ``bbox -h`` prints detailed usage information.

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

Limitations
-----------
The Breakbox agent currently implements its reset feature by deleting all iptables and tc rules, so it currently won't play nicely on systems that have rules configured via other means. This will be improved in future, probably by having Breakbox keep track of rules it has created so that these can be targeted for reset.

It's also likely that adding multiple DELAY and/or PACKET_LOSS rules will not work correctly in many cases.
