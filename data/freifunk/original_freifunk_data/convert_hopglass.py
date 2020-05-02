#!/usr/bin/env python3

from pathlib import Path
import argparse
import json
import sys
import os


parser = argparse.ArgumentParser()
parser.add_argument("input", help="Input meshviewer file.")
parser.add_argument('--formatted', action="store_true", help="Formatted JSON output data.")
args = parser.parse_args()

links = {}
# map to give each node a short number
nodes = {}


def link_id(link):
	source = link['source']
	target = link['target']
	if source > target:
		return f"{source}->{target}"
	else:
		return f"{target}->{source}"

with open(args.input, "r") as file:
	obj = json.load(file)

	# record all nodes
	for node in obj['JSON']['rows']:
		e = {'id': len(nodes)}

		if 'hostname' in node['value']:
			e['name'] = node['value']['hostname']

		if 'latlng' in node['value']:
			e['x'] = float(node['value']['latlng'][0])
			e['y'] = float(node['value']['latlng'][1])

		nodes[node['id']] = e

		if 'links' in node['value']:
			for lnode in node['value']['links']:
				if lnode['id'] not in nodes:
					e = {'id': len(nodes)}

					if lnode['id'].endswith('.olsr'):
						e['name'] = lnode['id'][:-5]

					nodes[lnode['id']] = e

	for node in obj['JSON']['rows']:
		if 'links' not in node['value']:
			continue

		for lnode in node['value']['links']:
			target = lnode['id']

			link = {
				'source': nodes[node['id']]['id'],
				'target': nodes[lnode['id']]['id']
			}

			if 'olsr_ipv4' in lnode:
				link_quality = lnode['linkQuality']
				link['source_tq'] = link_quality
				link['target_tq'] = link_quality

			lid = link_id(link)
			if lid not in links:
				links[lid] = link

if args.formatted:
	json.dump({'nodes': list(nodes.values()), 'links': list(links.values())}, sys.stdout, indent="  ", sort_keys = True)
else:
	json.dump({'nodes': list(nodes.values()), 'links': list(links.values())}, sys.stdout, sort_keys = True)
