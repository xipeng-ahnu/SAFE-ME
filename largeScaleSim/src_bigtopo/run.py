import os
from nfv_distribution_LP import *
from reroute import *
from reroute_compare_alg import *
for ratio in range(1,11):
    print "ratio=",ratio
    flow_num = 1500*ratio
    file_path = 'data/'+'flow_num='+str(flow_num)
    os.makedirs(file_path)

    get_nfv_distribution(ratio,174,file_path)
    get_route_alg1(file_path)
    
    get_route_compare_algs(file_path)
