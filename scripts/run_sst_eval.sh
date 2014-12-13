

#for factorizations in ident wholetags supersense nopos bioprefix
#do
    for file in `ls $1/*`
    do
    vals=`perl conlleval.pl -d "\t" < $file| grep accuracy`
    outstring="$file $vals"
    echo $outstring
    done
#done

