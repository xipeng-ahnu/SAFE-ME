#coding=utf-8
from algorithms import dijkstra
from algorithms import dijkstra2
from algorithms import dijkstra3
#from operator import itemgetter
#from prioritydictionary import priorityDictionary
from graph_for_l2 import DiGraph
from collections import defaultdict
import json
import os
from time import sleep
#import math
CODEC = 'utf-8'
mynet = "8s9vnf.json"
g = DiGraph(mynet) 


capacity = {'F1':10,'F2':10,'F3':10,'I1':10,'I2':10,'I3':10,'P1':10,'P2':10,'P3':10}


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
        
        
def get_route_compare_algs(file_path):        
             
    all_node = []
    all_node_alone = []    
    all_edge = []    
    all_edge_alone = []
    all_edge_alone_order = []
    one_edge = []
    one_edge1= []
    one_edge_order = []
    one_node = []
    source = []
    terminal = []
    weight = []
    flow_sfc = []            
    
    fd=file_path+'/SIMPLE_path.txt'
    if os.path.exists(fd):
        os.remove(fd)
    fd=file_path+'/PDA_path.txt'
    if os.path.exists(fd):
        os.remove(fd)  
    
    
    
    
    k = 0        
    for line in open(file_path+"/flow_feasible_vnf.txt"):
        
        flow_path=txt_wrap_by("'","'",line,0)
        #
        #print flow_path,flow_path[0]
        flow_sfc.append(flow_path)
    
        if k%3 == 0:    
            source.append(flow_path[0])
            terminal.append(flow_path[len(flow_path)-2])
            weight.append(flow_path[len(flow_path)-1])  
        k=k+1  
            
            
    print len(source),len(flow_sfc),k
    
    
    flow_number = len(source)
    print "flow_number",flow_number
    
    
    for sr in range (0,flow_number):
        if sr%100 == 0:
            print"source is ",sr,source[sr], terminal[sr]
        main_path_all = []
        one_source_edge = []
        one_source_edge_order = []
        one_source_node = []
        
        main_path =[]
        for q in range(0,len(flow_sfc[3*sr])-2):
            #print "sfc",flow_sfc[3*sr][q+1]
            path = dijkstra(g, str(flow_sfc[3*sr][q]),str(flow_sfc[3*sr][q+1]))
            main_path_seg = path.get('path')
            for i in range(0,len(main_path_seg)):
                main_path_seg[i] = main_path_seg[i].encode(CODEC)
            for i in range(0,len(main_path_seg)-1):
                main_path.append(main_path_seg[i])
            if q == len(flow_sfc[3*sr])-3:
                main_path.append(main_path_seg[len(main_path_seg)-1])          
        #print main_path
        for i in range(0,len(main_path)):
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
    
        
       # print  all_node_alone,all_edge_alone,all_edge_alone_order
        
        #sleep(600)
        
        
        one_source_edge_order = []
        one_source_node = []
        one_source_edge = []    
        
        main_path =[]
        for q in range(0,len(flow_sfc[3*sr+1])-2):
            #print "sfc",flow_sfc[3*sr+1][q+1]
            path = dijkstra2(g, str(flow_sfc[3*sr+1][q]),str(flow_sfc[3*sr+1][q+1]),main_path_all)
            main_path_seg = path.get('path')
            for i in range(0,len(main_path_seg)):
                main_path_seg[i] = main_path_seg[i].encode(CODEC)
            for i in range(0,len(main_path_seg)-1):
                main_path.append(main_path_seg[i])
            if q == len(flow_sfc[3*sr+1])-3:
                main_path.append(main_path_seg[len(main_path_seg)-1])          
        #print main_path
        for i in range(0,len(main_path)):
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
        
        main_path =[]
        for q in range(0,len(flow_sfc[3*sr+2])-2):
            #print "sfc",flow_sfc[3*sr+2][q+1]
            path = dijkstra3(g, str(flow_sfc[3*sr+2][q]),str(flow_sfc[3*sr+2][q+1]),main_path_all)
            main_path_seg = path.get('path')
            for i in range(0,len(main_path_seg)):
                main_path_seg[i] = main_path_seg[i].encode(CODEC)
            for i in range(0,len(main_path_seg)-1):
                main_path.append(main_path_seg[i])
            if q == len(flow_sfc[3*sr+2])-3:
                main_path.append(main_path_seg[len(main_path_seg)-1])          
        #print main_path
        for i in range(0,len(main_path)):
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
    #print  all_node_alone
    #print  all_edge_alone_order
        weight [sr] = int (weight[sr])
    
    
    
    
    for flow_traffic in range(1,2):
        for randome_time in range(0,1):
            for entries in range(31,32):             #300-4200
                entries = entries *10000
              
                ce = 10000
                #print entries
                for alg in range(0,10):
                    if alg == 2:  #SIMPLE alg, linke load balancing 
                        used_ce = defaultdict(lambda:None)
                        used_entries  = defaultdict(lambda:None)
                        for v in all_node:
                            used_entries[v] = 0
                        for e in all_edge:
                            used_ce[e] = 0
                        lambda1 = 0
                        max_entries = 0
                        temp2 = 0
                        for i in range(0,flow_number):
                            temp = [[0 for col in range(2)] for row in range(3)]
                            for row in range(0,3):
                                for col in range(0,2):
                                    temp[row][col] = 0  
                                   
                            for j in range(0,3):
                                for n in range(0,len(all_edge_alone[3*i+j])):
                                    
                                    
                                    q=0
                                    for m in range(0,len(all_edge_alone[3*i+j])):
                                        if all_edge_alone[3*i+j][n] == all_edge_alone[3*i+j][m]:
                                            q=q+1           
                                    if temp[j][1]<(used_ce[all_edge_alone[3*i+j][n]] + q*weight[i])/float(ce):
                                        temp[j][1] = (used_ce[all_edge_alone[3*i+j][n]] + q*weight[i])/float(ce)  
                            temp1 = 1000000
                            k = 0 #Indicate which of several feasible paths is selected
                            for j in range(0,3):
                                if temp[j][1] < temp1:   #Select the feasible path that meets the flow table constraints and has the lightest load.
                                    k = j;
                                    temp1 = temp[j][1];
                            for n in range(0,len(all_edge_alone[3*i+k])):  #Select one of the feasible paths (Article k), and use link capacity and flow entries.
                                used_ce[all_edge_alone[3*i+k][n]] = used_ce[all_edge_alone[3*i+k][n]] + weight[i]
                            for n in range(0,len(all_node_alone[3*i+k])):
                                used_entries[all_node_alone[3*i+k][n]] = used_entries[all_node_alone[3*i+k][n]] + 1 
    
     
                            alg2_choosed_path=[]
                            alg2_choosed_path.append(source[i])
                            for j in range (0,len(all_node_alone[3*i+k])):
                                alg2_choosed_path.append(all_node_alone[3*i+k][j])
                            alg2_choosed_path.append(terminal[i])
                            alg2_choosed_path.append(weight[i])
                            fd=open(file_path+'/SIMPLE_path.txt','a') 
                            fd.write(str(alg2_choosed_path) + '\n')
                            fd.close()
                            
                                                    
    
                        
                        
                        alg2_entries ={}
                        for j in used_entries:
                            if 's' in str(j):
                                alg2_entries[j] = used_entries [j]
                                if max_entries < used_entries[j]:
                                    max_entries = used_entries[j]
                                    
                        p1 = file_path+"/SIMPLE_entries.json"  #rounding
                        fd = open(p1, 'w')
                        fd.write(json.dumps(alg2_entries, indent=1))
                        fd.close()  
                                
                    
                         
                        p1 = file_path+"/SIMPLE_ce.json"  #rounding
                        p2 = file_path+"/SIMPLE_NF_load.json"  # rounding
                        fd1 = open(p1, 'w')
                        fd2 = open(p2, 'w')
                        alg2_ce_link = {}
                        alg2_ce_middlebox = {}
                        for e in all_edge:
                            isMark = 0
                            #Link load and midllebox load
                            for key in capacity:
                                if key in e:
                                    alg2_ce_middlebox[key] = float(used_ce[e])/2  #eg, path: s4-F2-s4.  ce(F2s4)= double, but load(F2) = single 
                                    isMark = 1
                            if isMark == 0:
                                alg2_ce_link[e] = float(used_ce[e]) / float(ce)
                        fd1.write(json.dumps(alg2_ce_link, indent=1))
                        fd1.close()
                        fd2.write(json.dumps(alg2_ce_middlebox, indent=1))
                        fd2.close()
                        lambda1 = 0
                        for j in alg2_ce_link:
                            if lambda1 < alg2_ce_link[j]:
                                lambda1 = alg2_ce_link[j]
                                
                        SIMPLE_max_NF=0
                        for j in alg2_ce_middlebox:
                            if SIMPLE_max_NF < alg2_ce_middlebox[j]:
                                SIMPLE_max_NF = alg2_ce_middlebox[j]                 
                        

                                      
                        print "SIMPLE",lambda1,max_entries 
                        p1 = file_path+"/SIMPLE_lambda.json"
                        fd = open(p1, 'w')
                        fd.write(json.dumps(lambda1))
                        fd.close()     
              
                        p1 = file_path+"/SIMPLE_max_entries.json"
                        fd = open(p1, 'w')
                        fd.write(json.dumps(max_entries))
                        fd.close()      
                                                          
                        p1 = file_path+"/SIMPLE_max_NF.json"
                        fd = open(p1, 'w')
                        fd.write(json.dumps(SIMPLE_max_NF))
                        fd.close()  
                                                  
     
     
     
                    if alg == 3:  #PDA alg
                        used_ce = defaultdict(lambda:None)
                        used_entries  = defaultdict(lambda:None)
                        for v in all_node:
                            used_entries[v] = 0
                        for e in all_edge:
                            used_ce[e] = 0
                        lambda1 = 0
                        max_entries = 0
                        temp2 = 0
                        for i in range(0,flow_number):
                            temp = [[0 for col in range(2)] for row in range(3)]
                            for row in range(0,3):
                                for col in range(0,2):
                                    temp[row][col] = 0  
                                   
                            for j in range(0,3):
                                for n in range(0,len(all_node_alone[3*i+j])):
                                    q=0
                                    for m in range(0,len(all_node_alone[3*i+j])):
                                        if all_node_alone[3*i+j][n] == all_node_alone[3*i+j][m]:
                                            q=q+1                         
                                    
                                    if temp[j][1]<used_entries[all_node_alone[3*i+j][n]] + q:
                                        temp[j][1] = used_entries[all_node_alone[3*i+j][n]] + q 
                            temp1 = 10000000
                            k = 0 #Indicate which of several feasible paths is selected
                            for j in range(0,3):
                                if temp[j][1] < temp1:   #Select the feasible path that meets the flow table constraints and has the lightest load.
                                    k = j;
                                    temp1 = temp[j][1];
                            for n in range(0,len(all_edge_alone[3*i+k])):  #Select one of the feasible paths (Article k), and use link capacity and flow entries.
                                used_ce[all_edge_alone[3*i+k][n]] = used_ce[all_edge_alone[3*i+k][n]] + weight[i]
                                #if used_ce[all_edge_alone[3*i+k][n]]/float(ce) > lambda1:
                                    #lambda1 = used_ce[all_edge_alone[3*i+k][n]]/float(ce)   #Record the largest lambda
                            for n in range(0,len(all_node_alone[3*i+k])):
                                used_entries[all_node_alone[3*i+k][n]] = used_entries[all_node_alone[3*i+k][n]] + 1    
    
     
                            alg3_choosed_path=[]
                            alg3_choosed_path.append(source[i])
                            for j in range (0,len(all_node_alone[3*i+k])):
                                alg3_choosed_path.append(all_node_alone[3*i+k][j])
                            alg3_choosed_path.append(terminal[i])
                            alg3_choosed_path.append(weight[i])
                            fd=open(file_path+'/PDA_path.txt','a') 
                            fd.write(str(alg3_choosed_path) + '\n')
                            fd.close()
                        
                        print "PDA_used_ce",used_ce["s3F3"],used_ce["F3s3"],used_ce["s1s3"],used_ce["s3s1"],all_edge
    
    
                        
                        alg3_entries ={}
                        for j in used_entries:
                            if 's' in str(j):
                                alg3_entries[j] = used_entries [j]
                                if max_entries < used_entries[j]:
                                    max_entries = used_entries[j]
                                    
                        p1 = file_path+"/PDA_entries.json"  #rounding
                        fd = open(p1, 'w')
                        fd.write(json.dumps(alg3_entries, indent=1))
                        fd.close()  
                                            
                        
                        
                                    
                                                        
                        p1 = file_path+"/PDA_ce.json"  #rounding
                        p2 = file_path+"/PDA_NF_load.json"  # rounding
                        fd1 = open(p1, 'w')
                        fd2 = open(p2, 'w')
                        alg3_ce_link = {}
                        alg3_ce_middlebox = {}
                        for e in all_edge:
                            isMark = 0
                            #Link load and midllebox load
                            for key in capacity:
                                if key in e:
                                    alg3_ce_middlebox[key] = float(used_ce[e])/2
                                    isMark = 1
                            if isMark == 0:
                                alg3_ce_link[e] = float(used_ce[e]) / float(ce)
                        fd1.write(json.dumps(alg3_ce_link, indent=1))
                        fd1.close()
                        fd2.write(json.dumps(alg3_ce_middlebox, indent=1))
                        fd2.close()
                        lambda1 = 0
                        for j in alg3_ce_link:
                            if lambda1 < alg3_ce_link[j]:
                                lambda1 = alg3_ce_link[j]
                                
                        PDA_max_NF=0
                        for j in alg3_ce_middlebox:
                            if PDA_max_NF < alg3_ce_middlebox[j]:
                                PDA_max_NF = alg3_ce_middlebox[j]                 
                        
                        
    
                        
                        
                                      
                        print "PDA",lambda1, max_entries 
                        p1 = file_path+"/PDA_lambda.json"
                        fd = open(p1, 'w')
                        fd.write(json.dumps(lambda1))
                        fd.close()     
                        
                        
                        p1 = file_path+"/PDA_max_entries.json"
                        fd = open(p1, 'w')
                        fd.write(json.dumps(max_entries))
                        fd.close()
                        
                        p1 = file_path+"/PDA_max_NF.json"
                        fd = open(p1, 'w')
                        fd.write(json.dumps(PDA_max_NF))
                        fd.close()  
                        
    print "Compare_algs Finished"
