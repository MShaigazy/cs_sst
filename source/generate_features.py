# -*- coding: utf-8 -*-
#!/usr/bin/env python

#features from a webanno tsv file, exported in the following format:
# @author: Hector Martinez based on previous work by Barbara Plank/Dirk Hovy/Anders Johannsen
##
# FILE MUST CONTAIN POS TAGS!
import argparse
import logging
import codecs
import sys, os
import re
from collections import defaultdict, Counter
from uniwordnet.dannet import DannetLoader
from lillelemma.sto_lemmatizer import StoLemmatizer
#from confusion_matrices_sst import wholetags, nopos, bioprefix, supersense



class CostSensitiveFeatureRow():
    def __init__(self,annotated_supersense,SSCM,confusiontype):
        #print annotated_supersense
        if annotated_supersense in SSCM:

            rest_of_senses = SSCM[annotated_supersense]
            del rest_of_senses[annotated_supersense] #removes the diagonal element in rest_of_senses to make sure there are no repetions when concatenating possible labels in the header


            self.supersenses = [annotated_supersense]+rest_of_senses.keys()
            self.supersenses_integers = [] #TODO!!!!
            self.costs = []
            for sense in self.supersenses:
                self.costs.append(SSCM[annotated_supersense][sense])
        else:
            self.supersenses = [annotated_supersense]
            self.supersenses_integers = [-1] #TODO!!!!
            self.costs = [1.0]


    def header(self):
        #1:2.0 2:1.0 ab1_expect_2| a b -- should look like this more or less
        tags = []
        for i in range(len(self.supersenses)):
            tags.append(self.supersenses[i]+":"+str(self.costs[i])) #DEVELOPMENT!!
        return " ".join(tags)

class SentenceFromWebAnno():

    def __init__(self, id):
        self.id = id
        self.coarsepos=[]
        self.forms=[]
        self.annotated_supersenses=[]
        self.most_frequent_supersenses=[]
        self.lemmas = []

    def worditerator(self):
        for i in range(len(self.forms)):
            yield i, self.forms[i], self.coarsepos[i], self.lemmas[i], self.most_frequent_supersenses[i], self.annotated_supersenses[i]

    def __str__(self):
                return str(self.id)+" ".join(self.forms)


def get_supersense_cost_matrix(inputfile):
    D = defaultdict(Counter)
    for line in open(inputfile).readlines():
        if line.startswith("#"): #skip the header
            pass
        else:
            row, column, support, confusionvalue = line.strip().split("\t")
            support = float(support)
            cost = 1 - float(confusionvalue)
            if cost < 1.0: #i.e. if the confusion value is above 0.0, this line can be removed if all the possible values have to be expressed for training, even those with cost=1
                D[row][column] = cost

    return D


def get_lemma_and_mfs(checkpos,dannet,DanishLemmatizer,onto2supersense,form,pos):
        if pos in checkpos.keys():
            lemma=DanishLemmatizer.lemmatize(form,pos)
            s = dannet.synsets(lemma.lower()+"."+checkpos[pos])
            if s:
                ot = s[0].attrs()["ontological_type"].replace("(","").replace(")","")
                ontokey = checkpos[pos]+"+"+ot
                if ontokey in onto2supersense:
                    sst=onto2supersense[ontokey]
                else:
                    sst="_"
            else:
                sst="_"
        else:
            lemma = form.lower()
            sst="_"
        return lemma, sst



def get_sentences_with_lemmatization_and_mfs(inputfile,dannet,DanishLemmatizer,onto2supersense,checkpos):
    sentenceid = 0
    currentsentence = SentenceFromWebAnno(sentenceid)
    for line in codecs.open(inputfile,encoding="utf-8").readlines():
        line = line.strip()
        if len(line) < 1:

            sentenceid+=1
            yield currentsentence
            currentsentence = SentenceFromWebAnno(sentenceid)
        else:
            fields =line.split("\t")
            form = fields[0]
            coarsepos = fields[1]
            supersense = fields[2]
            currentsentence.forms.append(form)
            currentsentence.annotated_supersenses.append(supersense)
            currentsentence.coarsepos.append(coarsepos)
            lemma, mfs = get_lemma_and_mfs(checkpos,dannet,DanishLemmatizer,onto2supersense,form,coarsepos) #calculates lemma and MFS from the input
            currentsentence.lemmas.append(lemma)
            currentsentence.most_frequent_supersenses.append(mfs)


def main():
    parser = argparse.ArgumentParser(description="Create standard features for Twitter SST")
    parser.add_argument('corpus', help="TSV data in <form,PetrovPOS,SST> format, colons ';' replaced with '<COLON>' ")
    parser.add_argument('--class-map', help="Map for string class to integer")
    parser.add_argument('--cluster-file', help="Cluster file", type=argparse.FileType('r'))
    parser.add_argument('--embeddings', help="embedding file name", type=argparse.FileType('r'))
    parser.add_argument('--confusionmatrix', help="confusion matrix file generated with confusion_matrices_sst using the confusiontype parameter")
    parser.add_argument('--confusiontype',help="""wholetags (e.g.  B-noun.person vs I-verb.cognition)
                                                 supersense (e.g. noun.person vs. verb.plant)
                                                 nopos (e.g. cognition vs. communication, ignoring noun.x or verb.x)
                                                 bioprefix (headpos+directionality)
                                                 none (standard unweighted)
                                                 """, required=True)

    #parser.add_argument('--onto2supersenses', help="embedding file name", type=argparse.FileType('r'),optional=False)

    args = parser.parse_args()


    ## INITIALIZE LOCAL DATA STRUCTURES - MAP TO SUPERSENSES, DANNET, LEMMATIZER
    #TODO: BROWN CLUSTERS , EMBEDDINGS, MAYBE TOPIC MODELS WEATHER PERMITTING

    checkpos = {} #TODO: Add also Danish Parole tags just in case
    checkpos["ADJ"] = "a"
    checkpos["NOUN"] = "n"
    checkpos["VERB"] = "v"

    ontotypetosupersense={}
    for line in open("../data/res/map_onto_to_supersense.tsv"):
        ontokey, freq, values = line.strip().split("\t")
        values = values.replace(" ","").split(";")
        for v in values:
            ontotypetosupersense[v[0]+"+"+ontokey]=v
    loader = DannetLoader('/Users/alonso/data/DanNet-2.2_csv')
    loader.load()
    dannet = loader.dannet


    #INITIALIZE CONFUSION MATRIX
    if args.confusiontype == "none": #NONE
        SSCM = {}
    else:
        SSCM = get_supersense_cost_matrix(args.confusionmatrix)

    DanishLemmatizer = StoLemmatizer()
    for sentence in get_sentences_with_lemmatization_and_mfs(args.corpus,dannet,DanishLemmatizer,ontotypetosupersense,checkpos):
        for tok_id, form, pos, lemma, mfs_supersense,annotated_supersense in sentence.worditerator():
            fr = CostSensitiveFeatureRow(annotated_supersense,SSCM,args.confusiontype)
            print "\t".join([fr.header(), pos, annotated_supersense])



if __name__ == "__main__":
    main()