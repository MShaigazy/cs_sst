#for cm in wholetags nopos bioprefix supersense
#do
#python ../source/confusion_matrices_sst.py -t $cm --file1 ../data/dup/sara.politiken5-6.tsv --file2 ../data/dup/idathomas.politiken5-6.tsv  > ../data/cm/politiken5-6.$cm.tsv
#done
#
#for cm in wholetags nopos bioprefix supersense
#do
#python ../source/confusion_matrices_sst.py -t $cm --file1  ../data/dup/ritterpos.test.SST.prepared.joint_part.annotations.CORRECTED.all-annotators.txt > ../data/cm/ritter.test.triple.$cm.tsv
#done


for cm in wholetags nopos bioprefix supersense
do
python ../source/confusion_matrices_sst.py -t $cm --file1 ../data/dup/sara.politiken5-6.tsv --file2 ../data/dup/idathomas.politiken5-6.tsv  --format matrix > ../data/cm/politiken.cm.$cm.tsv
done

for cm in wholetags nopos bioprefix supersense
do
python ../source/confusion_matrices_sst.py -t $cm --file1  ../data/dup/ritterpos.test.SST.prepared.joint_part.annotations.CORRECTED.all-annotators.txt --format matrix > ../data/cm/ritter.test.cm.$cm.tsv
done

for cm in wholetags nopos bioprefix supersense
do
python ../source/confusion_matrices_sst.py -t $cm --file1 ../data/dup/sarapol56.commontags.tsv --file2 ../data/dup/idathomaspol56.commontags.tsv --format matrix > ../data/cm/politiken.englishsenses.cm.$cm.tsv
done