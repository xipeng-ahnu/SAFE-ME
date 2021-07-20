#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 22 17:39:33 2018

@author: gejuncheng
"""

from algorithms import dijkstra
from algorithms import dijkstra2
from algorithms import dijkstra3
from graph_for_l2 import DiGraph
from time import sleep
CODEC = 'utf-8'
mynet = "rocketfuel_87s174h50nf.json"
defualt_path = 'data/defualt_path.txt'
file=open(defualt_path,'w')
g = DiGraph(mynet)
#Input switch, host, VNF name
switch = []
host = []
vnf = []
for i in range(0,87):
    s="s"+str(i+1)
    switch.append(s)
for i in range(0,174):
    h="h"+str(i+1)
    host.append(h)
for i in range(0,10):
    F="F"+str(i+1)
    vnf.append(F)
for i in range(0,10):
    I="I"+str(i+1)
    vnf.append(I)
for i in range(0,10):
    P="P"+str(i+1)
    vnf.append(P)
for i in range(0,10):
    D="D"+str(i+1)
    vnf.append(D)
for i in range(0,10):
    W="W"+str(i+1)
    vnf.append(W)
times = 0
for i in switch:
    print i
    for j in vnf:
        #print j
        path = dijkstra(g, i, j)
        main_path = path.get('path')
        main_cost = path.get('cost')
        file.write(str(main_path) + '\n')
        times +=1
        #print (main_path)
        #sleep(30)
    for k in host:
        path = dijkstra(g,i,k)
        main_path = path.get('path')
        #for i in range(0,len(main_path)):
        #    main_path[i] = main_path[i].encode(CODEC)
         #   print "main_path",main_path[i]
        file.write(str(main_path) + '\n')
        times += 1
print times,"Finished"


