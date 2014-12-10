matrix=baseline
for file in lowlands.sst ritterpos.test.SST.annotations.adjudicated.txt.dev ritterpos.test.SST.annotations.adjudicated.txt.eval ritterpos.test.SST.annotations.adjudicated.txt.TRAIN SEM.BIO.conll.fold1 SEM.BIO.conll.fold2 SEM.BIO.conll.fold3 SEM.BIO.conll.fold4 SEM.BIO.conll.fold5
do
        outfile=$file.vw.feats
        python ../source/generate_features.py ~/data/full/$file --weightmode regular --normalization-dict ../data/res/emnlp_dict.txt --embeddings ~/proj/cs_sst/data/res/cs_sst_en.reduced.embed  --lang en > $outfile
done
