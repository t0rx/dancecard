Dancecard
=========

This is an algorithm to solve the "driving trip" problem:
* n cars
* 2n drivers
* s sessions
* In each session, 2 drivers pair up per car
* We want to optimise for:
  * Everyone driving each car roughly the same number of times
  * Everyone driving with everyone else evenly
  * Minimising repetition - e.g. driving same car or with same person in nearby sessions

For full documentation, see the wiki page at https://github.com/t0rx/dancecard/wiki,


Build instructions
------------------

`dancecard.py` should run directly as long as you have [pyyaml](http://pyyaml.org/wiki/PyYAMLDocumentation) and [paho-mqtt](https://pypi.python.org/pypi/paho-mqtt/1.1) installed.  See those links for installation instructions.

To build the Docker images, run `./build` (you may need to do this under sudo if you haven't [given your user docker perms](https://docs.docker.com/engine/installation/linux/linux-postinstall/)).  You may want to edit the build script to change the docker repo user away from `t0rx`.

The build script should automatically detect if you're building on a Raspberry Pi and switch to Dockerfile-rpi rather than Dockerfile.  This depends on a couple of base images I maintain, but could easily be made standalone.

Enjoy,

`t0rx`
