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
    sfile.append("../runtime-PDA/s"+str(i)+"-runtime.json")


# init a dict for the switches to build config files
config = {}

# to avoid generate table entry repeatly, we define a flag dict for checking already generated entries
checker = {}

# we generate default entry for all 3 tables including SFC, NF and IPv4 table
#defaultSFC = generateDefaultEntry("MyIngress.safeme_sfc", "MyIngress.myNoAction", {})
#defaultNF = generateDefaultEntry("MyIngress.safeme_nf", "MyIngress.drop", {})
#defaultIPv4 = generateDefaultEntry("MyIngress.ipv4_lpm", "MyIngress.drop", {})

# we generate default entry for all 2 tables including Inport table and IPv4 table
defaultInport = generateDefaultEntry("MyIngress.inport_lpm", "MyIngress.myNoAction", {})
defaultIPv4 = generateDefaultEntry("MyIngress.ipv4_lpm", "MyIngress.drop", {})

for i in range(1, 18):
    sw = "s"+str(i)
    config[sw] = {} # init each switch config dict
    config[sw]["target"] = "bmv2"
    config[sw]["p4info"] = "build/pda.p4.p4info.txt"
    config[sw]["bmv2_json"] = "build/pda.json"
    config[sw]["table_entries"] = [] # default table entries is empty list
    config[sw]["table_entries"].append(defaultInport)
    config[sw]["table_entries"].append(defaultIPv4)
    checker[sw] = {}

#print json.dumps(config)

# for PDA, first we load SFC rules from json file
# then we change the route for the host pair from the routes array to meet the requirement of SFC 

# for each route in the table, if src is a host and destination is a host
# we add a normal ipv4 route without any SFC and NF control
routes2 = {}
for route in routes:
    l = len(route)
    startNode = route[0]
    endNode = route[l-1]
    # build another route dict for PDA to use
    if not startNode in routes2:
        routes2[startNode] = {}
    routes2[startNode][endNode] = route
    # build ipv4 route for each host pair
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
                    newIPv4Entry = generateTableEntry("MyIngress.ipv4_lpm", match, "MyIngress.ipv4_forward2", action_params)
                    config[curNode]["table_entries"].append(newIPv4Entry)
                    checker[curNode][dstip] = 1

# load VNF config and SFC rule config
nf_conf_file = open("../runtime-PDA/NFmapping.json", "r")
nf_conf = json.load(nf_conf_file)
nf_conf_file.close()

sfc_file = open("../runtime-PDA/sfcRules.json", "r")
sfc_rules0 = json.load(sfc_file)
sfc_file.close()

# build safeme rules from sfc_rules array
# first we translate Fx, Ix, Px NF
sfc_rules = []
for rule0 in sfc_rules0:
    rule = []
    for node in rule0:
        if node[0:1] == "F" or node[0:1] == "I" or node[0:1] == "P":
            rule.append(nf_conf[node])
        else:
            rule.append(node)
    sfc_rules.append(rule)

# then we build PDA rules based on INPORT to identify the path through NFs
for rule in sfc_rules:
    # build a single rule, add config to switches
    # for a path, we should deploy inport based routing for each switch and NF node
    nodeNum = len(rule)
    srchost = rule[0]
    dsthost = rule[nodeNum-1]
    # we find each route segment from host to 1st NF, 1st NF to 2nd NF, and so on
    for i in range(0, nodeNum-1):
        path = routes2[rule[i]][rule[i+1]]
        #print path
        plen = len(path)
        startNode = path[0]
        endNode = path[plen -1]
        startIndex = 1 # 0 means host or NF, because every segment started with a host or a NF, host needs no rules to be deployed, NF rule has been deployed in the last node for the previous loop
        endIndex = plen - 1
        if endNode[0:1] == "h": # means the last segment ends with dst host from last NF, we no need deploy rules for host, so end index should stop at plen-2
            endIndex = plen - 2
        # do rules generation for inport based PDA routing
        for j in range(1, endIndex + 1):
            inport = egress[path[j]][path[j-1]]
            # if last node is NF, then outport will be inport
            if j == endIndex and j == plen-2 and path[j+1][0:1] == "h": # this indicates last node and it is the dst host
                outport = egress[path[j]][path[j+1]]
                dstmac = base["hosts"][path[j+1]]["mac"]
            elif j == endIndex and path[j][0:1] == "s": # this indicates last node and it is a NF
                outport = inport
                dstmac = base["switches"][path[j-1]]["mac"]
            else:
                outport = egress[path[j]][path[j+1]]
                dstmac = base["switches"][path[j+1]]["mac"]
            # build inport based entry for SFC
            currentSwitch = path[j]
            match = {}
            match["standard_metadata.ingress_port"] = inport
            match["hdr.ipv4.dstAddr"] = [base["hosts"][dsthost]["ip"], 32]
            action_params = {}
            action_params["dstAddr"] = dstmac
            action_params["port"] = outport
            newInportEntry = generateTableEntry("MyIngress.inport_lpm", match, "MyIngress.ipv4_forward", action_params)
            config[currentSwitch]["table_entries"].append(newInportEntry)

#print json.dumps(config)
for i in range(0, 17):
    fp = open(sfile[i], "w")
    json.dump(config["s"+str(i+1)], fp)
    fp.close()


