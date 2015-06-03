# Debian Package Graph
Create a dot graph from a supplied debian source package name, it's binary packages and their depenencies,
conflicts, suggested packages and recommended packages. (Python3!)

## Dependencies
* [psycopg2](https://pypi.python.org/pypi/psycopg2)
* [Graphviz](http://www.graphviz.org/)

The above can be installed with the following debian command;
> apt-get install python3-psycopg2 graphviz

## Usage
Supply a positional package name argument and, optionally, a --release argument (defaults to sid) for
debian release by command line and a dot-create SVG file will be piped to STDOUT.
> ./make_dot.py iptables --release stretch > iptables_stretch.svg

In the created SVG, green lines represent depenency relations, red lines represent conflict relations,
blue lines represent recommended relations and yellow lines represent suggested relations, the
dashed versions of these represent the same meanings but originating from source package.
Purple lines are connections between source package and binary packages.

![Example graph](https://raw.githubusercontent.com/jesopo/debian-package-graph/master/example_iptables_stretch.svg)
