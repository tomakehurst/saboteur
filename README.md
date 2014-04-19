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

RPM and DEB packages are available for the agent. See [Releases](https://github.com/tomakehurst/saboteur/releases "Releases").

A CLI is also available as an RPM under releases, or you can just download and use it directly from source https://raw.github.com/tomakehurst/saboteur/master/bin/sab.

Installing the agent and CLI
----------------------------
Saboteur's only dependency is Python 2.6.6+.

To install from the RPM:

``
    $ rpm -ivh https://github.com/tomakehurst/saboteur/releases/download/v0.6/saboteur-0.6-1.noarch.rpm
``

And from the DEB package:

``
    $ wget -P /tmp https://github.com/tomakehurst/saboteur/releases/download/v0.6/saboteur_0.6_all.deb && dpkg --install /tmp/saboteur_0.6_all.deb
``

After installation, start the agent daemon in the usual way:

``
    $ service saboteur-agent start
``

Compatibility
-------------
So far I've verified that Saboteur works on Centos 6.4, Red Hat 6.4 and Ubuntu 12.10. It currently has some issues with the
tc defaults on Fedora 18, so only the NETWORK_FAILURE, SERVICE_FAILURE and FIREWALL_TIMEOUT fault types work on that OS.

I'd welcome any feedback about successes/failures on other distros or versions.


Using the CLI
-------------
The Saboteur package installs a CLI executable which can be used to configure and reset faults both locally and remotely.
Typing ``sab`` without arguments (or with ``-h``) will display usage information.

To create a new fault:

``
    $ sab add --fault_type NETWORK_FAILURE --to_port 8818 --direction IN --hosts myhost1,myhost2
``

To remove all faults:

``
    $ sab reset --hosts myhost1,myhost2
``

Note: omitting ``--hosts`` will cause commands to be sent to localhost.


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

See [the tests](https://github.com/tomakehurst/saboteur/blob/master/tests/apicommands_tests.py "the tests")
for more examples of valid commands.

To reset all faults, send a DELETE request to the root path e.g.

``
    $ curl -X DELETE http://192.168.2.11:6660/
``

Resilience testing Saboteur and JUnit
-------------------------------------
[Crash Lab](https://github.com/tomakehurst/crash-lab) is a Java library for automating resilience/stability type tests
(or any scenario involving network faults), which has a Saboteur client as part of it, and
[some examples](https://github.com/tomakehurst/crash-lab/blob/master/src/test/java/com/tomakehurst/crashlab/ExampleScenarios.java).



Limitations
-----------
The Saboteur agent currently implements its reset feature by deleting all iptables and tc rules, so it currently won't
play nicely on systems that have rules configured via other means. This will be improved in future, probably by having
Saboteur keep track of rules it has created so that these can be targeted for reset.

It's also likely that adding multiple DELAY and/or PACKET_LOSS rules will not work correctly.

Fixes are coming for both of these issues.

Finally, please don't use this in production (yet)! It's in no way secure, and would make an ideal attack vector for
anyone wanting to DoS your site.

I'm considering trying to make the agent secure enough to be used as a building block for a chaos monkey. Again, any
feedback on the usefulness of this would be appreciated!
