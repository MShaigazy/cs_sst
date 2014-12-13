import argparse
from collections import Counter, defaultdict
parser = argparse.ArgumentParser(description="Create standard features for Twitter SST")
parser.add_argument('input', help="TSV data in <form,PetrovPOS,SST> format, colons ';' replaced with '<COLON>' ")
parser.add_argument('traincorpus', help="TSV data in <form,PetrovPOS,SST> format, colons ';' replaced with '<COLON>' ")
parser.add_argument('lang', help="Map for string class to integer")
args = parser.parse_args()

shortpos={}
shortpos["NOUN"]="NOUN"
shortpos["VERB"]="NOUN"
shortpos["ADJ"]="ADJ"
shortpos["NN"]="NOUN"
shortpos["NNS"]="NOUN"
shortpos["NNP"]="NOUN"
shortpos["NNPS"]="NOUN"
shortpos["VB"]="VERB"
shortpos["VBD"]="VERB"
shortpos["VBG"]="VERB"
shortpos["VBN"]="VERB"
shortpos["VBP"]="VERB"
shortpos["VBZ"]="VERB"




MFS={}
MFS[("da","NOUN")]="B-noun.person"
MFS[("da","VERB")]="B-verb.stative"
MFS[("da","ADJ")]="B-adj.all"

MFS[("en","NOUN")]="B-noun.artifact"
MFS[("en","VERB")]="B-verb.communication"



MFSCounter = defaultdict(Counter)

for idx, line in enumerate(open(args.traincorpus).readlines()):
    if len(line) > 2:
        word, pos, sense = line.strip().split("\t")
        lexpos = shortpos.get(pos,"O")
        if lexpos != "O":
            MFSCounter[(word.lower(),lexpos)][sense]+=1


for idx, line in enumerate(open(args.input).readlines()):
    if len(line) > 2:
        word, pos, sense = line.strip().split("\t")
        lexpos = shortpos.get(pos,pos)
        mfs = MFS.get((args.lang,lexpos),"O")
        if pos.startswith("V") and sense == "O":
            mfs = "O"
        else:
            if (word.lower(),lexpos) in MFSCounter:
                mfs = MFSCounter[(word.lower(),lexpos)].most_common()[0][0]
        print "\t".join([str(idx),word,pos,sense,mfs])
    else:
        print