#-*- coding: utf-8 -*-
import random
from algorithms import dijkstra

from graph_for_l2 import DiGraph
from collections import defaultdict
from pulp import *
import math

import json
from time import sleep

#Print out each stream (28 in total, whichever is the specific switch)
sfc = ['F-I-D','F-P','F-I-D-W','I-P']  #F:firewall, I:IDS, D: IPSec, P: Proxy, W: WAN-opt (need shun xu: F-I-P-D-W) 

  #The proportion of the number of hits to the number of host pairs (10 points)

def get_flows(flows_num,ratio):
    k = 1
    m=0
    ii=0
    flowDic = {}
    for i in range(0,flows_num):
        #print"i",i
        ii=i+1
        for j in range(i,flows_num):
            if i != j:
                j=j+1  #h is the serial number is from 1
                pro = random.randint(1,10)
                m=m+1
                #if flows_num*(flows_num-1)/2 - m == flows_num*(flows_num-1)/2*ratio*0.1 - k:
                if flows_num*(flows_num-1)/2 - m == 1500*ratio - k:

                    rand = random.randint(1,100)
                    #[Flow source switch, destination switch, bandwidth, passed function chain]
                    flows = ['h'+str(ii),'h'+str(j),rand,sfc[rand%4]]
                    #print flows
                    flowDic[k] = flows
                    k +=1
                else:                        
                    #if pro<=ratio and k <= flows_num*(flows_num-1)/2* ratio*0.1:
                    if pro<=ratio and k <= 1500* ratio:
                        
                        rand = random.randint(1,100)
                        #[Flow source switch, destination switch, bandwidth, passed function chain]
                        flows = ['h'+str(ii),'h'+str(j),rand,sfc[rand%4]]
                        #print flows
                        flowDic[k] = flows
                        k +=1
    return flowDic



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
        
def txt_wrap_by2(start_str, end_str, html):
    start = 0
    keyvaule=[]
    while start <=len(html):
        start = html.find(start_str,start)
        if start >= 0:
            start += len(start_str)
            end = html.find(end_str, start)
            if end >= 0:
                keyvaule.append(html[start:end].strip())                
                start = end 
        else:
            return keyvaule
       
def find_n_sub_str(src, sub, pos, start):
    index = src.find(sub, start)
    if index != -1 and pos > 0:
        return find_n_sub_str(src, sub, pos - 1, index + 1)
    return index

def get_nfv_distribution(ratio, host_num,file_path):

    CODEC = 'utf-8'
    mynet = "rocketfuel_87s174h50nf.json"
    g = DiGraph(mynet)
    
    #Custom VNF processing power (1-10)
    capacity = {'F1':10,'F2':10,'F3':10,'F4':10,'F5':10,'F6':10,'F7':10,'F8':10,'F9':10,'F10':10,'I1':10,'I2':10,'I3':10,'I4':10,'I5':10,'I6':10,'I7':10,'I8':10,'I9':10,'I10':10,'P1':10,'P2':10,'P3':10,'P4':10,'P5':10,'P6':10,'P7':10,'P8':10,'P9':10,'P10':10,'D1':10,'D2':10,'D3':10,'D4':10,'D5':10,'D6':10,'D7':10,'D8':10,'D9':10,'D10':10,'W1':10,'W2':10,'W3':10,'W4':10,'W5':10,'W6':10,'W7':10,'W8':10,'W9':10,'W10':10}
    each_NF_num = 10
    #Enter two functional chains
    #Number of streams between 80 hosts
    flowDic = get_flows(host_num,ratio)
    flow_number = len(flowDic)
    print "flow_number",flow_number
    #print flowDic
    #Find out which streams of each type of NF have passed
    flow = {}
    flow['F'] = []
    flow['I'] = []
    flow['P'] = []
    flow['D'] = []
    flow['W'] = []
    for key in flowDic:
        if 'F' in str(flowDic[key][3]):
            flow['F'].append(key)
        if 'I' in str(flowDic[key][3]):
            flow['I'].append(key)
        if 'P' in str(flowDic[key][3]):
            flow['P'].append(key)
        if 'D' in str(flowDic[key][3]):
            flow['D'].append(key)
        if 'W' in str(flowDic[key][3]):
            flow['W'].append(key)
    #j stands for 9 processors, i stands for task (flow)
    p = [([0] * len(flow)*10) for i in range(len(flowDic))]
    #print len(p),len(p[0])
    
    
    
    for j in capacity.keys():
        print j
        #Calculate the processing power of Pij = stream bandwidth * distance to the NF (S-VNF-D) / NF
        if 'F' in j:
            #print "F",j
            if '1' in j and '10' not in j:
                row = 0
            elif '2' in j:
                row = 1
            elif '3' in j:
                row = 2
            elif '4' in j:
                row = 3
            elif '5' in j:
                row = 4
            elif '6' in j:
                row = 5
            elif '7' in j:
                row = 6
            elif '8' in j:
                row = 7
            elif '9' in j:
                row = 8
            elif '10' in j:
                #print "F10",j
                row = 9        
            for i in flow['F']:
            
               # print flowDic[i][0],j,flowDic[i][1]
                path1 = dijkstra(g, flowDic[i][0], j)
                path2 = dijkstra(g, j, flowDic[i][1])
                distance = path1.get('cost')+path2.get('cost')
                bandwidth = flowDic[int(i)][2]
                power = capacity[j]
                #print "power",power
                #p[i-1][row] = bandwidth * distance / power
                distance = math.sqrt(math.sqrt(distance))
                p[i-1][row] = bandwidth * distance / power
                #p[i-1][row] = bandwidth
                #print i
                #print p[i-1][row]
        elif 'I' in j:
            if '1' in j and '10' not in j:
                row = 10
            elif '2' in j:
                row = 11
            elif '3' in j:
                row = 12
            elif '4' in j:
                row = 13
            elif '5' in j:
                row = 14
            elif '6' in j:
                row = 15
            elif '7' in j:
                row = 16
            elif '8' in j:
                row = 17
            elif '9' in j:
                row = 18
            elif '10' in j:
                row = 19
            for i in flow['I']:
                path1 = dijkstra(g, flowDic[i][0], j)
                path2 = dijkstra(g, j, flowDic[i][1])
                distance = path1.get('cost')+path2.get('cost')
                bandwidth = flowDic[int(i)][2]
                power = capacity[j]
                distance = math.sqrt(math.sqrt(distance))
                p[i-1][row] = bandwidth * distance / power
        elif 'P' in j:
            if '1' in j and '10' not in j:
                row = 20
            elif '2' in j:
                row = 21
            elif '3' in j:
                row = 22
            elif '4' in j:
                row = 23
            elif '5' in j:
                row = 24
            elif '6' in j:
                row = 25
            elif '7' in j:
                row = 26
            elif '8' in j:
                row = 27
            elif '9' in j:
                row = 28
            elif '10' in j:
                row = 29
            for i in flow['P']:
                path1 = dijkstra(g, flowDic[i][0], j)
                path2 = dijkstra(g, j, flowDic[i][1])
                distance = path1.get('cost')+path2.get('cost')
                bandwidth = flowDic[int(i)][2]
                power = capacity[j]
                distance = math.sqrt(math.sqrt(distance))
                p[i-1][row] = bandwidth * distance / power
                
        elif 'D' in j:
            if '1' in j and '10' not in j:
                row = 30
            elif '2' in j:
                row = 31
            elif '3' in j:
                row = 32
            elif '4' in j:
                row = 33
            elif '5' in j:
                row = 34
            elif '6' in j:
                row = 35
            elif '7' in j:
                row = 36
            elif '8' in j:
                row = 37
            elif '9' in j:
                row = 38
            elif '10' in j:
                row = 39
            for i in flow['D']:
                path1 = dijkstra(g, flowDic[i][0], j)
                
                path2 = dijkstra(g, j, flowDic[i][1])
                distance = path1.get('cost')+path2.get('cost')
                bandwidth = flowDic[int(i)][2]
                power = capacity[j]
                distance = math.sqrt(math.sqrt(distance))
                p[i-1][row] = bandwidth * distance / power
        elif 'W' in j :
            if '1' in j and '10' not in j:
                row = 40
            elif '2' in j:
                row = 41
            elif '3' in j:
                row = 42
            elif '4' in j:
                row = 43
            elif '5' in j:
                row = 44
            elif '6' in j:
                row = 45
            elif '7' in j:
                row = 46
            elif '8' in j:
                row = 47
            elif '9' in j:
                row = 48
            elif '10' in j:
                row = 49
            for i in flow['W']:
                path1 = dijkstra(g, flowDic[i][0], j)
                path2 = dijkstra(g, j, flowDic[i][1])
                distance = path1.get('cost')+path2.get('cost')
                bandwidth = flowDic[int(i)][2]
                power = capacity[j]
                distance = math.sqrt(math.sqrt(distance))
                p[i-1][row] = bandwidth * distance / power
    
    '''
    Solving linear equation
    '''
    #x = [[0 for col in range(len(flowDic))] for row in range(3)]
    #x[i][j] ：Indicates that the ith stream passes through the jth vnf, and j(0-8) represents [F1, F2, F3, I1, I2, I3, P1, P2, P3]
    '''Which F is passed through?'''
    x =[[0 for col in range(10)] for row in range(len(flowDic))]
    #print x
    for i in range(0, len(flowDic)):
        for j in range(0, 10):
            x[i][j] = "x"
            if len(flowDic) < 100000:
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
    for i in range(0, len(flowDic)):
        z.append("z" + str(i))
    
    temp = []
    for i in range(0, len(flowDic)):
        for j in range(0,10):  # 3 si the number of path that each flow can choose
            temp.append(x[i][j])
    for i in range(0, len(flowDic)):
        temp.append(z[i])
    
    prob = LpProblem('lptest', LpMinimize)
    r = LpVariable('r', lowBound = 0)
    xx = LpVariable.dicts("",temp, lowBound = 0,upBound = 1)#,cat = pulp.LpInteger
    #print temp
    print "-------2222222-----"
    #print x[0]
    #Add the target equation
    #0-28 flows
    prob += r
    #0->F(0,1,2);1->I(3,4,5);2->P(6,7,8)
    x_e = defaultdict(lambda:(defaultdict(lambda:(defaultdict(lambda:None)))))
    for i in range(10):
        for j in range(len(flowDic)):
            x_e[i][j][0] = x[j][i]
            x_e[i][j][1] = p[j][i]
    for i in range(0,10):
        prob += lpSum(xx[x_e[i][j][0]]*x_e[i][j][1] for j in x_e[i]) <=r
    #Add constraints
    for i in range(0,len(flowDic)):
        prob += lpSum([xx[j] for j in x[i]]) ==1
    GLPK().solve(prob)
    print 'F_objective_sr =', value(prob.objective)
    
    
    
    
    i=0
    j=0
    l=0
    for v in prob.variables():
        #print v, v.varValue
        l =l +1
        if l<flow_number*10+1:  #(the number of flows /cdot 3) +1
            x[i][j]=v.varValue
            if j<9:
                j =j+1
            else:
                i=i+1
                j=0
    for i in range(0,flow_number):
        k=0
        choose=0
        for j in range(0,10):
            if x[i][j]>k:
                choose=j
                k=x[i][j]
        for j in range(0,10):
            if j == choose:
                x[i][j] = 1
            else:
                x[i][j] = 0
    
    for i in range(0,flow_number):
        if ('F' in str(flowDic[i+1][3])):
            for j in range(0,10):
                if x[i][j] == 1:
                    flowDic[i+1].append(j)  
            #print flowDic[i+1]
            
    
    
    
    
    
    #sleep(600)
    
    '''Which I passed through'''
    #P_1 refers to the cost of I function
    p_1 = [([0] * 10) for i in range(len(flowDic))]
    #print "hh",len(p_1),len(p_1[0])
    for i in range(len(flowDic)):
        for j in range(10):
            #print i,j,
            p_1[i][j] = p[i][j+10]
    x1 =[[0 for col in range(10)] for row in range(len(flowDic))]
    for i in range(0, len(flowDic)):
        for j in range(0, 10):
            x1[i][j] = "x"
            if len(flowDic) < 100000:
                if i < 10:
                    x1[i][j] = x1[i][j] + "0000"
                elif i < 100:
                    x1[i][j] = x1[i][j] + "000"
                elif i < 1000:
                    x1[i][j] = x1[i][j] + "00"
                elif i < 10000:
                    x1[i][j] = x1[i][j] + "0"
            x1[i][j] = x1[i][j] + str(i) + str(j)
    
    z1 = []
    for i in range(0, len(flowDic)):
        z1.append("z" + str(i))
    
    temp1 = []
    for i in range(0, len(flowDic)):
        for j in range(0,10):  # 3 si the number of path that each flow can choose
            temp1.append(x1[i][j])
    for i in range(0, len(flowDic)):
        temp1.append(z1[i])
    
    prob1 = LpProblem('lptest1', LpMinimize)
    r1 = LpVariable('r1', lowBound = 0)
    xx1 = LpVariable.dicts("",temp1, lowBound = 0,upBound = 1)#, cat = pulp.LpInteger
    #print xx1

    prob1 += r1
    #0->F(0,1,2);1->I(3,4,5);2->P(6,7,8)
    x_e1 = defaultdict(lambda:(defaultdict(lambda:(defaultdict(lambda:None)))))
    for i in range(10):
        for j in range(len(flowDic)):
            x_e1[i][j][0] = x1[j][i]
            x_e1[i][j][1] = p_1[j][i]
    for i in range(0,10):
        prob1 += lpSum(xx1[x_e1[i][j][0]]*x_e1[i][j][1] for j in x_e1[i]) <=r1
    for i in range(0,len(flowDic)):
        prob1 += lpSum([xx1[j] for j in x1[i]]) ==1
    GLPK().solve(prob1)
    print 'I_objective_sr =', value(prob1.objective)
    
    
    
    
    i=0
    j=0
    l=0
    for v in prob1.variables():
        l =l +1
        if l<flow_number*10+1:  #(the number of flows /cdot 3) +1
            x[i][j]=v.varValue
            if j<9:
                j =j+1
            else:
                i=i+1
                j=0
    for i in range(0,flow_number):
        k=0
        choose=0
        for j in range(0,10):
            if x[i][j]>k:
                choose=j
                k=x[i][j]
        for j in range(0,10):
            if j == choose:
                x[i][j] = 1
            else:
                x[i][j] = 0
    
    for i in range(0,flow_number):
        if ('I' in str(flowDic[i+1][3])):
            for j in range(0,10):
                if x[i][j] == 1:
                    flowDic[i+1].append(j)  
            #print flowDic[i+1]
    
    
    
    '''Which P passed?'''
    p_3 = [([0] * 10) for i in range(len(flowDic))]
    for i in range(len(flowDic)):
        for j in range(10):
            p_3[i][j] = p[i][j+20]
    x3 =[[0 for col in range(10)] for row in range(len(flowDic))]
    for i in range(0, len(flowDic)):
        for j in range(0, 10):
            x3[i][j] = "x"
            if len(flowDic) < 100000:
                if i < 10:
                    x3[i][j] = x3[i][j] + "0000"
                elif i < 100:
                    x3[i][j] = x3[i][j] + "000"
                elif i < 1000:
                    x3[i][j] = x3[i][j] + "00"
                elif i < 10000:
                    x3[i][j] = x3[i][j] + "0"
            x3[i][j] = x3[i][j] + str(i) + str(j)
    z3 = []
    for i in range(0, len(flowDic)):
        z3.append("z3" + str(i))
    
    temp3 = []
    for i in range(0, len(flowDic)):
        for j in range(0,10):  # 3 si the number of path that each flow can choose
            temp3.append(x3[i][j])
    for i in range(0, len(flowDic)):
        temp3.append(z3[i])
    
    prob3 = LpProblem('lptest3', LpMinimize)
    r3 = LpVariable('r3', lowBound = 0)
    xx3 = LpVariable.dicts("",temp3, lowBound = 0,upBound = 1)#, cat = pulp.LpInteger
    x_e3 = defaultdict(lambda:(defaultdict(lambda:(defaultdict(lambda:None)))))
    for i in range(10):
        for j in range(len(flowDic)):
            x_e3[i][j][0] = x3[j][i]
            x_e3[i][j][1] = p_3[j][i]
    for i in range(0,10):
        prob3 += lpSum(xx3[x_e3[i][j][0]]*x_e3[i][j][1] for j in x_e3[i]) <=r3
    for i in range(0,len(flowDic)):
        prob3 += lpSum([xx3[j] for j in x3[i]]) ==1
    GLPK().solve(prob3)
    print 'P_objective_sr =', value(prob3.objective)
    i=0
    j=0
    l=0
    for v in prob3.variables():
        l =l +1
        if l<flow_number*10+1:  #(the number of flows /cdot 3) +1
            x[i][j]=v.varValue
            if j<9:
                j =j+1
            else:
                i=i+1
                j=0
    for i in range(0,flow_number):
        k=0
        choose=0
        for j in range(0,10):
            if x[i][j]>k:
                choose=j
                k=x[i][j]
        for j in range(0,10):
            if j == choose:
                x[i][j] = 1
            else:
                x[i][j] = 0
    
    for i in range(0,flow_number):
        if ('P' in str(flowDic[i+1][3])):
            for j in range(0,10):
                if x[i][j] == 1:
                    flowDic[i+1].append(j)  
            #print flowDic[i+1]
    
    
    
    
    
    '''Which D is passed through?'''
    p_4 = [([0] * 10) for i in range(len(flowDic))]
    for i in range(len(flowDic)):
        for j in range(10):
            p_4[i][j] = p[i][j+30]
    x4 =[[0 for col in range(10)] for row in range(len(flowDic))]
    for i in range(0, len(flowDic)):
        for j in range(0, 10):
            x4[i][j] = "x"
            if len(flowDic) < 100000:
                if i < 10:
                    x4[i][j] = x4[i][j] + "0000"
                elif i < 100:
                    x4[i][j] = x4[i][j] + "000"
                elif i < 1000:
                    x4[i][j] = x4[i][j] + "00"
                elif i < 10000:
                    x4[i][j] = x4[i][j] + "0"
            x4[i][j] = x4[i][j] + str(i) + str(j)
    z4 = []
    for i in range(0, len(flowDic)):
        z4.append("z4" + str(i))
    
    temp4 = []
    for i in range(0, len(flowDic)):
        for j in range(0,10):  # 3 si the number of path that each flow can choose
            temp4.append(x4[i][j])
    for i in range(0, len(flowDic)):
        temp4.append(z4[i])
    
    prob4 = LpProblem('lptest4', LpMinimize)
    r4 = LpVariable('r4', lowBound = 0)
    xx4 = LpVariable.dicts("",temp4, lowBound = 0,upBound = 1)#, cat = pulp.LpInteger
    prob4 += r4
    x_e4 = defaultdict(lambda:(defaultdict(lambda:(defaultdict(lambda:None)))))
    for i in range(10):
        for j in range(len(flowDic)):
            x_e4[i][j][0] = x4[j][i]
            x_e4[i][j][1] = p_4[j][i]
    for i in range(0,10):
        prob4 += lpSum(xx4[x_e4[i][j][0]]*x_e4[i][j][1] for j in x_e4[i]) <=r4
    for i in range(0,len(flowDic)):
        prob4 += lpSum([xx4[j] for j in x4[i]]) ==1
    GLPK().solve(prob4)
    print 'D_objective_sr =', value(prob4.objective)
    i=0
    j=0
    l=0
    for v in prob4.variables():
        l =l +1
        if l<flow_number*10+1:  #(the number of flows /cdot 3) +1
            x[i][j]=v.varValue
            if j<9:
                j =j+1
            else:
                i=i+1
                j=0
    for i in range(0,flow_number):
        k=0
        choose=0
        for j in range(0,10):
            if x[i][j]>k:
                choose=j
                k=x[i][j]
        for j in range(0,10):
            if j == choose:
                x[i][j] = 1
            else:
                x[i][j] = 0
    
    for i in range(0,flow_number):
        if ('D' in str(flowDic[i+1][3])):
            for j in range(0,10):
                if x[i][j] == 1:
                    flowDic[i+1].append(j)  
            #print flowDic[i+1]
    
    
    
    
        
    '''Which W to solve'''
    p_5 = [([0] * 10) for i in range(len(flowDic))]
    for i in range(len(flowDic)):
        for j in range(10):
            p_5[i][j] = p[i][j+40]
    x5 =[[0 for col in range(10)] for row in range(len(flowDic))]
    for i in range(0, len(flowDic)):
        for j in range(0, 10):
            x5[i][j] = "x"
            if len(flowDic) < 100000:
                if i < 10:
                    x5[i][j] = x5[i][j] + "0000"
                elif i < 100:
                    x5[i][j] = x5[i][j] + "000"
                elif i < 1000:
                    x5[i][j] = x5[i][j] + "00"
                elif i < 10000:
                    x5[i][j] = x5[i][j] + "0"
            x5[i][j] = x5[i][j] + str(i) + str(j)
    z5 = []
    for i in range(0, len(flowDic)):
        z5.append("z5" + str(i))
    
    temp5 = []
    for i in range(0, len(flowDic)):
        for j in range(0,10):  # 3 si the number of path that each flow can choose
            temp5.append(x5[i][j])
    for i in range(0, len(flowDic)):
        temp5.append(z5[i])
    
    prob5 = LpProblem('lptest5', LpMinimize)
    r5 = LpVariable('r5', lowBound = 0)
    xx5 = LpVariable.dicts("",temp5, lowBound = 0,upBound = 1)#, cat = pulp.LpInteger
    #print xx3

    prob5 += r5
    x_e5 = defaultdict(lambda:(defaultdict(lambda:(defaultdict(lambda:None)))))
    for i in range(10):
        for j in range(len(flowDic)):
            x_e5[i][j][0] = x5[j][i]
            x_e5[i][j][1] = p_5[j][i]
    for i in range(0,10):
        prob5 += lpSum(xx5[x_e5[i][j][0]]*x_e5[i][j][1] for j in x_e5[i]) <=r5
    for i in range(0,len(flowDic)):
        prob5 += lpSum([xx5[j] for j in x5[i]]) ==1
    GLPK().solve(prob5)
    print 'W_objective_sr =', value(prob5.objective)
    i=0
    j=0
    l=0
    for v in prob5.variables():
        l =l +1
        if l<flow_number*10+1:  #(the number of flows /cdot 3) +1
            x[i][j]=v.varValue
            if j<9:
                j =j+1
            else:
                i=i+1
                j=0
    for i in range(0,flow_number):
        k=0
        choose=0
        for j in range(0,10):
            if x[i][j]>k:
                choose=j
                k=x[i][j]
        for j in range(0,10):
            if j == choose:
                x[i][j] = 1
            else:
                x[i][j] = 0
    
    for i in range(0,flow_number):
        if ('W' in str(flowDic[i+1][3])):
            for j in range(0,10):
                if x[i][j] == 1:
                    flowDic[i+1].append(j)  
            #print flowDic[i+1]
          
        
        
    flow_vnf = file_path+'/flow_vnf.txt'
    file=open(flow_vnf,'w')      
    
    
    
    
    NF_load = (defaultdict(lambda:None))
    for i in capacity:
        NF_load[i]=0
    
    for t in flowDic:
        line = str(flowDic[t])
        newsDate=txt_wrap_by("'","'",line,0)
        flow_rate=txt_wrap_by2(",",",",line)[1]
        #print "flow-rate",flow_rate
        nf_number =[]  #Save the serial number of each passed NF
        h=txt_wrap_by2(",",",",line)
        for i in range(3,len(h)):
            nf_number.append(h[i])    
        ff=find_n_sub_str(line,",",3,0)
        
        sfc_len = (len(newsDate[2])+1)/2     
        k=find_n_sub_str(line,",",2+sfc_len,0)
        #print "2222222222",line,k, txt_wrap_by(",","]",line,k)
    
        nf_number.append(txt_wrap_by(",","]",line,k)[0])
    
    
        flow_path = []
        flow_path.append(newsDate[0])
        for i in range(0,sfc_len):
            flow_path.append(str(newsDate[2][2*i])+str(int(nf_number[i])+1))   
        flow_path.append(newsDate[1])
        flow_path.append(flow_rate)
       # print flow_path,flow_path[0],len(flow_path)
        file.write(str(flow_path) + '\n')
        
        for i in range(1,sfc_len+1):
            #print flow_path[len(flow_path)-1]
            NF_load[flow_path[i]] = int(NF_load[flow_path[i]]) + int(flow_path[len(flow_path)-1])
        
    file.closed
    
    
    
    flow_vnf = file_path+'/alg1_NF_load.txt'
    file=open(flow_vnf,'w') 
    file.write(json.dumps(NF_load,indent=1))
    file.closed    
    
    
    alg1_max_NF=0
    for i in NF_load:
        if alg1_max_NF < NF_load[i]:
            alg1_max_NF = NF_load[i]
            
    fd=open(file_path+'/alg1_max_NF.txt','w')
    fd.write(json.dumps(alg1_max_NF))
    fd.closed
    
    
    
    file=open(file_path+'/flow_feasible_vnf.txt','w') 
            
    
    for t in flowDic:
        for n in range(0,3):
            for i in range(4,len(flowDic[t])):
                flowDic[t][i]=random.randint(0,each_NF_num-1)
            
                   
            line = str(flowDic[t])
            newsDate=txt_wrap_by("'","'",line,0)
            flow_rate=txt_wrap_by2(",",",",line)[1]
            #print "flow-rate",flow_rate
            nf_number =[]  #Save the serial number of each passed NF
            h=txt_wrap_by2(",",",",line)
            for i in range(3,len(h)):
                nf_number.append(h[i])    
            ff=find_n_sub_str(line,",",3,0)
        
        
            sfc_len = (len(newsDate[2])+1)/2     
            k=find_n_sub_str(line,",",2+sfc_len,0) 
            nf_number.append(txt_wrap_by(",","]",line,k)[0])
        
        
            flow_path = []
            flow_path.append(newsDate[0])
            for i in range(0,sfc_len):
                flow_path.append(str(newsDate[2][2*i])+str(int(nf_number[i])+1))   
            flow_path.append(newsDate[1])
            flow_path.append(flow_rate)
           # print flow_path,flow_path[0],len(flow_path)
            file.write(str(flow_path) + '\n')
    file.closed
    
    print "NFV Distribution Finished"



