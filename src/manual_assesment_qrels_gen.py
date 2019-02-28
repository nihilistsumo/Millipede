#!/usr/bin/python3

import sys,random

def find_page_for_para(para, dict2, dict3):
    for p in dict2.keys():
        if para in dict2[p]:
            return 2,p
    for p in dict3.keys():
        if para in dict3[p]:
            return 3,p

def generate_qrels(assesment_file, art_qrels):
    rev_art_qrels_map = dict()
    with open(art_qrels, 'r') as art:
        for line in art:
            page = line.split(" ")[0]
            para = line.split(" ")[2]
            rev_art_qrels_map[para] = page
    with open(assesment_file,'r') as input:
        lines = input.readlines()
    with open(assesment_file,'w') as out:
        for line in lines:
            page = rev_art_qrels_map[line.split(" ")[0]]
            out.write(page+" "+line)

generate_qrels("/home/sumanta/Documents/Dugtrio-data/temp",
               "/home/sumanta/Documents/Dugtrio-data/parasim-manual-assesment/art-filtered-paragraph-manual-y2test.qrels")