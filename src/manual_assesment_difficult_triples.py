#!/usr/bin/python3

import sys,random

def find_difficult_triples(triples_file, manual_qrels):
    with open(triples_file, 'r') as f:
        lines = f.readlines()
    #man_qrels = "/home/sumanta/Documents/Dugtrio-data/parasim-manual-assesment.old/filtered-paragraph-manual-y2test.qrels"
    para_sec_dict = dict()
    with open(manual_qrels, 'r') as q:
        for l in q.readlines():
            para = l.split(" ")[2]
            sec = l.split(" ")[0]
            if para in para_sec_dict.keys():
                para_sec_dict[para].append(sec)
            else:
                para_sec_dict[para] = [sec]
    count = 1
    num_difficult = 0
    for line in lines:
        p1 = line.split(" ")[1]
        s1 = set(para_sec_dict[p1])
        p2 = line.split(" ")[2]
        s2 = set(para_sec_dict[p2])
        p3 = line.split(" ")[3]
        s3 = set(para_sec_dict[p3])
        if (len(s1 & s2 & s3) > 0):
            print(str(count)+" "+line)
            num_difficult+=1
            #print(str(s1) + " " + str(s2) + " " + str(s3) + "\n")
        count+=1
    print(str(num_difficult)+" difficult triples found from "+str(count-1))

find_difficult_triples(sys.argv[1], sys.argv[2])