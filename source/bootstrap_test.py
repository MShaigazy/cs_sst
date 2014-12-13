from __future__ import division
import sys,re
import numpy as np
from scipy import stats
from sklearn import metrics
import random



def getColumn(column, file):
    acc = []
    for line in open(file):
        if len(line) < 2:
            pass
        else:
            try:
                acc.append(line.strip().split("\t")[column])

            except:
                print line
    return acc

sys1=getColumn(-1,sys.argv[1])
sys2=getColumn(-1,sys.argv[2])#
gold=getColumn(-2,sys.argv[2])#
Iter = int(sys.argv[3])


def pvalue_bootstrap_ner_f1(s1,s2, gold):
    f1_macro= metrics.f1_score(s1, gold, average="macro") - metrics.f1_score(s2, gold, average="macro")
    f1_micro= metrics.f1_score(s1, gold, average="micro") - metrics.f1_score(s2, gold, average="micro")
    accuracy= metrics.accuracy_score(s1, gold) - metrics.accuracy_score(s2, gold)
    false_1_macro=0
    false_1_micro=0
    false_accuracy=0
    for _ in range(Iter):
        resample_i=np.random.randint(0,len(s1),len(s1))
        s1_r=s1[resample_i]
        s2_r=s2[resample_i]
        gold_r=gold[resample_i]
        new_f1_macro= metrics.f1_score(s1_r, gold_r, average="macro") - metrics.f1_score(s2_r, gold_r, average="macro")
        new_f1_micro= metrics.f1_score(s1_r, gold_r, average="micro") - metrics.f1_score(s2_r, gold_r, average="micro")
        new_accuracy= metrics.accuracy_score(s1_r, gold_r) - metrics.accuracy_score(s2_r, gold_r)
        #print f1_macro, f1_micro, accuracy, new_f1_macro, f1_micro, new_accuracy
        if new_f1_macro*f1_macro<0:
            false_1_macro+=1.0
        if new_f1_micro*f1_micro<0:
            false_1_micro+=1.0
        if new_accuracy*accuracy<0:
            false_accuracy+=1.0
    r = []

    r.append(metrics.f1_score(s1, gold, average="macro"))
    r.append(metrics.f1_score(s2, gold, average="macro"))
    r.append(false_1_macro/float(Iter))
    r.append(metrics.f1_score(s1, gold, average="micro"))
    r.append(metrics.f1_score(s2, gold, average="micro"))
    r.append(false_1_micro/float(Iter))
    
    r.append(metrics.accuracy_score(s1, gold))
    r.append(metrics.accuracy_score(s2, gold))
    r.append(false_accuracy/float(Iter))
    return [str(a) for a in r]


header = ["repetitions", "macroF1-s1", "macroF1-s2", "macroF1-p", "microF1-s1", "microF1-s2", "microF1-p", "acc-s1", "acc-s2", "acc-p"]
print "\t".join(header)
shuffled_indices =  np.random.randint(0,len(sys1),len(sys1))
current_indices = shuffled_indices[:int(len(shuffled_indices))]
sys1_current = [sys1[i] for i in range(len(current_indices))] 
sys2_current = [sys2[i] for i in range(len(current_indices))] 
gold_current = [gold[i] for i in range(len(current_indices))] 
#print rep, k, len(current_indices) 
print str(Iter)+"\t"+"\t".join(pvalue_bootstrap_ner_f1(np.array(sys1_current), np.array(sys2_current), np.array(gold_current)))