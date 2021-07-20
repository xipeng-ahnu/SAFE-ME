import os 

from nfv_distribution_LP import *
from reroute import *
from reroute_compare_alg import *

for ratio in range(1,11):
    print "ratio=",ratio
    flow_num = 300*ratio
    file_path = 'data/'+'flow_num='+str(flow_num)
    os.makedirs(file_path)

    get_nfv_distribution(ratio,80,file_path)
    get_route_alg1(file_path)
    
    get_route_compare_algs(file_path)





    #p11 = file_path+"/111.json"  # rounding







'''

for i in range(1,11):
    ratio =i
    os.system("python ./nfv_distribution_LP.py")
    os.system("python ./reroute.py")
    os.system("python ./reroute_compare_alg.py")
'''