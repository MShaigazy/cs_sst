for cm in wholetags nopos bioprefix supersense
do
python ../source/confusion_matrices_sst.py -t $cm ../data/dup/sara.politiken5-6.tsv ../data/dup/idathomas.politiken5-6.tsv  > ../data/cm/politiken5-6.$cm.tsv
done