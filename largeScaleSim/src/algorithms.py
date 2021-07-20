
import copy
import math
from pulp import *
from collections import defaultdict
from operator import itemgetter
from prioritydictionary import priorityDictionary
from graph_for_l2 import DiGraph
import json


#
def ksp_yen(graph, node_start, node_end, max_k=2):
    #Question:distances?? previous??
    distances, previous = dijkstra(graph, node_start)
    
    A = [{'cost': distances[node_end], 
          'path': path(previous, node_start, node_end)}]
    B = []
    
    if not A[0]['path']: return A
    
    for k in range(1, max_k):
        for i in range(0, len(A[-1]['path']) - 1):
            node_spur = A[-1]['path'][i]
            path_root = A[-1]['path'][:i+1]
            
            edges_removed = []
            for path_k in A:
                curr_path = path_k['path']
                if len(curr_path) > i and path_root == curr_path[:i+1]:
                    cost = graph.remove_edge(curr_path[i], curr_path[i+1])
                    if cost == -1:
                        continue
                    edges_removed.append([curr_path[i], curr_path[i+1], cost])
            
            path_spur = dijkstra(graph, node_spur, node_end)
            
            if path_spur['path']:
                path_total = path_root[:-1] + path_spur['path']
                dist_total = distances[node_spur] + path_spur['cost']
                potential_k = {'cost': dist_total, 'path': path_total}
           
                if not (potential_k in B):
                    B.append(potential_k)
            
            for edge in edges_removed:
                graph.add_edge(edge[0], edge[1], edge[2])
        
        if len(B):
            B = sorted(B, key=itemgetter('cost'))
            A.append(B[0])
            B.pop(0)
        else:
            break
    
    return A


#
def dijkstra(graph, node_start, node_end=None):
    #print"graph",graph
    #print node_start, node_end
    distances = {}      
    previous = {}       
    Q = priorityDictionary()

    for v in graph:
      ##print "-%s-"%v
      distances[v] = DiGraph.INFINITY
      previous[v] = DiGraph.UNDEFINDED
      Q[v] = DiGraph.INFINITY
      for u in graph[v]:
        if u in distances:
          continue 
        distances[u] = DiGraph.INFINITY
    
    distances[node_start] = 0
    Q[node_start] = 0
    
    for v in Q:
        if v == node_end: break
        if not graph[v]:
            continue
        for u in graph[v]:
            cost_vu = distances[v] + graph[v][u]
            if cost_vu < distances[u]:
                distances[u] = cost_vu
                Q[u] = cost_vu
                previous[u] = v
    if node_end:
        return {'cost': distances[node_end], 
                'path': path(previous, node_start, node_end)}
    else:
        return (distances, previous)



def dijkstra2(graph, node_start, node_end=None,all_paths=None):
    distances = {}      
    previous = {}       
    Q = priorityDictionary()
    for v in graph:
      distances[v] = DiGraph.INFINITY
      previous[v] = DiGraph.UNDEFINDED
      Q[v] = DiGraph.INFINITY
      for u in graph[v]:
        if u in distances:
          continue 
        distances[u] = DiGraph.INFINITY
    
    distances[node_start] = 0
    Q[node_start] = 0
    
    for v in Q:
        if v == node_end: break
        if not graph[v]:
            continue
        for u in graph[v]:
            newcost = graph[v][u]
            for w in range(0,len(all_paths)):
              if u == all_paths[w]:
                newcost = 100
            cost_vu = distances[v] + newcost
            if cost_vu < distances[u]:
                distances[u] = cost_vu
                Q[u] = cost_vu
                previous[u] = v

    if node_end:
        return {'cost': distances[node_end], 
                'path': path(previous, node_start, node_end)}
    else:
        return (distances, previous)


def dijkstra3(graph, node_start, node_end=None,all_paths=None):
    distances = {}      
    previous = {}       
    Q = priorityDictionary()
    for v in graph:
      distances[v] = DiGraph.INFINITY
      previous[v] = DiGraph.UNDEFINDED
      Q[v] = DiGraph.INFINITY
      for u in graph[v]:
        if u in distances:
          continue 
        distances[u] = DiGraph.INFINITY
    
    distances[node_start] = 0
    Q[node_start] = 0
    
    for v in Q:
        if v == node_end: break
        if not graph[v]:
            continue
        for u in graph[v]:
            newcost = graph[v][u]
            for w in range(0,len(all_paths)):
              if u == all_paths[w]:
                newcost = 100
            cost_vu = distances[v] + newcost
            if cost_vu < distances[u]:
                distances[u] = cost_vu
                Q[u] = cost_vu
                previous[u] = v

    if node_end:
        return {'cost': distances[node_end], 
                'path': path(previous, node_start, node_end)}
    else:
        return (distances, previous)


#
def path(previous, node_start, node_end):
    route = []

    node_curr = node_end    
    while True:
        route.append(node_curr)
        if previous[node_curr] == node_start:
            route.append(node_start)
            break
        elif previous[node_curr] == DiGraph.UNDEFINDED:
            return []
        
        node_curr = previous[node_curr]
    
    route.reverse()
    return route
