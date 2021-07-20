#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon May 24 23:21:05 2021
@author: xipeng

This assist script helps to build controller rules
For each switch, we generate a json P4 switch config file for rule installing for the init process of the network
"""
from helperFunctions import *
import json

# First we load some preliminary config files to get basic hosts switches configuration, links, routes and SFC rules
# load basic hosts and switches config
baseFile = open("base.json", "r")
base = json.load(baseFile)
baseFile.close()


# build link array
linkFile = open("links.json", "r")
links = json.load(linkFile)
linkFile.close()

# from links to generate a target-port mapping config[sw]ect egress
# in this config[sw]ect, give src node and dst node, get the output port for the src switch
egress = {}

for link in links:
    # link is like ['s16', 's6', 1, {'delay': '0ms', 'bw': None, 'node1': 's16', 'node2': 's6', 'port2': 5, 'port1': 1}]
    if not egress.__contains__(link[3]["node1"]):
        egress[link[3]["node1"]] = {}
    if not egress.__contains__(link[3]["node2"]):
        egress[link[3]["node2"]] = {}
    egress[link[3]["node1"]][link[3]["node2"]] = link[3]["port1"]
    egress[link[3]["node2"]][link[3]["node1"]] = link[3]["port2"]

# load routes file
routes = {}

routeFile = open("routes.json", "r")

routes = json.load(routeFile)

routeFile.close()

# print routes

# build ipv4 routes for each switch from s1 to s8
sfile = [] # sfile is the switch config file name
for i in range(1, 18):
    sfile.append("../runtime-basic/s"+str(i)+"-runtime.json")


# init a dict for the switches to build config files
config = {}

# to avoid generate table entry repeatly, we define a flag dict for checking already generated entries
checker = {}

# we generate default entry for all 3 tables including SFC, NF and IPv4 table
defaultSFC = generateDefaultEntry("MyIngress.safeme_sfc", "MyIngress.myNoAction", {})
defaultNF = generateDefaultEntry("MyIngress.safeme_nf", "MyIngress.drop", {})
defaultIPv4 = generateDefaultEntry("MyIngress.ipv4_lpm", "MyIngress.drop", {})

for i in range(1, 18):
    sw = "s"+str(i)
    config[sw] = {} # init each switch config dict
    config[sw]["target"] = "bmv2"
    config[sw]["p4info"] = "build/basic.p4.p4info.txt"
    config[sw]["bmv2_json"] = "build/basic.json"
    config[sw]["table_entries"] = [] # default table entries is empty list
    config[sw]["table_entries"].append(defaultIPv4)
    checker[sw] = {}

#print json.dumps(config)

# for each route in the table, if src is a host and destination is a host
# we add a normal ipv4 route without any SFC and NF control
for route in routes:
    l = len(route)
    startNode = route[0]
    endNode = route[l-1]
    if startNode[0:1] == "h" and endNode[0:1] == "h":
        # we only consider two host pair ipv4 route deployment
        dstip = base["hosts"][endNode]["ip"]
        srcip = base["hosts"][startNode]["ip"]
        for j in range(0, l-1):
            curNode = route[j]
            nextNode = route[j+1]
            if nextNode[0:1] == "s":
                nextMac = base["switches"][nextNode]["mac"]
            elif nextNode[0:1] == "h":
                nextMac = base["hosts"][nextNode]["mac"]
            if curNode[0:1] == "s": # if this node is a switch
                if not dstip in checker[curNode]:
                    match = {}
                    match["hdr.ipv4.dstAddr"] = [dstip, 32]
                    action_params = {}
                    action_params["dstAddr"] = nextMac
                    action_params["port"] = egress[curNode][nextNode]
                    newIPv4Entry = generateTableEntry("MyIngress.ipv4_lpm", match, "MyIngress.ipv4_forward", action_params)
                    config[curNode]["table_entries"].append(newIPv4Entry)
                    checker[curNode][dstip] = 1

#print json.dumps(config)
for i in range(0, 17):
    fp = open(sfile[i], "w")
    json.dump(config["s"+str(i+1)], fp)
    fp.close()


