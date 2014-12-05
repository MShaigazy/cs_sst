import codecs
from nltk.stem.snowball import DanishStemmer
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class StoLemmatizer(object):

    def __init__(self):
        self._read_sto_mapping()
        self._read_sto_words()
        self._stemmer = DanishStemmer()


    def _read_sto_mapping(self):
        self.sto_to_uni = {}
        with codecs.open(os.path.join(__location__, "da-sto.map"), encoding='utf-8') as f:
            for line in f:
                sto, uni = line.strip().split("\t")
                self.sto_to_uni[sto] = uni

    def _read_sto_words(self):
        self.lookup_form_and_pos = {}
        self.lookup_form = {}

        with codecs.open(os.path.join(__location__, "STOposUTF8.txt"), encoding='utf-8') as f:
            for line in f:
                form, lemma, pos = line.strip().split("\t")
                self.lookup_form_and_pos[(form.lower(), self.sto_to_uni[pos])] = lemma.lower()
                self.lookup_form_and_pos[(form.lower(), None)] = lemma.lower()

                self.lookup_form[form.lower()] = lemma.lower()

    def lemmatize(self, form, pos=None):
        """
        Look-up word form with optional part-of-speech (universal tagset).

        The method implements a fall-back strategy. When a match with the correct
         part of speech cannot be found, it tries to match the word form with any part of speech.
         If this also fails, the word is stemmed (using the Snowball stemmer) instead of lemmatized.

        :param form:
        :param pos:
        :return:
        """

        form = form.lower()
        if pos in ('NUM', '.', 'X'):
            return form

        return self.lookup_form_and_pos.get((form, pos)) \
               or self.lookup_form_and_pos.get((form, None)) \
               or self._stemmer.stem(form)






