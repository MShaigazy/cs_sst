import argparse
import sys
from collections import Counter





def wholetags(tag):
    return tag

def nopos(tag):
    return tag.split(".")[-1]

def bioprefix(tag):
    return tag[0]

def supersense(tag):
    if len(tag) < 2:
        return tag
    else:
        return tag[2:]

def getColumn(file, column):
    acc = []
    for line in open(file):
        if len(line) < 2:
            pass
        else:
            acc.append(line.strip().split("\t")[column])
    return acc

def applymaxdist(array,maxdist):
    acc = []
    for v in array:
        if v > -1*maxdist and v < maxdist:
            acc.append(v)
        elif v <= -1*maxdist:
            acc.append(-1*maxdist)
        #elif v >= args.maxdist:
        else:
            acc.append(maxdist)
    return acc


def rowtotals(M,L):
    R = Counter()
    for label in L:
        for (row, col) in M.iterkeys():
            if row == label:
                R[label]+=1.0*M[(row,col)]
    return R

def coltotals(M,L):
    C = Counter()
    for label in L:
        for row, col in M.iterkeys():
            if col == label:
                C[label]+=1.0*M[row,col]
    return C


def main():
    parser = argparse.ArgumentParser(description="Generates confusion matrices for supersense-annotated data")
    parser.add_argument("file1",   metavar="FILE", help="name of the tagged file")
    parser.add_argument("file2", metavar="FILE", help="name of the tagged file")
    parser.add_argument("-lc","--labelcolumnindex", help="column index of the label, default -1", required=False, type=int, default=-1) #column index as array indices, starting from 0
    parser.add_argument("-t","--typeofmatrix", help="""wholetags (e.g.  B-noun.person vs I-verb.cognition)
                                                     supersense (e.g. )
                                                     nopos (e.g. cognition vs. communication, ignoring noun.x or verb.x)
                                                     bioprefix (headpos+directionality)
                                                     """, required=False, default="wholetags")  # headdistance, regular, headpos



    args = parser.parse_args()



    M = Counter()
    L = set()
    T = 0
    labels1 = []
    labels2 = []

    #if args.typeofmatrix == "wholetags":
    labels_orig1 = getColumn(args.file1, args.labelcolumnindex)
    labels_orig2 = getColumn(args.file2, args.labelcolumnindex)
    labels1 = [globals()[args.typeofmatrix](label) for label in labels_orig1]
    labels2 = [globals()[args.typeofmatrix](label) for label in labels_orig2]
    for l1, l2 in zip(labels1,labels2):
        L.add(l1)
        L.add(l2)
        M[(l1,l2)]+=0.5
        M[(l2,l1)]+=0.5


    print "#"+" ".join(sys.argv)
    print "#Note support is for the internal representation (e.g. noun.person instead of B-noun.person), not for the printed key. There will be repetitions for anything for wholetags"
    print "#row, col, support, norm_over_row_i_and_col_j"
    T = sum(M.values())
    rowtots = rowtotals(M,L)
    coltots= coltotals(M,L)
    #print rowtots
    #print coltots
    for l1 in sorted(set(labels_orig1)):
        for l2 in sorted(set(labels_orig2)):
            lcm1 = globals()[args.typeofmatrix](l1)
            lcm2 = globals()[args.typeofmatrix](l2)
            if M[lcm1,lcm2] == 0.0:
                outline = [l1, l2, 0.0, 0.0 ]
            else:
                outline = [l1, l2, M[lcm1,l2], M[(lcm1,lcm2)]/(rowtots[lcm1] + coltots[lcm2])]
            print "\t".join([str(x) for x in outline])


main()

