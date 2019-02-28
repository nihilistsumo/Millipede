#!/usr/bin/python3

import sys,random, itertools

def get_qrels(qrels_filepath):
    qrels_map = dict()
    with open(qrels_filepath) as f:
        for line in f:
            q = line.split(" ")[0]
            page = q.split("/")[0]
            sec = q[len(page)+1:]
            para = line.split(" ")[2]
            rank = int(line.split(" ")[3])
            if page in qrels_map.keys():
                page_dict = qrels_map.get(page)
                if sec in page_dict.keys():
                    qrels_map.get(page).get(sec).append((para,rank))
                else:
                    paralist = [(para,rank)]
                    qrels_map.get(page)[sec] = paralist
            else:
                paralist = [(para,rank)]
                secdict = dict()
                secdict[sec] = paralist
                qrels_map[page] = secdict
    return qrels_map

def get_qrels(qrels_filepath, art_qrels_filepath):
    qrels_map = dict()
    art_qrels_map = dict()
    with open(art_qrels_filepath,'r') as art:
        for line in art:
            page = line.split(" ")[0]
            para = line.split(" ")[2]
            if page not in art_qrels_map.keys():
                paras = [line.split(" ")[2]]
                art_qrels_map[page] = paras
            else:
                art_qrels_map[page].append(para)

    with open(qrels_filepath) as f:
        for line in f:
            q = line.split(" ")[0]
            page = q.split("/")[0]
            sec = q[len(page)+1:]
            para = line.split(" ")[2]
            rank = int(line.split(" ")[3])
            if page not in qrels_map.keys():
                para_dict = dict()
                para_dict[para] = [sec]
                qrels_map[page] = para_dict
            else:
                para_dict = qrels_map[page]
                if para not in qrels_map[page].keys():
                    qrels_map[page][para] = [sec]
                else:
                    qrels_map[page][para].append(sec)
    return qrels_map

def write_triples(qrels, out_filepath):
    qrels_map = get_qrels(qrels)
    triples_dict = dict()
    for page in qrels_map.keys():
        triples = []
        sec_dict = qrels_map[page]
        print(page+"\n")
        for sec in sec_dict.keys():
            rel_paras = qrels_map[page][sec]
            #if ("45f4822af5c0285172edccd89c61ef364bd702bd",2) in rel_paras:
            #    print("caught")
            if len(rel_paras)<2:
                continue
            non_rel_paras = []
            # History section
            for s in sec_dict.keys():
                if s != sec:
                    non_rel_paras = non_rel_paras + sec_dict[s]
            if len(non_rel_paras) > 0:
                for i in range(len(rel_paras)-1):
                    for j in range(i+1, len(rel_paras)):
                        for non_p in non_rel_paras:
                            triples.append((rel_paras[i], rel_paras[j], non_p))
            print(".", end='')
        triples_dict[page] = triples
        print(" Done")
    with open(out_filepath,'a+') as out:
        for p in triples_dict:
            for t in triples_dict[p]:
                out.write(p+" "+t[0][0]+" "+t[1][0]+" "+t[2][0]+" "+str(t[0][1])+str(t[1][1])+str(t[2][1])+"\n")

def write_triples_new(qrels, art_qrels, out_filepath):
    qrels_map = get_qrels(qrels, art_qrels)
    triples_dict = dict()
    for page in qrels_map.keys():
        triples = []
        paras_set = qrels_map[page].keys()
        print(page+"\n")
        for trip in itertools.combinations(paras_set,3):
            odd = "none"
            if len(set(qrels_map[page][trip[0]]) & set(qrels_map[page][trip[1]]) & set(qrels_map[page][trip[2]])) > 0:
                difficult = 1
            else:
                difficult = 0
                if len(set(qrels_map[page][trip[0]]) & set(qrels_map[page][trip[1]])) > 0:
                    odd = trip[2]
                elif len(set(qrels_map[page][trip[1]]) & set(qrels_map[page][trip[2]])) > 0:
                    odd = trip[0]
                else:
                    odd = trip[1]
            triples.append((trip[0], trip[1], trip[2], odd, difficult))
        print(".", end='')
        triples_dict[page] = triples
        print(" Done")
    with open(out_filepath,'a+') as out:
        for p in triples_dict:
            for t in triples_dict[p]:
                out.write(p+" "+t[0]+" "+t[1]+" "+t[2]+" "+t[3]+" "+str(t[4])+"\n")

def print_random_triples(triples_file):
    test_trip = dict()
    with open(triples_file) as f:
        for line in f:
            page = line.split(" ")[0]
            p1 = line.split(" ")[1]
            p2 = line.split(" ")[2]
            p3 = line.split(" ")[3]
            ranks = line.split(" ")[4]
            if page in test_trip.keys():
                test_trip[page].append((p1, p2, p3, ranks))
            else:
                para_list = [(p1, p2, p3, ranks)]
                test_trip[page] = para_list
    for p in test_trip.keys():
        for tup in sample(test_trip[p], 4):
            print(p + " " + tup[0] + " " + tup[1] + " " + tup[2] + " " + tup[3])

def remove_duplicate_from_qrels(qrels):
    all_paras_list = []
    all_paras = set()
    with open(qrels) as f:
        for line in f.readlines():
            all_paras.add(line.split(" ")[2])
            all_paras_list.append(line.split(" ")[2])
    print("No of unique paras: "+str(len(all_paras)))
    print("No of all paras: "+str(len(all_paras_list)))
    dup_paras = set()
    for p in all_paras:
        if all_paras_list.count(p) > 1:
            dup_paras.add(p)
    unique_paras = all_paras.difference(dup_paras)
    with open(qrels) as f:
        lines = f.readlines()
        for line in lines:
            if line.split(" ")[2] in unique_paras:
                print(line)

write_triples_new(sys.argv[1], sys.argv[2], sys.argv[3])
#remove_duplicate_from_qrels(sys.argv[1])