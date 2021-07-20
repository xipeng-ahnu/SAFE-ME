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
    sfile.append("../runtime-safeme/s"+str(i)+"-runtime.json")


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
    config[sw]["p4info"] = "build/safeme.p4.p4info.txt"
    config[sw]["bmv2_json"] = "build/safeme.json"
    config[sw]["table_entries"] = [] # default table entries is empty list
    config[sw]["table_entries"].append(defaultSFC)
    config[sw]["table_entries"].append(defaultNF)
    config[sw]["table_entries"].append(defaultIPv4)
    checker[sw] = {}

#print json.dumps(config)

# for each route in the table, if src is a host and destination is a host
# we add a normal ipv4 route without any SFC and NF control
routes2 = {}
for route in routes:
    l = len(route)
    startNode = route[0]
    endNode = route[l-1]
    # build another route dict for safeme to use
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
                    newIPv4Entry = generateTableEntry("MyIngress.ipv4_lpm", match, "MyIngress.ipv4_forward", action_params)
                    config[curNode]["table_entries"].append(newIPv4Entry)
                    checker[curNode][dstip] = 1

# load VNF config and SFC rule config
nf_conf_file = open("../runtime-safeme/NFmapping.json", "r")
nf_conf = json.load(nf_conf_file)
nf_conf_file.close()

sfc_file = open("../runtime-safeme/sfcRules.json", "r")
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

# then we build sfc rules here
for rule in sfc_rules:
    # build a single rule, add config to switches
    # for a path, we should find out the ingress switch to add sfc rules
    # and the egress switch for the destination to remove the sfc rules
    nodeNum = len(rule)
    srchost = rule[0]
    dsthost = rule[nodeNum-1]
    # we should generate tags for each NF
    # tags store the current tag sequence from the first NF as tags[0] to last NF as tags[len(tags)-1]
    tags = []
    for i in range(1, nodeNum-1):
        tags.append(int(nf_conf[rule[i]]))
    tagLen = len(tags) 
    for i in range(0, nodeNum-1):
        # find each segment path from host to 1st NF, 1st NF to 2nd NF, etc
        path = routes2[rule[i]][rule[i+1]]
        plen = len(path)
        startNode = path[0]
        endNode = path[plen -1]        
        if startNode[0:1] == "h": # this means the first segment
            starthost = startNode
            ingressSwitch = path[1]
            lastSwitchToNF = path[plen-2]
            currentNF = path[plen-1]
            # we build ingress SFC table rules
            match = {}           
            #match["hdr.ipv4.srcAddr"] = [base["hosts"][srchost]["ip"][0:base["hosts"][srchost]["ip"].rfind(".")]+".0", 24]
            match["hdr.ipv4.srcAddr"] = [base["hosts"][srchost]["ip"], 32]
            match["hdr.ipv4.dstAddr"] = base["hosts"][dsthost]["ip"] 
            action_params = {}
            sTag = 0;
            for j in range(tagLen-1, 0, -1):
                sTag = sTag * 256 + tags[j]            
            action_params["sTag"] = sTag
            action_params["mTag"] = tags[0]
            newSFCEntry = generateTableEntry("MyIngress.safeme_sfc", match, "MyIngress.safeme_addtag", action_params)
            config[ingressSwitch]["table_entries"].append(newSFCEntry)
            # then we build tag shift nf rules for the closest switch to the NF
            match2 = {}           
            match2["hdr.safeme.tagMatchField"] = int(nf_conf[endNode])
            match2["hdr.ipv4.dstAddr"] = [base["hosts"][dsthost]["ip"][0:base["hosts"][dsthost]["ip"].find(".")]+".0.0.0", 8] 
            action_params2 = {}           
            action_params2["dstAddr"] = base["switches"][currentNF]["mac"]
            action_params2["port"] = egress[lastSwitchToNF][currentNF]
            newNFEntry2 = generateTableEntry("MyIngress.safeme_nf", match2, "MyIngress.safeme_shift_forward", action_params2)
            config[lastSwitchToNF]["table_entries"].append(newNFEntry2)
            # then for each other intermediate switch to the NF, we just do NF tag based forwarding by add a nf rule
            for k in range(1, plen-2): # here from index 1 means ignore the src host
                match3 = {}           
                match3["hdr.safeme.tagMatchField"] = int(nf_conf[endNode])
                match3["hdr.ipv4.dstAddr"] = [base["hosts"][dsthost]["ip"][0:base["hosts"][dsthost]["ip"].find(".")]+".0.0.0", 8] 
                action_params3 = {}           
                action_params3["dstAddr"] = base["switches"][path[k+1]]["mac"]
                action_params3["port"] = egress[path[k]][path[k+1]]
                newNFEntry3 = generateTableEntry("MyIngress.safeme_nf", match3, "MyIngress.safeme_normal_forward", action_params3)
                config[path[k]]["table_entries"].append(newNFEntry3) 
                    
        elif endNode[0:1] == "h": # this means the last segment
            lastSwitchToDst = path[plen-2]
            # we first build tag remove nf rule for the closest switch to the dst host
            match = {}           
            match["hdr.safeme.tagMatchField"] = 0
            match["hdr.ipv4.dstAddr"] = [base["hosts"][dsthost]["ip"], 32] 
            action_params = {}           
            action_params["dstAddr"] = base["hosts"][dsthost]["mac"]
            action_params["port"] = egress[lastSwitchToDst][dsthost]
            newNFEntry = generateTableEntry("MyIngress.safeme_nf", match, "MyIngress.safeme_removetag", action_params)
            config[lastSwitchToDst]["table_entries"].append(newNFEntry)
            # then we build tag 0 nf rule for the intermediate switches to forwarding
            for k in range(0, plen-2):
                match2 = {}           
                match2["hdr.safeme.tagMatchField"] = 0
                match2["hdr.ipv4.dstAddr"] = [base["hosts"][dsthost]["ip"], 32] 
                action_params2 = {}           
                action_params2["dstAddr"] = base["switches"][path[k+1]]["mac"]
                action_params2["port"] = egress[path[k]][path[k+1]]
                newNFEntry2 = generateTableEntry("MyIngress.safeme_nf", match2, "MyIngress.safeme_normal_forward", action_params2)
                config[path[k]]["table_entries"].append(newNFEntry2)

        else: # this means the intermediate segment
            lastSwitchToNF = path[plen-2]
            currentNF = path[plen-1]
            # we first build tag shift nf rules for the closest switch to the NF
            match = {}           
            match["hdr.safeme.tagMatchField"] = int(nf_conf[endNode])
            match["hdr.ipv4.dstAddr"] = [base["hosts"][dsthost]["ip"][0:base["hosts"][dsthost]["ip"].find(".")]+".0.0.0", 8] 
            action_params = {}           
            action_params["dstAddr"] = base["switches"][currentNF]["mac"]
            action_params["port"] = egress[lastSwitchToNF][currentNF]
            newNFEntry = generateTableEntry("MyIngress.safeme_nf", match, "MyIngress.safeme_shift_forward", action_params)
            config[lastSwitchToNF]["table_entries"].append(newNFEntry) 
            # then for each other intermediate switch to the NF, we just do NF tag based forwarding by add a nf rule
            for k in range(0, plen-2):
                match2 = {}           
                match2["hdr.safeme.tagMatchField"] = int(nf_conf[endNode])
                match2["hdr.ipv4.dstAddr"] = [base["hosts"][dsthost]["ip"][0:base["hosts"][dsthost]["ip"].find(".")]+".0.0.0", 8] 
                action_params2 = {}           
                action_params2["dstAddr"] = base["switches"][path[k+1]]["mac"]
                action_params2["port"] = egress[path[k]][path[k+1]]
                newNFEntry2 = generateTableEntry("MyIngress.safeme_nf", match2, "MyIngress.safeme_normal_forward", action_params2)
                config[path[k]]["table_entries"].append(newNFEntry2) 



#print json.dumps(config)
for i in range(0, 17):
    fp = open(sfile[i], "w")
    json.dump(config["s"+str(i+1)], fp)
    fp.close()
