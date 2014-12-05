# -*- coding: utf-8 -*-

from dannet import Dannet
wordnet = Dannet.load('/home/hvk610/tool/dannet/DanNet-2.2_csv')
#print wordnet.synsets("hejre")
for synset in wordnet.synsets("vippe.v"):
    print "lemmas", synset.lemmas()
    print "attrs", synset.attrs()
    print "relations",synset.relations()
    print "hypernyns", synset.hypernyms()
    print "hypernympaths", synset.hypernym_paths()
    print "name",synset.name()
    print "lex_units"
    for unit in synset.lex_units():
        print unit.attrs()
    print "....."
    
print "OBS....and now for nouns"
for synset in wordnet.synsets("vippe.n"):
    print "lemmas", synset.lemmas()
    print "attrs", synset.attrs()
    print "relations",synset.relations()
    print "hypernyns", synset.hypernyms()
    print "hypernympaths", synset.hypernym_paths()
    print "name",synset.name()
    print "lex_units"
    for unit in synset.lex_units():
        print unit.attrs()
    print "....."

#print "related",synset.related()
#for ss in wordnet.all_synsets():
#    print ss.attrs()