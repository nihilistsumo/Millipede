#!/usr/bin/python3

import numpy as np
import random

bm25_run = "/home/sumanta/Documents/Porcupine-data/parasim-manual-assesment/baseline/parasim-bm25-filtered-paragraph-manual-y2test.run"
asptext_run = "/home/sumanta/Documents/Porcupine-data/parasim-manual-assesment/aspfet-out/parasim-true-page-para-train--asptext-run"
aspvec_run = "/home/sumanta/Documents/Porcupine-data/parasim-manual-assesment/aspvec-out/manual-assesment-y2test-aspvec.run"

train_triples = "/home/sumanta/Documents/Porcupine-data/parasim-manual-assesment/triples/triples.train/manually-created-y2train.triples.qrels"

bm25_parasim_dict = dict()
aspt_parasim_dict = dict()
aspv_parasim_dict = dict()
triples_qrels = dict()

def init():
    with open(bm25_run, 'r') as bm:
        for l in bm.readlines():
            p1 = l.split(" ")[0].split(":")[2]
            p2 = l.split(" ")[2]
            score = l.split(" ")[4]
            bm25_parasim_dict[frozenset([p1, p2])] = score

    with open(asptext_run, 'r') as at:
        for l in at.readlines():
            p1 = l.split(" ")[0].split(":")[2]
            p2 = l.split(" ")[2]
            score = l.split(" ")[4]
            aspt_parasim_dict[frozenset([p1, p2])] = score

    with open(aspvec_run, 'r') as av:
        for l in av.readlines():
            p1 = l.split(" ")[0].split(":")[2]
            p2 = l.split(" ")[2]
            score = l.split(" ")[4]
            aspv_parasim_dict[frozenset([p1, p2])] = score

    with open(train_triples, 'r') as trip:
        for l in trip.readlines():
            p1 = l.split(" ")[1]
            p2 = l.split(" ")[2]
            p3 = l.split(" ")[3]
            triples_qrels[frozenset([p1, p2, p3])] = p3

    for i in range(100):
        k = random.sample(triples_qrels.keys(),1)
        print(str(k[0])+": "+triples_qrels[k[0]])

def run_odd_one_out(method_dict):
    odd_run = dict()
    for k in triples_qrels.keys():
        s = 0.0
        odd = ""
        for p in k:
            parapair = k.difference(frozenset([p]))
            if len(parapair)<2:
                print(str(k)+" key size not 3!")
                continue
            if parapair not in method_dict.keys():
                print(str(parapair)+" does not exist in score dict!")
                continue
            curr_score = float(method_dict[parapair])
            if curr_score>s:
                s = curr_score
                odd = p
        odd_run[k] = odd
    return odd_run

def evaluate(run_dict):
    total_q = len(run_dict.keys())
    hit = 0.0
    for k in run_dict.keys():
        if triples_qrels[k]==run_dict[k]:
            hit+=1.0
    return hit*100/total_q

init()
bm25_run = run_odd_one_out(bm25_parasim_dict)
aspt_run = run_odd_one_out(aspt_parasim_dict)
aspv_run = run_odd_one_out(aspv_parasim_dict)

print("BM25 accuracy: "+str(evaluate(bm25_run))+"%")
print("ASPt accuracy: "+str(evaluate(aspt_run))+"%")
print("ASPv accuracy: "+str(evaluate(aspv_run))+"%")
