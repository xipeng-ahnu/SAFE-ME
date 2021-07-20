#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 22 17:39:33 2018
Revised on Mon May 24 21:30:03 2021
@author: gejuncheng
@editor: xipeng
"""

from algorithms import dijkstra
from algorithms import dijkstra2
from algorithms import dijkstra3
from graph_for_l2 import DiGraph
from time import sleep
import json
CODEC = 'utf-8'
mynet = "8s9vnf.json"
defualt_path = 'data/default_path_for_switch.txt'
file=open(defualt_path,'w')
g = DiGraph(mynet)
#Input switch, host, VNF name
switch = []
host = []
vnf = []
for i in range(0,8):
    s="s"+str(i+1)
    switch.append(s)
#for i in range(0,8):
#    h="h"+str(i+1)
#    host.append(h)
host.append("h11")
host.append("h12")
host.append("h21")
host.append("h22")
host.append("h31")
host.append("h32")
host.append("h41")
host.append("h42")
host.append("h51")
host.append("h52")
host.append("h61")
host.append("h62")
host.append("h71")
host.append("h72")
host.append("h81")
host.append("h82")

for i in range(0,3):
    F="F"+str(i+1)
    vnf.append(F)
for i in range(0,3):
    I="I"+str(i+1)
    vnf.append(I)
for i in range(0,3):
    P="P"+str(i+1)
    vnf.append(P)

times = 0
results = []
for i in switch:
    #print i
    for j in vnf:
        #print j
        path = dijkstra(g, i, j)
        main_path = path.get('path')
        main_cost = path.get('cost')
        #file.write(str(main_path) + '\n')
        results.append(main_path)
        times +=1
        #print (main_path)
        #sleep(30)
    for k in host:
        path = dijkstra(g,i,k)
        main_path = path.get('path')
        #for i in range(0,len(main_path)):
        #    main_path[i] = main_path[i].encode(CODEC)
         #   print "main_path",main_path[i]
        #file.write(str(main_path) + '\n')
        results.append(main_path)
        times += 1

json.dump(results, file)
print times,"Finished"


