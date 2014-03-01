Saboteur
========

Saboteur is a network fault injection tool that aims to simplify resilience and stability testing.
Its core component is an agent that accepts commands over HTTP and configures its host's network stack
for various common fault scenarios.

Currently these include:
-   Total network partition
-   Remote service dead (not listening on the expected port)
-   Delays
-   Packet loss
-   TCP connection timeout (as often happens when two systems are separated by a stateful firewall)

Currently it is Linux only, but support may be added for OSX in future.

An RPM package is available for the agent. See [Releases](https://github.com/tomakehurst/saboteur/releases "Releases").

A CLI is also available as an RPM under releases, or you can just download and use it directly from source https://raw.github.com/tomakehurst/saboteur/master/cli/sab.

Installing the agent
--------------------
Currently the agent installs from an RPM only (DEB package to follow). It's only dependency is Python 2.6.6+, so if this is already installed you can install the RPM directly:

``
    $ rpm -ivh https://github.com/tomakehurst/saboteur/releases/download/v0.5/saboteur-agent-0.5-1.noarch.rpm
``

After installation, start the agent daemon in the usual way:

``
    $ service saboteur-agent start
``


Using the CLI
-------------
The command line interface supports three types of action:
* Define a new client/service
* Add a fault
* Reset all faults

*Note: I'm not particularly keen on the defined client/service model for the CLI, so I'll probably change it to accept
host, port and direction directly when adding faults*

A client or service must first be defined before faults can be added or reset. You should define a client when the saboteur agent is running on the same host as client to a remote service. For instance if my application on host app01 connects to a database cluster on hosts db01 and db02 (listening on port 3306) and the saboteur agent is running on app01, I'd define a client:

``
    $ sab define-client db --hosts app01 --to_port 3306
``

Then I can add some delay onto packets between my app and anything listening on port 3306:

``
    $ sab add db --fault_type DELAY --delay 200 --variance 50 --distribution normal
``

When I want to put everything back to normal I can issue a reset:

``
    $ sab reset db
``

When running the saboteur agent on the host of the service being depended on, define a service instead. If the agent is running on the database hosts from the previous example, define the service this way:

``
    $ sab define-service db --hosts db01,db02 --to_port 3306
``

Typing ``sab -h`` prints detailed usage information.

Using the HTTP API directly
---------------------------
Saboteur has a simple JSON over HTTP API. To add a new rule, simply POST to the agent process on port 6660 e.g.
``
    $ curl -X POST -d '{ "name": "packet-loss-to-app-server",
    "type": "PACKET_LOSS",
    "direction": "IN",
    "to_port": 8080,
    "probability": 0.2,
    "correlation": 25 }' http://192.168.2.11:6660/
``

See [saboteur-tests.py](https://github.com/tomakehurst/saboteur/blob/master/agent/saboteur-tests.py "saboteur-tests.py")
for more examples of valid commands.

To reset all faults, send a DELETE request to the root path e.g.

``
    $ curl -X DELETE http://192.168.2.11:6660/
``

Resilience testing Saboteur and JUnit
-------------------------------------
[Crash Lab](https://github.com/tomakehurst/crash-lab) is a Java library for automating resilience/stabilty type tests
(or any scenario involving network faults), which has a Saboteur client as part of it, and
[some examples](https://github.com/tomakehurst/crash-lab/blob/master/src/test/java/com/tomakehurst/crashlab/ExampleScenarios.java).



Limitations
-----------
The Saboteur agent currently implements its reset feature by deleting all iptables and tc rules, so it currently won't
play nicely on systems that have rules configured via other means. This will be improved in future, probably by having
Saboteur keep track of rules it has created so that these can be targeted for reset.

It's also likely that adding multiple DELAY and/or PACKET_LOSS rules will not work correctly.

Fixes are coming for both of these issues.
