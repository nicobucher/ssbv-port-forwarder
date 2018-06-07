# ssbv-port-forwarder
Small TM transfer frame forwarder for legacy TM/TC equipment

This little tool allows to broadcast frame data if used as a multiway proxy between legacy SSBV TM/TC equipment.

Use the example config.ini file to specify in- and outgoing port numbers and ip addresses. In the given config, data going through port 6001 would also be available on port 6000 to a third application.
