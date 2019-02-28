#!/usr/bin/python3

import sys,random

bm25_run = "/home/sumanta/Documents/Porcupine-data/parasim-manual-assesment.old/baseline/parasim-bm25-filtered-paragraph-manual-y2test.run"
asptext_run = "/home/sumanta/Documents/Porcupine-data/parasim-manual-assesment.old/aspfet-out/parasim-true-page-para-train--asptext-run"
aspvec_run = "/home/sumanta/Documents/Porcupine-data/parasim-manual-assesment.old/aspvec-out/manual-assesment-y2test-aspvec.run"

train_triples = "/home/sumanta/Documents/Porcupine-data/parasim-manual-assesment/triples/triples.train/manually-created-y2train.triples"
with open(bm25_run, 'r') as bm:
    bm_lines = bm.readlines()
with open(asptext_run, 'r') as at:
    at_lines = at.readlines()
with open(aspvec_run, 'r') as av:
    av_lines = av.readlines()
with open(train_triples, 'r') as trip:
    trip_lines = trip.readlines()

bm25_parasim_dict = dict()
for l in bm_lines:
    p1 = l.split(" ")[0].split(":")[2]
    p2 = l.split(" ")[2]
    score = l.split(" ")[4]
    bm25_parasim_dict[frozenset([p1, p2])] = score

aspt_parasim_dict = dict()
for l in at_lines:
    p1 = l.split(" ")[0].split(":")[2]
    p2 = l.split(" ")[2]
    score = l.split(" ")[4]
    aspt_parasim_dict[frozenset([p1, p2])] = score

aspv_parasim_dict = dict()
for l in av_lines:
    p1 = l.split(" ")[0].split(":")[2]
    p2 = l.split(" ")[2]
    score = l.split(" ")[4]
    aspv_parasim_dict[frozenset([p1, p2])] = score

triples_qrels = dict()
for l in trip_lines:
    p1 = l.split(" ")[1]
    p2 = l.split(" ")[2]
    p3 = l.split(" ")[3]
    triples_qrels[frozenset([p1, p2, p3])] = p3

print("BM25 dict size: " + str(len(bm25_parasim_dict.keys())) + "\nAspt dict size: " + str(
    len(aspt_parasim_dict.keys())) + "\nAspv dict size: " + str(len(aspv_parasim_dict.keys())))

def run_odd_one_out(method_dict):
    odd_run = dict()
    for k in triples_qrels.keys():
        s = 0.0
        odd = ""
        for p in k:
            parapair = k.difference(frozenset([p]))
            if len(parapair)<2:
                print("Something strange with this: "+str(k))
                continue
            if parapair not in method_dict.keys():
                print(str(parapair)+" not in method_dict")
            elif float(method_dict[parapair])>s:
                s = float(method_dict[parapair])
                odd = p
        odd_run[k] = p
    return odd_run

def evaluate(run_dict):
    total_q = len(run_dict.keys())
    hit = 0.0
    for k in run_dict.keys():
        if triples_qrels[k]==run_dict[k]:
            hit+=1.0
    return hit*100/total_q

bm25_run = run_odd_one_out(bm25_parasim_dict)
aspt_run = run_odd_one_out(aspt_parasim_dict)
aspv_run = run_odd_one_out(aspv_parasim_dict)

print("BM25 accuracy: "+str(evaluate(bm25_run))+"%")
print("ASPt accuracy: "+str(evaluate(aspt_run))+"%")
print("ASPv accuracy: "+str(evaluate(aspv_run))+"%")