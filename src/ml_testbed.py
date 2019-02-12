#!/usr/bin/python3

import numpy as np
import random

from time import time
import matplotlib.pyplot as plt
from matplotlib import offsetbox
from sklearn import (manifold, datasets, decomposition, ensemble,
                     discriminant_analysis, random_projection)

def convert_qrels_to_target(qrels, paraids):
    target = []
    labels = set()
    labels_dict = {}
    qrels_dict = {}
    with open(qrels) as q:
        qrels_content = q.readlines()
    for line in qrels_content:
        labels.add(line.split(" ")[0])
        qrels_dict[line.split(" ")[2]] = line.split(" ")[0]
    i = 0
    for l in labels:
        labels_dict[l] = i
        i=i+1
    for para in paraids:
        target.append(labels_dict[qrels_dict[para]])
    return target

def get_page_paras(art_qrels):
    page_paras_dict = {}
    with open(art_qrels) as aq:
        qrels_content = aq.readlines()
    for l in qrels_content:
        page = l.split(" ")[0]
        para = l.split(" ")[2]
        if page in page_paras_dict.keys():
            page_paras_dict[page].append(para)
        else:
            paras = []
            paras.append(para)
            page_paras_dict[page] = paras
    return page_paras_dict

'''
paraids: numpy array of 4858 para IDs from by1train
aspids: numpy 2D array of 4858 arrays of 10000 aspect IDs corresponding to the paragraph indexed in paraids
aspvals: numpy 2D array of 4858 arrays of 10000 aspect values corresponding to the paragraph indexed in paraids and
aspect ids in aspids
rand_embd_dat: numpy 2D array of 4858 arrays of 100 ints/floats representing random embedding in aspect space of the 
corresponding paragraph on the same index in paraids
target: list of 4858 int labels of paragraphs corresponding to paraids index
page_paras: dictionary of 117 pageIDs to list of paraIDs in the page

'''
paraids = np.load('/home/sumanta/Documents/Porcupine-data/Porcupine_aspvec_python/obj/aspvec-paraids.npy')
aspids = np.load('/home/sumanta/Documents/Porcupine-data/Porcupine_aspvec_python/obj/aspvec-aspids.npy')
aspvals = np.load('/home/sumanta/Documents/Porcupine-data/Porcupine_aspvec_python/obj/aspvec-aspvals.npy')
rand_embd_dat = np.load('/home/sumanta/Documents/Porcupine-data/Porcupine_aspvec_python/obj/aspvec-rand-embd.npy')
target = convert_qrels_to_target(
    '/home/sumanta/Documents/Mongoose-data/trec-data/benchmarkY1-train/train.pages.cbor-toplevel.qrels', paraids)
page_paras = get_page_paras(
    '/home/sumanta/Documents/Mongoose-data/trec-data/benchmarkY1-train/train.pages.cbor-article.qrels')

test_pages = random.sample(page_paras.keys(),len(page_paras.keys())//4)
train_pages = page_paras.keys() - test_pages
test_dat = []
test_labels = []
for pg in test_pages:
    paras = page_paras[pg]
    for p in paras:
        test_dat.append(rand_embd_dat[list(paraids).index(p)])
        test_labels.append(target[list(paraids).index(p)])
train_dat = []
train_labels = []
for pg in train_pages:
    paras = page_paras[pg]
    for p in paras:
        train_dat.append(rand_embd_dat[list(paraids).index(p)])
        train_labels.append(target[list(paraids).index(p)])
