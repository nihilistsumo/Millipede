#!/usr/bin/python3

import sys,random

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

def write_triples(qrels, out_filepath):
    qrels_map = get_qrels(qrels)
    triples_dict = dict()
    for page in qrels_map.keys():
        triples = []
        sec_dict = qrels_map[page]
        print(page+"\n")
        for sec in sec_dict.keys():
            rel_paras = qrels_map[page][sec]
            if len(rel_paras)<2:
                continue
            non_rel_paras = []
            for s in sec_dict.keys():
                if s!=sec:
                    non_rel_paras = non_rel_paras + sec_dict[s]
            for i in range(len(rel_paras)-1):
                for j in range(i+1, len(rel_paras)):
                    for non_p in non_rel_paras:
                        triples.append((rel_paras[i], rel_paras[j], non_p))
            print(".", end='')
        triples_dict[page] = triples
        print(" Done")
    with open(out_filepath,'a') as out:
        for p in triples_dict:
            for t in triples_dict[p]:
                out.write(p+" "+t[0][0]+" "+t[1][0]+" "+t[2][0]+" "+str(t[0][1])+str(t[1][1])+str(t[2][1])+"\n")

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

write_triples(sys.argv[1], sys.argv[2])