#!/usr/bin/env python3
import argparse, json, os, re, subprocess, sys
import psycopg2

def get_variable(s):
    return "\"%s\"" % s

def parse_csv(s):
    parsed_set = set([])
    if s:
        s_list = s.split(",")
        for piece in s_list:
            piece = piece.strip().split(" ", 1)[0]
            parsed_set.add(piece)
    return sorted(parsed_set)

def make_list(from_variable, to_list, line_colour, line_style="solid"):
    dot_text = ""
    if to_list:
        for to_name in to_list:
            to_variable = get_variable(to_name)
            dot_text += "    %s [label=\"%s\"];\n" % (to_variable, to_name)
            dot_text += "    %s -> %s [color=%s, style=%s];\n" % (from_variable,
                to_variable, line_colour, line_style)
    return dot_text
def make_binary_digraph(source_variable, binary_name, binary_depends,
        binary_conflicts, binary_recommends, binary_suggests):
    binary_variable = get_variable(binary_name)
    dot_text =  "    %s [label=\"%s\"];\n" % (binary_variable, binary_name)
    dot_text += "    %s -> %s [color=purple];\n" % (source_variable, binary_variable)
    dot_text += make_list(binary_variable, parse_csv(binary_depends), "green")
    dot_text += make_list(binary_variable, parse_csv(binary_conflicts), "red")
    dot_text += make_list(binary_variable, parse_csv(binary_recommends), "blue")
    dot_text += make_list(binary_variable, parse_csv(binary_suggests), "yellow")
    return dot_text

arg_parser = argparse.ArgumentParser(description=
    "Create SVG graph of package dependencies and conflicts from debian repositories.")
arg_parser.add_argument("--release", default="sid", help="Debian release (default: sid)")
arg_parser.add_argument("--format", default="svg", help="Output format (default: svg)")
arg_parser.add_argument("package", help="Name of the package to render a graph of")
args = arg_parser.parse_args()

db = psycopg2.connect(host="public-udd-mirror.xvm.mit.edu", database="udd", user=
    "public-udd-mirror", password="public-udd-mirror")
db_cursor = db.cursor()

db_cursor.execute(
    """SELECT source, version, build_depends, build_conflicts FROM sources WHERE
    source=%s AND release=%s ORDER BY version DESC""",
    [args.package, args.release])
source_result = db_cursor.fetchone()
if not source_result:
    sys.stderr.write("Source package not found\n")
    sys.exit()
source_name = source_result[0]
version = source_result[1]
build_depends = source_result[2]
build_conflicts = source_result[3]

db_cursor.execute("""SELECT package, depends, conflicts, recommends, suggests FROM
    packages WHERE source=%s AND release=%s AND source_version=%s AND 
    (architecture='amd64' OR architecture='all')""", [source_name,
    args.release, version])
binary_results = db_cursor.fetchall()

build_depends_list = parse_csv(build_depends)
build_conflicts_list = parse_csv(build_conflicts)

source_variable = "source"
dot_text =  "digraph g {\n"
dot_text += "    graph [nodesep=0.1, ranksep=3, rankdir=LR, center=true];\n"
dot_text += "    edge [weight=1];\n"
dot_text += "    node [fontsize=12];\n"
#dot_text += "    splines=\"false\";\n"
dot_text += "    %s [label=\"%s\", shape=box];\n" % (source_variable, source_name)
dot_text += make_list(source_variable, build_depends_list, "green", "dashed")
dot_text += make_list(source_variable, build_conflicts_list, "red", "dashed")

for package_name, package_depends, package_conflicts, package_recommends, \
        package_suggests in binary_results:
    dot_text += make_binary_digraph(source_variable, package_name, package_depends, package_conflicts,
        package_recommends, package_suggests)
dot_text += "}\n"

process = subprocess.Popen(["dot", "-T", args.format], stdout=subprocess.PIPE,
    stdin=subprocess.PIPE)
process.stdin.write(dot_text.encode("utf8"))
svg = process.communicate()[0].decode("utf8")
process.stdin.close()
sys.stdout.write(svg)