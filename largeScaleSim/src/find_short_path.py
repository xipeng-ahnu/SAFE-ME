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
CODEC = 'utf-8'
mynet = "8s9vnf.json"
defualt_path = 'data/defualt_path.txt'
file=open(defualt_path,'w')
g = DiGraph(mynet)
#输入交换机，主机，VNF名称
switch = ['s1','s2','s3','s4','s5','s6','s7','s8']
host = ['h10','h11','h12','h13','h14','h15','h16','h17','h18','h19','h20','h21','h22','h23','h24','h25','h26','h27','h28','h29','h30','h31','h32','h33','h34','h35','h36','h37','h38','h39','h40','h41','h42','h43','h44','h45','h46','h47','h48','h49','h50','h51','h52','h53','h54','h55','h56','h57','h58','h59','h60','h61','h62','h63','h64','h65','h66','h67','h68','h69','h70','h71','h72','h73','h74','h75','h76','h77','h78','h79','h80','h81','h82','h83','h84','h85','h86','h87','h88','h89']
vnf = ['F1','F2','F3','I1','I2','I3','P1','P2','P3']
times = 0
for i in switch:
    for j in vnf:
        path = dijkstra(g, i, j)
        main_path = path.get('path')
        main_cost = path.get('cost')
        file.write(str(main_path) + '\n')
        times +=1
        #print (main_cost)
    for k in host:
        path = dijkstra(g,i,k)
        main_path = path.get('path')
        #for i in range(0,len(main_path)):
        #    main_path[i] = main_path[i].encode(CODEC)
         #   print "main_path",main_path[i]
        file.write(str(main_path) + '\n')
        times += 1
print times,"Finished"


