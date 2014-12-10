# -*- coding: utf-8 -*-
#!/usr/bin/env python

#features from a webanno tsv file, exported in the following format:
# @author: Hector Martinez based on previous work by Barbara Plank/Dirk Hovy/Anders Johannsen
##
# FILE MUST CONTAIN PETROV POS TAGS!
import argparse
import copy
import logging
import codecs
import sys, os
import re
import numpy as np
from scipy.spatial.distance import cosine
from collections import defaultdict, Counter
from uniwordnet.dannet import DannetLoader
from lillelemma.sto_lemmatizer import StoLemmatizer
#from confusion_matrices_sst import wholetags, nopos, bioprefix, supersense
import sys

import math





class CostSensitiveFeatureRow():
    def __init__(self,annotated_supersense,SSCM, weigthmode, identifier,sense_to_integer,separator):
            if weigthmode == "iw": #Print only the first one for importance weighting
                self.supersenses = [annotated_supersense]
                self.costs = []
                for sense in self.supersenses:
                    self.costs.append(SSCM[annotated_supersense][sense])
                self.supersenses_integers = [sense_to_integer[x] for x in self.supersenses]
            elif weigthmode == "cs":
                if annotated_supersense in SSCM:
                    rest_of_senses = copy.deepcopy(SSCM[annotated_supersense])
                    del rest_of_senses[annotated_supersense] #removes the diagonal element in rest_of_senses to make sure there are no repetions when concatenating possible labels in the header
                    self.supersenses = [annotated_supersense]+rest_of_senses.keys()
                    self.costs = []
                    for sense in self.supersenses:
                        self.costs.append(SSCM[annotated_supersense][sense])
                else:
                    self.supersenses = [annotated_supersense]
                    self.costs = [1.0]
                self.supersenses_integers = [sense_to_integer[x] for x in self.supersenses]
            elif weigthmode == "regular":
                self.supersenses = [annotated_supersense]
                self.costs = []
                self.supersenses_integers = self.supersenses
            self.feats = defaultdict(dict)
            self.identifier = identifier
            self.separator = separator

    def header(self):
        #1:2.0 2:1.0 ab1_expect_2| a b -- should look like this more or less
        tags = []
        if len(self.costs) > 0:
            for i in range(len(self.supersenses_integers)):
                tags.append(self.supersenses_integers[i]+self.separator+str(self.costs[i]))
        else:
            tags.append(self.supersenses_integers[0])
        tags.append(self.identifier)
        return " ".join(tags)

    def __str__(self):
        a = []
        for namespace in sorted(self.feats.keys()):
            a.append(namespace +" "+self.feats[namespace])
        return htmlescape(self.header()+"|"+" |".join(a))

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


def f_zipperwordwindow(index,wordlist):

    signlist = ["-"] * len(wordlist[:index]) + [""] +  ["+"] * (len(wordlist[index:]) -1)
    return " ".join([s+w for s,w in zip(signlist,wordlist)])


def featnames(id,windowsize): #"generates the name for w-2,,w+2 style features"
    names = []
    for x in range(windowsize*2+1):
        suffix = x-windowsize
        names.append(id+"_"+(str(int(suffix))))
    return names

def vw_name(string):
    return string.replace(':', '<COLON>').replace('|', '<PIPE>').replace(' ', '_')

def htmlescape(text):
    #text = (text).decode('utf-8')

    from htmlentitydefs import codepoint2name
    d = dict((unichr(code), u'&%s;' % name) for code,name in codepoint2name.iteritems() if code!=38) # exclude "&"
    if u"&" in text:
        text = text.replace(u"&", u"&amp;")
    for key, value in d.iteritems():
        if key in text:
            text = text.replace(key, value)
    return text


def max_min_embed(embedingslist,dimensions, operation):
    maxvect = []
    for d in range(dimensions):
        acc = []
        for vector in range(len(embedingslist)):
            acc.append(embedingslist[vector][d])
        if operation == "max":
            maxvect.append(max(acc))
        elif operation == "min":
            maxvect.append(min(acc))
        #print >> sys.stderr,maxvect
    return maxvect


def get_embedding(word,embeddings,dimensions):
    embed = []
    if word in embeddings:
        embed=embeddings[word]
    else:
        embed = [0.0] * dimensions
    return embed


def featnamelist(pref,n):
    namelist = []
    for i in range(n):
        namelist.append(pref+"_"+str(i))
    return namelist

def f_embeddings(list, index, windowsize, embeddings,dimensions,normalization):

    if normalization:
        normlist = [normalization.get(word.lower(), word).lower() for word in list]
        list = normlist

    paddedlist = ["NOTANEMBEDDING"] * windowsize + list + ["NOTANEMBEDDING"] * windowsize
    index = index + windowsize
    embeds = []
    for word in paddedlist[(index-windowsize):index+windowsize+1]:
        embeds.append(get_embedding(word,embeddings,dimensions))

    cosines = []
    currentvector = embeds[windowsize]
    contextvectors = copy.deepcopy(embeds)
    del contextvectors[windowsize]
    for vector in contextvectors:
        try:
            if sum(vector) !=0.0:
                c = cosine(currentvector,vector)
                if math.isnan(c):
                    c = 0.0
            else:
                c = 0.0
        except:
            c = 0.0
        cosines.append(c)

    weightedcontextvector = np.array([0.0] * dimensions)
    for vector in contextvectors:
        try:
            weightedcontextvector+=vector
        except:
            print >> sys.stderr, vector
            print >> sys.stderr, paddedlist

    weightedcontextvector+=currentvector
    weightedcontextvector+=currentvector

            # for i,f in enumerate(feats):
            # f_i=pref+"_"+str(i)+":"+f
            # featv.append(f_i)
    # print >> sys.stderr, weightedcontextvector
    # print >> sys.stderr, cosines
    # print >> sys.stderr, paddedlist[(index-windowsize):index+windowsize+1]
    outlist = []
    featnames = []
    outlist.extend(cosines)
    featnames.extend(featnamelist("c",len(cosines)))
    outlist.extend(weightedcontextvector)
    featnames.extend(featnamelist("w",dimensions))
    outlist.extend(max_min_embed(embeds,dimensions,"max"))
    featnames.extend(featnamelist("h",dimensions)) #high is for max
    outlist.extend(max_min_embed(embeds,dimensions,"min")) #l is for low
    featnames.extend(featnamelist("l",dimensions))


    #return " ".join([str(c) for c in outlist][:40])
    return " ".join([name+":"+str(value) for name,value in zip(featnames,outlist)])



def f_wordwindow(list, index, windowsize, name): #for [a,b,c,d,e], i=2 and windowsize=2, returns [a,b,c,d] with headers for each value
    paddedlist = ["^","_"] + list + ["_","$"]
    index = index + windowsize
    values = paddedlist[(index-windowsize):index+windowsize+1]
    names = featnames(name, windowsize)
    result = []
    for n, v in zip(names, values):
        result.append(vw_name(n+"="+v))
    return " ".join(result)


def f_brownclusters(word,browndict):
    word = word.lower()
    clusterid = browndict.get(word)
    feats = []
    if clusterid:
        feats.append("c2=" + clusterid[0:2])  #prefix 2
        feats.append("c4=" + clusterid[0:4])  #prefix 4
        feats.append("c6=" + clusterid[0:6])  #prefix 6
        feats.append("c8=" + clusterid[0:8])  #prefix 8
        feats.append("c10=" + clusterid[0:10])  #prefix 10
        feats.append("c12=" + clusterid[0:12])  #prefix 12
        feats.append("c14=" + clusterid[0:14])  #prefix 14
        feats.append("c16=" + clusterid[0:16])  #prefix 16
    else:
        feats.append("c2=_")
        feats.append("c4=_")
        feats.append("c6=_")
        feats.append("c8=_")
        feats.append("c10=_")
        feats.append("c12=_")
        feats.append("c14=_")
        feats.append("c16=_")
    return " ".join(feats)




def f_morphology(word, pos):
        feats = []
        # check capitalization
        if word[0].isupper() and not word in ["URL", "NUMBER"]:
            feats.append("caps")  #first char is uppercase

        # check if contains digits
        if "0" in word or pos == "AO" or pos == "AC":
            feats.append("num")

        # check if contains ' (possesive)
        if "'" in word:
            feats.append("possessive")

        # check if contains hyphen
        if "-" in word:
            feats.append("hyphen")

        # single character
        if len(word) == 1:
            feats.append("single")

        # 3char suffix
        if len(word) > 4:
            feats.append("suffix=" + word[-3:])
        else:
            feats.append("suffix=_")

        # 3char prefix
        if len(word) > 4:
            feats.append("prefix=" + word[:3])
        else:
            feats.append("prefix=" + word)

        # if entire word is uppercase
        if word.isupper():
            feats.append("allUpper")
        # only letters
        if word.isalpha():
            feats.append("alphanum")
        result = []
        for c in word:
            if c.isupper():
                result.append('X')
            elif c.islower():
                result.append('x')
            elif c in '0123456789':
                result.append('d')
            else:
                result.append(c)
        feats.append("shape="+re.sub(r"x+", "x*", ''.join(result)))

        if pos == "NP":
            feats.append('proper')

        return " ".join(feats)


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



def get_lemma_and_mfs_en(checkpos,wordnet,lemmatizer,form,pos):
        sst = "_"
        if pos in checkpos.keys():
            lemma=lemmatizer.lemmatize(form.lower(),checkpos[pos])
            try:
                sst = wordnet.synsets(form,checkpos[pos])[0].lexname
            except KeyError:
                sst = "notinwn"
            except IndexError:
                sst = "notinwn"
        else:
            lemma = form.lower()
            sst="_"
        return lemma, sst

def get_lemma_and_mfs_da(checkpos,dannet,DanishLemmatizer,onto2supersense,form,pos):
        if dannet == None or DanishLemmatizer == None:
            return (form.upper(), "sense.debug")


        if pos in checkpos.keys():
            lemma=DanishLemmatizer.lemmatize(form,pos)
            s = dannet.synsets(lemma.lower()+"."+checkpos[pos])
            if s:
                ot = s[0].attrs()["ontological_type"].replace("(","").replace(")","")
                ontokey = checkpos[pos]+"+"+ot
                if ontokey in onto2supersense:
                    sst=onto2supersense[ontokey]
                else:
                    sst="notinwn"
            else:
                sst="notinwn"
        else:
            lemma = form.lower()
            sst="_"
        return lemma, sst



def get_sentences_with_lemmatization_and_mfs(inputfile,wordnet,lemmatizer,onto2supersense,checkpos,lang):
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
            if lang == "da":
                lemma, mfs = get_lemma_and_mfs_da(checkpos,wordnet,lemmatizer,onto2supersense,form,coarsepos) #calculates lemma and MFS from the input
            elif lang == "en":
                lemma, mfs = get_lemma_and_mfs_en(checkpos,wordnet,lemmatizer,form,coarsepos) #calculates lemma and MFS from the input
            currentsentence.lemmas.append(lemma)
            currentsentence.most_frequent_supersenses.append(mfs)

def readclusters(cluster_file):
    words2ids = {}
    for l in open(cluster_file).readlines():
        fields = l.strip().split("\t")
        clusterId = fields[0]
        word = fields[1]
        words2ids[word] = clusterId
    return words2ids

def main():
    parser = argparse.ArgumentParser(description="Create standard features for Twitter SST")
    parser.add_argument('corpus', help="TSV data in <form,PetrovPOS,SST> format, colons ';' replaced with '<COLON>' ")
    parser.add_argument('--classmap', help="Map for string class to integer")
    parser.add_argument('--embeddings', help="embedding file name")
    parser.add_argument('--confusionmatrix', help="confusion matrix file generated with confusion_matrices_sst using the confusiontype parameter")
    parser.add_argument('--normalization-dict', help="Normalization dictionary")
    parser.add_argument('--weightmode', help="either iw for importance weighting (only provides goldclass:weight without the other classes, or cs for full cost-sensitive, or regular for just majority-class input", default="regular")
    parser.add_argument('--separator', help="header separator", default=":")

    parser.add_argument('--lang', help="en or da", default="da")



    #parser.add_argument('--onto2supersenses', help="embedding file name", type=argparse.FileType('r'),optional=False)
    args = parser.parse_args()

    debug = False

    ## INITIALIZE LOCAL DATA STRUCTURES - MAP TO SUPERSENSES, DANNET, LEMMATIZER


    checkpos = {} #TODO: Add also Danish Parole tags just in case


    if args.lang == "da":
        checkpos["ADJ"] = "a"
        checkpos["NOUN"] = "n"
        checkpos["VERB"] = "v"

        browndict = readclusters("../data/res/brownpaths_clarin_500")
        ontotypetosupersense={}

        for line in open("../data/res/map_onto_to_supersense.tsv"):
            ontokey, freq, values = line.strip().split("\t")
            values = values.replace(" ","").split(";")
            for v in values:
                ontotypetosupersense[v[0]+"+"+ontokey]=v

        sense_to_integer={}
        for line in open("../data/res/da_map_bio.txt").readlines():
            line = line.strip()
            if line:
                val,key = line.split("\t")
                sense_to_integer[key] = val

            lemmatizer = StoLemmatizer()
            loader = DannetLoader('/Users/alonso/data/DanNet-2.2_csv')
            loader.load()
            wordnet = loader.dannet

    elif args.lang == "en":
        checkpos = {"NOUN": 'n', "VERB": 'v', "ADJ": "a", "FW": "n", "JJ": "a",
               "JJR": "a", "JJS": "a", "MD": "v", "NN": "n", "NNS": "n", "NNP": "n", "NNPS": "n",
               "RB": "r", "RBR": "r", "RBS": "r", "VB": "v", "VBD": "v", "VBG": "v", "VBN": "v", "VBP": "v", "VBZ": "v", "WRB": "r"}
        from nltk.corpus import wordnet
        ontotypetosupersense = None
        from nltk.stem.wordnet import WordNetLemmatizer
        lemmatizer = WordNetLemmatizer()
        browndict = readclusters("../data/res/eng_brownpaths.txt.ukwac")
        sense_to_integer={}
        for line in open("../data/res/en_map_bio.txt").readlines():
            line = line.strip()
            if line:
                val,key = line.split("\t")
                sense_to_integer[key] = val

    normalization = {}
    if args.normalization_dict:
        normalization = dict(tuple(line.strip().split("\t"))
                     for line in codecs.open(args.normalization_dict, encoding='utf-8'))

    #INITIALIZE CONFUSION MATRIX
    embeddings={}
    for line in codecs.open(args.embeddings,encoding="utf-8").readlines():
        line = line.strip()
        if line:
            a= line.split(" ")
            embeddings[a[0]] = np.array([float(v) for v in a[1:]]) #cast to float, otherwise we cannot operate
            dimensions = len(a[1:])

    SSCM = {}
    if args.confusionmatrix != None: #NONE
         SSCM = get_supersense_cost_matrix(args.confusionmatrix)


    for sentence in get_sentences_with_lemmatization_and_mfs(args.corpus,wordnet,lemmatizer,ontotypetosupersense,checkpos,args.lang):
        for tok_id, form, pos, lemma, mfs_supersense,annotated_supersense in sentence.worditerator():
            fr = CostSensitiveFeatureRow(annotated_supersense,SSCM, args.weightmode, "'"+str(sentence.id)+":"+str(tok_id),sense_to_integer, args.separator)
            fr.feats["wordwindow"] = f_wordwindow(sentence.forms,tok_id,2, "w")
            fr.feats["lemmawindow"] = f_wordwindow(sentence.lemmas,tok_id,2, "l")
            fr.feats["poswindow"] = f_wordwindow(sentence.coarsepos,tok_id,2, "p")
            fr.feats["sstwindow"] = f_wordwindow(sentence.most_frequent_supersenses,tok_id,2, "s")
            fr.feats["morphology"] = f_morphology(form, pos)
            fr.feats['brownclusters'] = f_brownclusters(form,browndict)
            fr.feats['embeddings'] = f_embeddings(sentence.forms,tok_id,2,embeddings,dimensions,normalization) # weighted average wa of the context embeddings, plus max and min, and cosine of the current word to the surrounding -2,+2
            fr.feats['zipperbagofwords'] = f_zipperwordwindow(tok_id,sentence.forms)# (form,embeddings,"e",dimensions) # [ -a -word +after +later]
            fr.feats['zipperbagoflemmas'] = f_zipperwordwindow(tok_id,sentence.lemmas)#(form,embeddings,"e",dimensions) #
            print fr
        print

if __name__ == "__main__":
    main()