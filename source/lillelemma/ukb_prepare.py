import argparse
import codecs
import re

from sto_lemmatizer import StoLemmatizer


parser = argparse.ArgumentParser(description="""Reads VW input and writes out lemmatized sentences""")
parser.add_argument('input_file', help="VW-formatted sentences")
args = parser.parse_args()

lemmatizer = StoLemmatizer()


word_pat = re.compile("w_0=(\S+)")
pos_pat = re.compile("p_0=(\S+)")

with codecs.open(args.input_file, encoding='utf-8') as f:
    sentence = []
    for line in f:
        if line.startswith("#"):
            continue

        if len(line.strip()) == 0:
            print sentence
            sentence = []
            continue

        m_word = word_pat.search(line)
        m_pos = pos_pat.search(line)

        if not (m_word and m_pos):
            raise StandardError("Word and POS not found in line: '{}'".format(line))

        word = m_word.groups()[0]
        pos = m_pos.groups(0)[0]
        lemma = lemmatizer.lemmatize(word, pos)

        sentence.append((word, lemma, pos))

    if sentence:
        print sentence