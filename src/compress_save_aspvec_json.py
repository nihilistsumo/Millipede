#!/usr/bin/python3

import sys, json, os
import numpy as np
import pickle, dill

'''
This script takes the directory path for the aspvec json files as input, converts
all the aspvecs to a dict of para:numpy_arr(aspvec) and saves them in a file

saved data -> {key=para ID as int, value=list of tuples containing aspid as int
and aspvec value for the aspid}
'''

def save_obj(obj, filepath):
    with open(filepath, 'wb') as f:
        #pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        pickle.dump(obj, f, protocol=2)

def load_obj(filepath):
    with open(filepath, 'rb') as f:
        return pickle.load(f)

def compress_save_json(data, comp_vec_data):
    for p in data.keys():
        #paraid = p.split(':')[1]
        #paraid_val = int("0x"+paraid,16)
        aspvec = data[p]
        aspvec_val = []
        for aspid in aspvec.keys():
            aspid_val = int(aspid.split(':')[1])
            new_tuple = (aspid_val, aspvec[aspid])
            aspvec_val.append(new_tuple)
        dt=np.dtype('int,float')
        aspvec_nparr = np.array(aspvec_val,dtype=dt)
        comp_vec_data[p] = aspvec_nparr
        #print("vec "+str(sys.getsizeof(aspvec_val)))

def split_and_compress_vecs(comp_vec_data, outpath):
    compressed = {}
    compressed['paraids'] = []
    compressed['aspids'] = []
    compressed['aspvals'] = []
    count = 0
    for p in comp_vec_data.keys():
        compressed['paraids'].append(p)
        aspids_curr = []
        aspvals_curr = []
        for tup in comp_vec_data[p]:
            aspids_curr.append(tup[0])
            aspvals_curr.append(tup[1])
        compressed['aspids'].append(aspids_curr)
        compressed['aspvals'].append(aspvals_curr)
        count = count + 1
        if(count>=100):
            print('.')
            count = 0
    save_obj(compressed['paraids'],outpath+"/aspvec-paraids")
    #save_obj(compressed['vecs'],outpath+"/aspvec-vecs")
    with open(outpath+"/aspvec-aspids",'wb') as aid:
        dill.dump(compressed['aspids'],aid)
    with open(outpath+"/aspvec-aspvals",'wb') as aval:
        dill.dump(compressed['aspvals'],aval)

json_dir = sys.argv[1]
output_path = sys.argv[2]

aspvec_comp_data = {}
for json_file in os.listdir(json_dir):
    with open(json_dir+"/"+json_file) as f:
        json_data = json.load(f)
        compress_save_json(json_data, aspvec_comp_data)
        print(sys.getsizeof(aspvec_comp_data))

print("number of paras: "+str(len(aspvec_comp_data.keys())))
save_obj(aspvec_comp_data,output_path+"/aspvec-data")

#vec_data = load_obj(output_path+"/aspvec-data")
#split_and_compress_vecs(vec_data,output_path)
