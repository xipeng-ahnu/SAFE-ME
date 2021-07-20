#coding=utf-8
from pulp import *
from algorithms import dijkstra
from algorithms import dijkstra2
from algorithms import dijkstra3
#from operator import itemgetter
#from prioritydictionary import priorityDictionary
from graph_for_l2 import DiGraph
from collections import defaultdict
import json
import random
import os
from time import sleep
#import math
CODEC = 'utf-8'
mynet = "8s9vnf.json"
g = DiGraph(mynet)
def txt_wrap_by(start_str, end_str, html,start):
    
    keyvaule=[]
    while start <=len(html):
        start = html.find(start_str,start)
        if start >= 0:
            start += len(start_str)
            end = html.find(end_str, start)
            if end >= 0:
                keyvaule.append(html[start:end].strip())                
                start = end + len(end_str)
        else:
            return keyvaule

def get_route_alg1 (file_path):
    all_node = []
    all_node_alone = []    
    all_edge = []    
    all_edge_alone = []
    all_edge_alone_order = []
    one_edge = []
    one_edge1 = []
    one_edge_order = []
    one_node = []
    source = []
    terminal = []
    weight = []
    fd=file_path+'/alg1_path_segment.txt'
    if os.path.exists(fd):
        os.remove(fd)
    fd=file_path+'/alg2_path_segment.txt'
    if os.path.exists(fd):
        os.remove(fd)    
    fd=file_path+'/alg1_path.txt'
    if os.path.exists(fd):
        os.remove(fd)    
    fd=file_path+'/alg2_path.txt'
    if os.path.exists(fd):
        os.remove(fd)        
    fd=file_path+'/flows.txt'
    if os.path.exists(fd):
        os.remove(fd)    
    fd=file_path+'/paths.txt'
    if os.path.exists(fd):
        os.remove(fd)
    for line in open(file_path+"/flow_vnf.txt"):
        flow_path=txt_wrap_by("'","'",line,0)
        #print flow_path,flow_path[0]
        for i in range(0,len(flow_path)-2):
            #print flow_path[i],flow_path[i+1]
            source.append(flow_path[i])
            terminal.append(flow_path[i+1])
            weight.append(flow_path[len(flow_path)-1])
    # The above is to randomly generate the stream and the stream bandwidth, that is, generate soure[], terminal[], weight[], as the input of the next part of the code routing.
    flow_number = len(source)
    print "flow_number",flow_number
    for sr in range (0,flow_number):
        if sr%1000 == 0:
            print"source is ",sr,source[sr], terminal[sr]
        main_path_all = []
        one_source_edge = []
        one_source_edge_order = []
        one_source_node = []
        path = dijkstra(g, source[sr], terminal[sr])
        main_path = path.get('path')
        for i in range(0,len(main_path)):
            main_path[i] = main_path[i].encode(CODEC)
            main_path_all.append(main_path[i])
        for f in range(0,len(main_path)-3):
            siwtch1 = int(main_path[f+1][1])
            siwtch2 = int(main_path[f+2][1])
            one_edge_order = main_path[f+1] + main_path[f+2]       
            if len(main_path[f+1]) == 3:
                siwtch1 = siwtch1*10 + int(main_path[f+1][2])
            if len(main_path[f+1]) == 4:
                siwtch1 = siwtch1*100 + int(main_path[f+1][2])*10 + int(main_path[f+1][3])
            if len(main_path[f+2]) == 3:
                siwtch2 = siwtch2*10 + int(main_path[f+2][2])
            if len(main_path[f+2]) == 4:
                siwtch2 = siwtch2*100 + int(main_path[f+2][2])*10 + int(main_path[f+2][3])
            if siwtch1 < siwtch2:
                one_edge = main_path[f+1] + main_path[f+2]
                one_edge1 = main_path[f+2] + main_path[f+1]
            else:
                one_edge = main_path[f+2] + main_path[f+1]
                one_edge1 = main_path[f+1] + main_path[f+2]
            if one_edge not in all_edge:
                if one_edge1 not in all_edge:
                    all_edge.append(one_edge)
                else:
                    one_edge = one_edge1
            one_source_edge.append(one_edge)
            one_source_edge_order.append(one_edge_order)
        all_edge_alone.append(one_source_edge)
        all_edge_alone_order.append(one_source_edge_order)
        for f in range(0,len(main_path)-2):
            one_node = main_path[f+1]
            if one_node not in all_node:
                all_node.append(one_node)
            one_source_node.append(one_node)
        all_node_alone.append(one_source_node)
        one_source_edge_order = []
        one_source_node = []
        one_source_edge = []
        path = dijkstra2(g, source[sr], terminal[sr],main_path_all)
        main_path = path.get('path')
        for i in range(0,len(main_path)):
            main_path[i] = main_path[i].encode(CODEC)
            main_path_all.append(main_path[i])
        for f in range(0,len(main_path)-3):
            siwtch1 = int(main_path[f+1][1])
            siwtch2 = int(main_path[f+2][1])
            one_edge_order = main_path[f+1] + main_path[f+2]
            if len(main_path[f+1]) == 3:
                siwtch1 = siwtch1*10 + int(main_path[f+1][2])
            if len(main_path[f+1]) == 4:
                siwtch1 = siwtch1*100 + int(main_path[f+1][2])*10 + int(main_path[f+1][3])
            if len(main_path[f+2]) == 3:
                siwtch2 = siwtch2*10 + int(main_path[f+2][2])
            if len(main_path[f+2]) == 4:
                siwtch2 = siwtch2*100 + int(main_path[f+2][2])*10 + int(main_path[f+2][3])
            if siwtch1 < siwtch2:
                one_edge = main_path[f+1] + main_path[f+2]
                one_edge1 = main_path[f+2] + main_path[f+1]
            else:
                one_edge = main_path[f+2] + main_path[f+1]
                one_edge1 = main_path[f+1] + main_path[f+2]
            if one_edge not in all_edge:
                if one_edge1 not in all_edge:
                    all_edge.append(one_edge)
                else:
                    one_edge = one_edge1
            one_source_edge.append(one_edge)
            one_source_edge_order.append(one_edge_order)
        all_edge_alone.append(one_source_edge)
        all_edge_alone_order.append(one_source_edge_order)
        for f in range(0,len(main_path)-2):
            one_node = main_path[f+1]
            if one_node not in all_node:
                all_node.append(one_node)
            one_source_node.append(one_node)
        all_node_alone.append(one_source_node)
        one_source_node = []
        one_source_edge = []
        one_source_edge_order = []
        path = dijkstra3(g, source[sr], terminal[sr],main_path_all)
        main_path = path.get('path')
        for i in range(0,len(main_path)):
            main_path[i] = main_path[i].encode(CODEC)
            main_path_all.append(main_path[i])
        for f in range(0,len(main_path)-3):
            siwtch1 = int(main_path[f+1][1])
            siwtch2 = int(main_path[f+2][1])
            one_edge_order = main_path[f+1] + main_path[f+2]
            if len(main_path[f+1]) == 3:
                siwtch1 = siwtch1*10 + int(main_path[f+1][2])
            if len(main_path[f+1]) == 4:
                siwtch1 = siwtch1*100 + int(main_path[f+1][2])*10 + int(main_path[f+1][3])
            if len(main_path[f+2]) == 3:
                siwtch2 = siwtch2*10 + int(main_path[f+2][2])
            if len(main_path[f+2]) == 4:
                siwtch2 = siwtch2*100 + int(main_path[f+2][2])*10 + int(main_path[f+2][3])
            if siwtch1 < siwtch2:
                one_edge = main_path[f+1] + main_path[f+2]
                one_edge1 = main_path[f+2] + main_path[f+1]
            else:
                one_edge = main_path[f+2] + main_path[f+1]
                one_edge1 = main_path[f+1] + main_path[f+2]
            if one_edge not in all_edge:
                if one_edge1 not in all_edge:
                    all_edge.append(one_edge)
                else:
                    one_edge = one_edge1
            one_source_edge.append(one_edge)
            one_source_edge_order.append(one_edge_order)
        all_edge_alone.append(one_source_edge)
        all_edge_alone_order.append(one_source_edge_order)
        for f in range(0,len(main_path)-2):
            one_node = main_path[f+1]
            if one_node not in all_node:
                all_node.append(one_node)
            one_source_node.append(one_node)
        all_node_alone.append(one_source_node)
        weight [sr] = int (weight[sr])
    for flow_traffic in range(1,2):
        alg0=0
        alg1=0
        alg2=0
        alg3=0
        for randome_time in range(0,1):
            for entries in range(31,32):             #300-4200
                entries = entries *10000
              
                ce = 10000
                #print entries
                for alg in range(0,1):
                    if alg == 0:  
                        x_e = defaultdict(lambda:(defaultdict(lambda:(defaultdict(lambda:None)))))
                        x_v = defaultdict(lambda:(defaultdict(lambda:(defaultdict(lambda:None)))))
                        x = [[0 for col in range(3)] for row in range(flow_number)] #3 is the number of path that each flow can choose
                        for i in range(0,flow_number):
                            for j in range(0,3):          #3 is the number of path that each flow can choose
                                x[i][j] = "x"
                                if flow_number < 100000:
                                    if i < 10:
                                        x[i][j] = x[i][j] + "0000"
                                    elif i < 100:
                                        x[i][j] = x[i][j] + "000"
                                    elif i < 1000:
                                        x[i][j] = x[i][j] + "00"
                                    elif i < 10000:
                                        x[i][j] = x[i][j] + "0"
                                x[i][j] = x[i][j] + str(i) + str(j)
            
                        z = []
                        for i in range(0,flow_number):
                            z.append("z"+str(i))
            
                        temp = []
                        for i in range(0,flow_number):
                            for j in range(0,3):              #3 si the number of path that each flow can choose
                                temp.append(x[i][j])
                        for i in range(0,flow_number):
                            temp.append(z[i])
                        prob = LpProblem('lptest', LpMinimize)
                        r = LpVariable('r', lowBound = 0)
                        xx = LpVariable.dicts("",temp, lowBound = 0,upBound = 1)
                        prob += r
                        for i in range(0,flow_number):
                            prob += lpSum([xx[j] for j in x[i]]) == xx[z[i]]       #that means, x[i][0]+x[i][1]....+x[i][len(x[i])-1] = 1
                            prob += xx[z[i]] == 1
                        print  "len(all_edge_alone)",len(all_edge_alone)
                        for i in range(0,len(all_edge_alone)):
                            for j in range(0,len(all_edge_alone[i])):           #for example, all_edge_alone[i][j] = v1v2
                                length_x_e = len( x_e[all_edge_alone[i][j]])
                                #print "length_x_e",length_x_e,all_edge_alone[i],all_edge_alone[i][j],i,j
                                x_e[all_edge_alone[i][j]][length_x_e][0] = x[i/3][i%3]
                                x_e[all_edge_alone[i][j]][length_x_e][1] = weight[i/3]
                        print"222"
                        for h in all_edge:
                            prob += lpSum(x_e[h][i][1]*xx[x_e[h][i][0]] for i in x_e[h]) <= ce*r
                        for i in range(0,len(all_node_alone)):
                            for j in range(0,len(all_node_alone[i])):
                                length_x_v = len( x_v[all_node_alone[i][j]])
                                if i%3 == 0:
                                    x_v[all_node_alone[i][j]][length_x_v][1] = 0  #choose dijstra path do not need extra entries
                                    x_v[all_node_alone[i][j]][length_x_v][0] = x[i/3][i%3] 
                                else:
                                    x_v[all_node_alone[i][j]][length_x_v][0] = x[i/3][i%3]
                                    if j == len(all_node_alone[i])-1:
                                        x_v[all_node_alone[i][j]][length_x_v][1] = 0 #the last hop do not need extra entries
                                    else:                 
                                        x_v[all_node_alone[i][j]][length_x_v][1] = 1
                        print"333"
                        for v in all_node:
                            prob += lpSum(x_v[v][i][1]*xx[x_v[v][i][0]] for i in x_v[v]) <= entries
                        GLPK().solve(prob)
                        print 'objective_sr =', value(prob.objective)
                        p1 = file_path+"/alg0.json"
                        fd = open(p1, 'w')
                        fd.write(json.dumps(value(prob.objective)))
                        fd.close()
                        i=0
                        j=0
                        l=0
                        for v in prob.variables():
                            l =l +1
                            if l<flow_number*3+1:  #(the number of flows /cdot 3) +1
                                x[i][j]=v.varValue
                                if j<2:
                                    j =j+1
                                else:
                                    i=i+1
                                    j=0
                        lambda1 = 0
                        used_ce = defaultdict(lambda:None)
                        for e in all_edge:
                            used_ce[e] = 0 
                                
                        flows_add = {}                   
                        for i in range(0,flow_number):
                            k=0
                            choose=0
                            choosed_path = []
    
                            for j in range(0,3):
                                if x[i][j]>=k:
                                    choose=j
                                    k=x[i][j]
                            for n in range(0,len(all_edge_alone[3*i+choose])):
                                    used_ce[all_edge_alone[3*i+choose][n]] = used_ce[all_edge_alone[3*i+choose][n]] + weight[i]
                                    if used_ce[all_edge_alone[3*i+choose][n]]/float(ce) > lambda1:
                                        lambda1 = used_ce[all_edge_alone[3*i+choose][n]]/float(ce)
                            choosed_path.append(source[i])
                            for j in range (0,len(all_node_alone[3*i+choose])):
                                choosed_path.append(all_node_alone[3*i+choose][j])
                            choosed_path.append(terminal[i])
                            choosed_path.append(str(weight[i]))
                            fd=open(file_path+'/alg1_path_segment.txt','a') 
                            fd.write(str(choosed_path) + '\n')
                            fd.close()
                            num_add_flow = 0
                            for key in range(0,len(all_edge_alone_order[3*i+choose])):
                                if all_edge_alone_order[3 * i + choose][key] not in all_edge_alone_order[3*i]:
                                    #['v2v9', 'v9v7', 'v7v1']->['', '2', '9']['', '9', '7']['', '7', '1']
                                    add_flow_key = str(all_edge_alone_order[3 * i + choose][key]).split('s')
                                    for num_i in range(0,3):
                                        add_flow_key[num_i] = 's'+str(add_flow_key[num_i])
                                    #print add_flow_key[1]
                                    #If the node is not in the dictionary, vi=1, if the dictionary is in the dictionary, flows_add[vi] = flows_add[vi]+1
                                    if add_flow_key[1] not in flows_add:
                                        flows_add[add_flow_key[1]] = 1
                                    else:
                                        flows_add[add_flow_key[1]] = flows_add[add_flow_key[1]]+1
                                    #print add_flow_key
                        #print "-------------->",all_node
                        for key_all in all_node:
                            if key_all not in flows_add:
                                flows_add[key_all] = 0
                                
                        p11 = file_path+"/alg1_entries.json"  # rounding
                        fd = open(p11, 'w')
                        fd.write(json.dumps(flows_add,indent=1))
                        fd.close()
                        
                        alg1_max_entries=0
                        for j in flows_add:
                            if alg1_max_entries < flows_add[j]:
                                alg1_max_entries = flows_add[j]
                        p11 = file_path+"/alg1_max_entries.json"  # rounding
                        fd = open(p11, 'w')
                        fd.write(json.dumps(alg1_max_entries))
                        fd.close()
                        file_object = open(file_path+'/alg1_path_segment.txt')
                        try:
                            data = file_object.read( )
                        finally:
                            file_object.close( )
                        print "data",data
                        data = data.replace("]","],")
                        data_len = len(data)-2
                        data = '['+data[:data_len]+']'
                        data_list = list(eval(data))
                        print "data_list",data_list,len(data_list)
                        stack = []
                        new_path = []
                        for i in range(0,len(data_list)):
                            if len(stack) == 0:
                                stack.append(data_list[i])
                            else:
                                if 'h' not in data_list[i][len(data_list[i])-2]:
                                    stack.append(data_list[i])
                                else:
                                    #If the last host is found, merge this link
                                    this_path = []
                                    for len_stack in range(0,len(stack)):
                                        a = stack.pop()
                                        this_path.append(a)
                                    one_path = []
                                    #print this_path
                                    for t in range(0,len(this_path)):
                                        index = len(this_path) -t-1
                                        #If it is the last list of this path, take the first four values
                                        if index == (len(this_path)-1):
                                            for w in range(0,(len(this_path[index])-1)):
                                                one_path.append(this_path[index][w])
                                        else:
                                            for w in range(1,(len(this_path[index])-1)):
                                                one_path.append(this_path[index][w])
                                    for w in range(1, len(data_list[i]) ):
                                        one_path.append(data_list[i][w])
                                    print "one_path",one_path
                                    fd = open(file_path+'/alg1_path.txt', 'a')
                                    fd.write(str(one_path) + '\n')
                                    fd.close()
                        p1 = file_path+"/alg1_ce.json"  #rounding
                        fd = open(p1, 'w')
                        alg1_ce = {}
                        for e in all_edge:
                            alg1_ce[e] = float(used_ce[e])/float(ce)
                        fd.write(json.dumps(alg1_ce, indent=1))
                        fd.close()
    
                        print lambda1  
                        p1 = file_path+"/alg1_lambda.json"  #rounding
                        fd = open(p1, 'w')
                        fd.write(json.dumps(lambda1))
                        fd.close()    
    
    
                        
                    if alg == 2:  #heuristic algorithm ,ospf need entries
                        used_ce = defaultdict(lambda:None)
                        used_entries  = defaultdict(lambda:None)
                        for v in all_node:
                            used_entries[v] = 0
                        for e in all_edge:
                            used_ce[e] = 0
                        lambda1 = 0
                        temp2 = 0
                        for i in range(0,flow_number):
                            temp = [[0 for col in range(2)] for row in range(3)]
                            for row in range(0,3):
                                for col in range(0,2):
                                    temp[row][col] = 0  
                                   
                            for j in range(0,3):
                                for n in range(0,len(all_node_alone[3*i+j])):
                                    if used_entries[all_node_alone[3*i+j][n]] + 1 > entries*10000:
                                        temp[j][0] = 1
                                for n in range(0,len(all_edge_alone[3*i+j])):
                                    if temp[j][1]<(used_ce[all_edge_alone[3*i+j][n]] + weight[i])/float(ce):
                                        temp[j][1] = (used_ce[all_edge_alone[3*i+j][n]] + weight[i])/float(ce)  
                            temp1 = 10000
                            k = 0 #Indicate which of several feasible paths is selected
                            for j in range(0,3):
                                if temp[j][0] != 1:
                                    if temp[j][1] < temp1:   #Select the feasible path that meets the flow table constraints and has the lightest load.
                                        k = j;
                                        temp1 = temp[j][1];
                            for n in range(0,len(all_edge_alone[3*i+k])):  #Select one of the feasible paths (Article k), and use link capacity and flow entries.
                                used_ce[all_edge_alone[3*i+k][n]] = used_ce[all_edge_alone[3*i+k][n]] + weight[i]
                                if used_ce[all_edge_alone[3*i+k][n]]/float(ce) > lambda1:
                                    lambda1 = used_ce[all_edge_alone[3*i+k][n]]/float(ce)   #Record the largest lambda
                            for n in range(0,len(all_node_alone[3*i+k])):
                                used_entries[all_node_alone[3*i+k][n]] = used_entries[all_node_alone[3*i+k][n]] + 1
                            #print lambda1,all_edge_alone[3*i+k]    
    
     
                            alg2_choosed_path=[]
                            alg2_choosed_path.append(source[i])
                            for j in range (0,len(all_node_alone[3*i+k])):
                                alg2_choosed_path.append(all_node_alone[3*i+k][j])
                            alg2_choosed_path.append(terminal[i])
                            alg2_choosed_path.append(weight[i])
                            fd=open(file_path+'/alg2_path_segment.txt','a') 
                            fd.write(str(alg2_choosed_path) + '\n')
                            fd.close()
        
        
        
                        file_object = open(file_path+'/alg2_path_segment.txt')
                        try:
                            data = file_object.read( )
                        finally:
                            file_object.close( )
                        data = data.replace("]","],")
                        data_len = len(data)-2
                        data = '['+data[:data_len]+']'
                        data_list = list(eval(data))
                        print data_list
                        stack = []
                        new_path = []
                        for i in range(0,len(data_list)):
                            if len(stack) == 0:
                                stack.append(data_list[i])
                            else:
                                if 'h' not in data_list[i][len(data_list[i])-2]:
                                    stack.append(data_list[i])
                                else:
                                    this_path = []
                                    for len_stack in range(0,len(stack)):
                                        a = stack.pop()
                                        this_path.append(a)
                                    one_path = []
                                    print this_path
                                    for t in range(0,len(this_path)):
                                        index = len(this_path) -t-1
                                        if index == (len(this_path)-1):
                                            for w in range(0,(len(this_path[index])-1)):
                                                one_path.append(this_path[index][w])
                                        else:
                                            for w in range(1,(len(this_path[index])-1)):
                                                one_path.append(this_path[index][w])
                                    for w in range(1, len(data_list[i]) ):
                                        one_path.append(data_list[i][w])
                                    print one_path
                                    fd = open(file_path+'/alg2_path.txt', 'a')
                                    fd.write(str(one_path) + '\n')
                                    fd.close()                   
                            
                            
        
        
        
                            
                                                    
                        
                        p1 = file_path+"/alg2_entries.json"  #rounding
                        fd = open(p1, 'w')
                        fd.write(json.dumps(used_entries, indent=1))
                        fd.close()                             
                            
    
                        p1 = file_path+"/alg2_ce.json"  #rounding
                        fd = open(p1, 'w')
                        alg2_ce = {}
                        for e in all_edge:
                            alg2_ce[e] = float(used_ce[e])/float(ce)
                        fd.write(json.dumps(alg2_ce, indent=1))
                        fd.close()
                        
                        
                                                          
                        print "greedy",lambda1 
                        p1 = file_path+"/alg2_lambda.json"
                        fd = open(p1, 'w')
                        fd.write(json.dumps(lambda1))
                        fd.write(json.dumps("/"))
                        fd.close()     
                        alg2=alg2+lambda1             
                                        
                              
                                 
                            
                    if alg == 3:  #ospf
                        lambda1=0  
                        used_ce = defaultdict(lambda:None)
                        used_entries  = defaultdict(lambda:None)
                        for v in all_node:
                            used_entries[v] = 0
                        for e in all_edge:
                            used_ce[e] = 0
                            
                        for i in range(0,flow_number):
                            for n in range(0,len(all_edge_alone[3*i])):
                                    #print n       
                                    used_ce[all_edge_alone[3*i][n]] = used_ce[all_edge_alone[3*i][n]] + weight[i]
                                    if used_ce[all_edge_alone[3*i][n]]/float(ce) > lambda1:
                                        #print "hhhhh"
                                        lambda1 = used_ce[all_edge_alone[3*i][n]]/float(ce)
                            #print weight[i],source[i],terminal[i],lambda1,all_edge_alone[3*i+choose]
                        print "ospf",lambda1  
                        p1 = file_path+"/alg3_lambda.json"  #rounding
                        fd = open(p1, 'w')
                        fd.write(json.dumps(lambda1))
                        fd.write(json.dumps("/"))
                        fd.close()  
                        alg3=alg3+lambda1   
    
    
                        p1 = file_path+"/alg3_ce.json"  #rounding
                        fd = open(p1, 'w')
                        alg3_ce = {}
                        for e in all_edge:
                            alg3_ce[e] = float(used_ce[e])/float(ce)
                        fd.write(json.dumps(alg3_ce, indent=1))
                        fd.close()
    print "Alg1 Finished"
