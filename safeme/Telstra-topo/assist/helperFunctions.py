#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon May 25 18:45:05 2021
@author: xipeng

"""

#import json

def generateDefaultEntry(tableName = None, actionName = None, actionParam = None):
    result = {}
    if tableName == None or type(tableName) != str:
        return None
    if actionName == None or type(actionName) != str:
        return None
    if actionParam == None or type(actionParam) != dict:
        return None
    result["table"] = tableName
    result["default_action"] = True
    result["action_name"] = actionName
    result["action_params"] = actionParam
    return result
'''
ff = open("test.json", "w")
json.dump(generateDefaultEntry("MyIngress.safeme_sfc", "MyIngress.myNoAction", {}), ff) 
'''

def generateTableEntry(tableName = None, match = None, actionName = None, actionParam = None):
    result = {}
    if tableName == None or type(tableName) != str:
        return None
    if tableName == None or type(match) != dict:
        return None
    if actionName == None or type(actionName) != str:
        return None
    if actionParam == None or type(actionParam) != dict:
        return None
    result["table"] = tableName
    result["match"] = match
    result["action_name"] = actionName
    result["action_params"] = actionParam
    return result

'''
ff = open("test.json", "w")
match = {}
match["hdr.ipv4.srcAddr"]="10.0.1.1"
match["hdr.ipv4.dstAddr"]= ["10.0.2.0", 24]

action = {}
action["sTag"] = 2
action["mTag"] = 1
json.dump(generateTableEntry("MyIngress.safeme_sfc", match, "MyIngress.safeme_addtag", action), ff) 
'''
