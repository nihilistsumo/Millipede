#!/usr/bin/python3

import numpy as np
import random, sys

from time import time
import matplotlib.pyplot as plt
from matplotlib import offsetbox
from sklearn import (manifold, datasets, decomposition, ensemble,
                     discriminant_analysis, random_projection)
from scipy import special

def usage():
    print("python3 rand_embed.py paraids-file aspids-file aspvals-file aspbucket-file rand-embd-output-file\n")

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

def create_rand_bucket():
    remain_aspid = set()
    for a in range(ASP_COUNT):
        remain_aspid.add(a)
    rand_asp_bucket = []
    bucket_size = ASP_COUNT//NUM_BUCKETS + 1
    while len(remain_aspid)>bucket_size:
        curr_bucket = random.sample(remain_aspid,bucket_size)
        for asp in curr_bucket:
            remain_aspid.remove(asp)
        rand_asp_bucket.append(curr_bucket)
    rand_asp_bucket.append(remain_aspid)
    return rand_asp_bucket

def embed_rand(buckets, aspids, paraids, aspvals):
    embed_asp_data = []
    for i in range(len(paraids)):
        paraid = paraids[i]
        asp_arr = aspids[i]
        aspval_arr = aspvals[i]
        embed_asp_arr = []
        for b in buckets:

            # Commented part was used to store common asp frequency as score for current bucket
            #common_asps = set(asp_arr).intersection(b)
            #asp_match = len(common_asps)
            #embed_asp_arr.append(asp_match)

            common_asps = set(asp_arr).intersection(b)
            asp_arr_list = list(asp_arr)
            score = 0
            for a in common_asps:
                score = score + aspval_arr[asp_arr_list.index(a)]
            embed_asp_arr.append(score)
            #print(str(asp_match)+" ", end="")
        embed_asp_data.append(embed_asp_arr)
        if(i%100==0):
            print(str(len(paraids)-i)+" paras to go")
    return embed_asp_data

def sample_plot(data, labels, num_subplots):
    fig, axs = plt.subplots(10, 5, figsize=(5, 25))
    #print("data rows = "+str(data.shape[0])+", data cols = "+str(data.shape[1]))
    count = 0
    for i in range(data.shape[0]):
        for j in range(i+1,data.shape[0]):
            axi = count//5
            axj = count%5
            if labels[i] == labels[j]:
                axs[axi, axj].set_title("True Pair")
            axs[axi, axj].hist2d(data[i], data[j])
            count = count + 1
            #print(count)
    #plt.hist2d(data[0],data[1])
    plt.show()

def sample_hm(data, labels):
    plt.imshow(data, cmap='hot', interpolation='nearest')
    plt.show()

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

def sample_kldiv_hm(data, labels, page):
    klmat = []
    bool_label = []
    for i in range(data.shape[0]):
        curr_dist = np.zeros(data.shape[0])
        curr_label = np.full(data.shape[0],False)
        for j in range(data.shape[0]):
            p1dist = np.array(norm(data[i]))
            p2dist = np.array(norm(data[j]))
            #curr_dist[j] = special.kl_div(p1dist, p2dist)
            curr_dist[j] = (p1dist * np.log(p1dist/p2dist)).sum()
            if labels[i] == labels[j]:
                curr_label[j] = True
        klmat.append(curr_dist)
        bool_label.append(curr_label)
    #sample_hm(np.array(klmat), labels)
    klmat = np.array(klmat)
    bool_label = np.array(bool_label)
    true_kldivs = []
    false_kldivs = []
    for i in range(bool_label.shape[0]):
        for j in range(i+1,bool_label.shape[0]):
            if bool_label[i][j]:
                true_kldivs.append(klmat[i][j])
            else:
                false_kldivs.append(klmat[i][j])
    fig, axs = plt.subplots(1, 2, figsize=(25, 5))
    axs[0].set_ylim(top=max(true_kldivs+false_kldivs))
    axs[1].set_ylim(top=max(true_kldivs+false_kldivs))
    true_klmean = sum(true_kldivs)/len(true_kldivs)
    false_klmean = sum(false_kldivs)/len(false_kldivs)
    axs[0].bar(np.arange(len(true_kldivs)),true_kldivs,color='g')
    axs[0].plot([true_klmean]*len(true_kldivs))
    axs[1].bar(np.arange(len(false_kldivs)),false_kldivs,color='r')
    axs[1].plot([false_klmean] * len(false_kldivs))
    plt.title(page)
    plt.show()



#----------------------------------------------------------------------
#------Copied from plot_lle_digits.py----------------------------------
# Scale and visualize the embedding vectors
def plot_embedding(X, title=None):
    x_min, x_max = np.min(X, 0), np.max(X, 0)
    X = (X - x_min) / (x_max - x_min)

    stub_arr = []
    for j in range(X.shape[0]):
        stub_arr.append(digits.images[0])

    plt.figure()
    ax = plt.subplot(111)
    for i in range(X.shape[0]):
        plt.text(X[i, 0], X[i, 1], str(y[i]),
                 color=plt.cm.Set1(y[i] / 10.),
                 fontdict={'weight': 'bold', 'size': 9})

    if hasattr(offsetbox, 'AnnotationBbox'):
        # only print thumbnails with matplotlib > 1.0
        shown_images = np.array([[1., 1.]])  # just something big
        for i in range(X.shape[0]):
            dist = np.sum((X[i] - shown_images) ** 2, 1)
            if np.min(dist) < 4e-3:
                # don't show points that are too close
                continue
            shown_images = np.r_[shown_images, [X[i]]]
            '''
            imagebox = offsetbox.AnnotationBbox(offsetbox.OffsetImage(stub_arr[i], cmap=plt.cm.gray_r), X[i])
            ax.add_artist(imagebox)
            '''
    plt.xticks([]), plt.yticks([])
    if title is not None:
        plt.title(title)
#------------------------------------------------------------------------

random.seed(100)

ASP_COUNT = 17979934
NUM_BUCKETS = 100
if len(sys.argv)<6:
    usage()
    sys.exit(0)
#paraids = np.load('/home/sumanta/Documents/Porcupine-data/Porcupine_aspvec_python/obj/aspvec-paraids.npy')
#aspids = np.load('/home/sumanta/Documents/Porcupine-data/Porcupine_aspvec_python/obj/aspvec-aspids.npy')
#aspvals = np.load('/home/sumanta/Documents/Porcupine-data/Porcupine_aspvec_python/obj/aspvec-aspvals.npy')
paraids = np.load(sys.argv[1])
aspids = np.load(sys.argv[2])
aspvals = np.load(sys.argv[3])

if len(sys.argv) == 7 and sys.argv[6] == 'c':
    asp_buc_np = np.array(create_rand_bucket())
    print("Creating random bucket")
    np.save('/home/sumanta/Documents/Porcupine-data/Porcupine_aspvec_python/obj/aspvec-embd-bucket.npy', asp_buc_np)
    print("Buckets created")

#asp_buc_np = np.load('/home/sumanta/Documents/Porcupine-data/Porcupine_aspvec_python/obj/aspvec-embd-bucket.npy')
asp_buc_np = np.load(sys.argv[4])
asp_embd_dat = embed_rand(asp_buc_np, aspids, paraids, aspvals)
asp_embd_dat_np = np.array(asp_embd_dat)
#np.save('/home/sumanta/Documents/Porcupine-data/Porcupine_aspvec_python/obj/aspvec-rand-embd-sumscore.npy', asp_embd_dat_np)
np.save(sys.argv[5])

print(len(asp_buc_np))
print(len(asp_buc_np[0]))
print(len(asp_buc_np[len(asp_buc_np)-1]))

'''
rand_embd_dat = np.load('/home/sumanta/Documents/Porcupine-data/Porcupine_aspvec_python/obj/aspvec-rand-embd.npy')
target = convert_qrels_to_target(
    '/home/sumanta/Documents/Mongoose-data/trec-data/benchmarkY1-train/train.pages.cbor-toplevel.qrels', paraids)
page_paras = get_page_paras(
    '/home/sumanta/Documents/Mongoose-data/trec-data/benchmarkY1-train/train.pages.cbor-article.qrels')
MAX_PARAS_IN_PAGE = 10
MAX_SUBPLOTS = MAX_PARAS_IN_PAGE * (MAX_PARAS_IN_PAGE-1)//2
for page in page_paras.keys():
    paras = page_paras[page]
    para_vecs = []
    para_targets = []
    for para in paras:
        para_vecs.append(rand_embd_dat[list(paraids).index(para)])
        para_targets.append(target[list(paraids).index(para)])
    X = np.array(para_vecs)
    y = np.array(para_targets)
    #print("X shape = "+str(X.shape)+", y shape = "+str(y.shape)+", y size = "+str(y.size))
    #if(X.shape[0]<51):
        #sample_plot(X, y, MAX_SUBPLOTS)
        #sample_hm(X, y)
    sample_kldiv_hm(X, y, page)
    
    n_samples, n_features = X.shape

    # ----------------------------------------------------------------------
    # t-SNE embedding of the digits dataset
    print("Computing t-SNE embedding")
    tsne = manifold.TSNE(n_components=2, init='pca', random_state=0)
    t0 = time()
    X_tsne = tsne.fit_transform(X)

    plot_embedding(X_tsne, "t-SNE embedding of the paras (time %.2fs)" %(time() - t0))

    plt.show()
    break
    '''


            
