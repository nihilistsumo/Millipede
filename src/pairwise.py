#!/usr/bin/python3

import numpy as np
import random
import pickle

from time import time
import matplotlib.pyplot as plt
from matplotlib import offsetbox
from scipy import stats
from sklearn import (manifold, datasets, decomposition, ensemble,
                     discriminant_analysis, random_projection, metrics)
import math, sys

def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

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

def norm(arr):
    # MIN_VAL is used to replace 0 to avoid div by 0 later
    MIN_VAL = 1.0e-20
    norm_arr = []
    for v in arr:
        norm_arr.append(v)
    sum = 0
    for d in arr:
        sum = sum + d
    for i in range(arr.size):
        if arr[i]<1:
            norm_arr[i] = MIN_VAL
        else:
            norm_arr[i] = arr[i]/float(sum)
    return norm_arr

def bhattacharya_dist(dat):
    dist_mat = []
    for i in range(dat.shape[0]):
        curr_dist = np.zeros(dat.shape[0])
        for j in range(dat.shape[0]):
            p1dist = np.array(norm(dat[i]))
            p2dist = np.array(norm(dat[j]))
            s = 0.0
            for x in range(d1.size):
                s = s + math.sqrt(d1[x]*d2[x])
            curr_dist[j] = -math.log(s)
        dist_mat.append(curr_dist)
    return np.array(dist_mat)

def kldiv_sim(dat):
    dist_mat = []
    for i in range(dat.shape[0]):
        curr_dist = np.zeros(dat.shape[0])
        for j in range(dat.shape[0]):
            p1dist = np.array(norm(dat[i]))
            p2dist = np.array(norm(dat[j]))
            curr_dist[j] = (p1dist * np.log(p1dist/p2dist)).sum()
        dist_mat.append(curr_dist)
    return np.array(dist_mat)

def pairwise_dist(data, labels, page, m):
    dist_mat = []
    bool_label = []
    print("Calculating for " + page +" using metric " + m)

    if m.lower() == "kldiv":
        dist_mat = kldiv_sim(data)
    elif m.lower() in {"additive_chi2", "chi2", "linear", "poly", "polynomial", "rbf", "laplacian", "sigmoid", "cosine"}:
        dist_mat = metrics.pairwise.pairwise_kernels(data, metric=m)
    elif m.lower() in {"cityblock","cosine","euclidean","l1","l2","manhattan"}:
        dist_mat = metrics.pairwise_distances(data, metric=m)
    else:
        dist_mat = kldiv_sim(data)

    for i in range(data.shape[0]):
        curr_label = np.full(data.shape[0],False)
        for j in range(data.shape[0]):
            if labels[i] == labels[j]:
                curr_label[j] = True
        bool_label.append(curr_label)
    return dist_mat, np.array(bool_label)

def plot_result(mat, bool_label, page):
    true_kldivs = []
    false_kldivs = []
    for i in range(bool_label.shape[0]):
        for j in range(i + 1, bool_label.shape[0]):
            if bool_label[i][j]:
                true_kldivs.append(mat[i][j])
            else:
                false_kldivs.append(mat[i][j])
    fig, axs = plt.subplots(1, 2, figsize=(25, 5))
    axs[0].set_ylim(top=max(true_kldivs + false_kldivs))
    axs[1].set_ylim(top=max(true_kldivs + false_kldivs))
    true_klmean = sum(true_kldivs) / len(true_kldivs)
    false_klmean = sum(false_kldivs) / len(false_kldivs)
    axs[0].bar(np.arange(len(true_kldivs)), true_kldivs, color='g')
    axs[0].plot([true_klmean] * len(true_kldivs))
    axs[1].bar(np.arange(len(false_kldivs)), false_kldivs, color='r')
    axs[1].plot([false_klmean] * len(false_kldivs))
    plt.title(page)
    plt.show()

def calc_pairwise(page_paras_dict, method, count):
    c = 0
    for page in page_paras_dict.keys():
        paras = page_paras_dict[page]
        para_vecs = []
        para_targets = []
        for para in paras:
            para_vecs.append(rand_embd_dat[list(paraids).index(para)])
            para_targets.append(target[list(paraids).index(para)])
        X = np.array(para_vecs)
        y = np.array(para_targets)
        dist_mat, labels = pairwise_dist(X, y, page, method)
        plot_result(dist_mat, labels, page)
        c = c+1
        if c>=int(count):
            break

def plot_result_allp(mean_diffs, method):
    diffs = []
    pages = []
    for p in mean_diffs.keys():
        pages.append(p)
        if math.isnan(mean_diffs[p][0]) or math.isnan(mean_diffs[p][1]) or mean_diffs[p][1]<np.finfo(float).tiny:
            diffs.append(0)
        else:
            diffs.append(mean_diffs[p][0]/mean_diffs[p][1])
    fig, axs = plt.subplots(1, 1, figsize=(25, 5))
    axs.set_ylim(top=max(diffs) + 0.001)
    axs.bar(np.arange(len(diffs)), diffs, color='g')

    axs.set_title("Scores by page using "+method)
    #ax.set_xticks(ind + width / 2)
    axs.set_xticklabels(pages)
    #ax.yaxis.set_units(inch)
    axs.autoscale_view()

    plt.show()

def calc_pairwise_allp(page_paras_dict, method):
    '''
    mean_dict = dict()
    mean_diff_dict = dict()
    for page in page_paras_dict.keys():
        paras = page_paras_dict[page]
        para_vecs = []
        para_targets = []
        for para in paras:
            para_vecs.append(rand_embd_dat[list(paraids).index(para)])
            para_targets.append(target[list(paraids).index(para)])
        X = np.array(para_vecs)
        y = np.array(para_targets)
        dist_mat, labels = pairwise_dist(X, y, page, method)

        true_kldivs = []
        false_kldivs = []
        for i in range(labels.shape[0]):
            for j in range(i + 1, labels.shape[0]):
                if labels[i][j]:
                    true_kldivs.append(dist_mat[i][j])
                else:
                    false_kldivs.append(dist_mat[i][j])

        if page.startswith("enwiki:Philosophy%20of%20human"):
            print("This is the one")
            x = sum(true_kldivs)
            print(true_kldivs)

        true_klmean = sum(true_kldivs) / len(true_kldivs)
        true_stderr = stats.sem(true_kldivs)
        false_klmean = sum(false_kldivs) / len(false_kldivs)
        false_stderr = stats.sem(false_kldivs)
        if method.lower() in {"additive_chi2", "chi2", "linear", "poly", "polynomial", "rbf", "laplacian", "sigmoid",
                         "cosine"}:
            mean_diff_dict[page] = (false_klmean - true_klmean, true_klmean)
        else:
            mean_diff_dict[page] = (true_klmean - false_klmean, true_klmean)
        mean_dict[page] = (true_klmean, true_stderr, false_klmean, false_stderr)

    save_obj(mean_dict, "/home/sumanta/Documents/Porcupine-data/Porcupine_aspvec_python/obj/pairwise_mean_dict")
    save_obj(mean_diff_dict, "/home/sumanta/Documents/Porcupine-data/Porcupine_aspvec_python/obj/pairwise_mean_diff_dict")
    '''
    plot_result_allp(load_obj("/home/sumanta/Documents/Porcupine-data/Porcupine_aspvec_python/obj/pairwise_mean_diff_dict"), method)



paraids = np.load('/home/sumanta/Documents/Porcupine-data/Porcupine_aspvec_python/obj/aspvec-paraids.npy')
aspids = np.load('/home/sumanta/Documents/Porcupine-data/Porcupine_aspvec_python/obj/aspvec-aspids.npy')
aspvals = np.load('/home/sumanta/Documents/Porcupine-data/Porcupine_aspvec_python/obj/aspvec-aspvals.npy')
rand_embd_dat = np.load('/home/sumanta/Documents/Porcupine-data/Porcupine_aspvec_python/obj/aspvec-rand-embd.npy')
target = convert_qrels_to_target(
    '/home/sumanta/Documents/Mongoose-data/trec-data/benchmarkY1-train/train.pages.cbor-toplevel.qrels', paraids)
page_paras = get_page_paras(
    '/home/sumanta/Documents/Mongoose-data/trec-data/benchmarkY1-train/train.pages.cbor-article.qrels')
'''
Methods:
cos: cosine similarity
bhatt: bhattacharya distance
lker: similarity between vectors using linear kernel
pker: similarity between vectors using poly kernel
'''
option = int(sys.argv[1])
if option==1:
    calc_pairwise(page_paras, sys.argv[2], sys.argv[3])
elif option==2:
    calc_pairwise_allp(page_paras, sys.argv[2])