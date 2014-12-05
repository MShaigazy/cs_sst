from unittest import TestCase
import unittest
from universal import Wordnet, Wordnet

class TestWordnet(TestCase):
    def setUp(self):
        wn = Wordnet()
        wn.add_synset(1, ['ROOT'], name='ROOT')
        # racehorse, race horse, bangtail ()
        wn.add_synset(2, ['racehorse', 'race horse', 'bangtail'],
                      attrs={'gloss': 'a horse bred for racing'})
        wn.add_synset(3, ['fermentation'],
                      attrs={'gloss': 'a process in which an agent causes an organic substance '
                                      'to break down into simpler substances; '
                                      'especially, the anaerobic breakdown of sugar into alcohol'})
        wn.add_synset(4, ['horse'],
                      attrs={'gloss': 'solid-hoofed herbivorous quadruped domesticated since prehistoric times'})

        wn.add_lex_unit(10, 1, 'The root')
        wn.add_lex_unit(11, 2, 'racehorse', {'POS': 'N'})
        wn.add_lex_unit(12, 2, 'race horse', {'POS': 'N'})
        wn.add_lex_unit(13, 2, 'bangtail', {'POS': 'N'})
        wn.add_lex_unit(14, 4, 'horse', {'POS': 'N'})

        wn.link_lex_units(11, 12, 'the same')

        wn.link_synsets(4, 'has_hyperonym', 1)
        wn.link_synsets(1, 'has_hyponym', 4)
        wn.link_synsets(2, 'has_hyperonym', 4)
        wn.link_synsets(4, 'has_hyponym', 2)
        wn.link_synsets(3, 'has_hyperonym', 1)
        wn.link_synsets(1, 'has_hyponym', 3)

        self.wn = wn

    def test_synset_count(self):
        synset_count = len(list(self.wn.all_synsets()))
        self.assertEqual(4, synset_count)

    def test_get_synset_by_id(self):
        synset = self.wn.synset_by_id(1)
        self.assertIsNotNone(synset)
        self.assertEqual('ROOT', synset.name())

    def test_get_lemmas(self):
        synset = self.wn.synset_by_id(2)
        self.assertEqual(set(synset.lemmas()), set(['racehorse', 'race horse', 'bangtail']))

    def test_related(self):
        root = self.wn.synset_by_id(1)
        self.assertLessEqual([3, 4], [s.id for s in root.related(type='has_hyponym')])

    def test_hypernym_paths(self):
        bangtail = self.wn.synset_by_id(2)
        print self.wn
        print bangtail
        for lex_unit in bangtail.lex_units():
            print lex_unit
        for rel in bangtail.relations():
            print rel

        paths = bangtail.hypernym_paths()
        self.assertEqual(1, len(paths))
        self.assertEqual([2, 4, 1], [s.id for s in paths[0]])

    # def test_get_hypernyms(self):
    #     synset = self.wn.synset_by_id(1)
    #     synset.hypernyms()
    #     # self.assertEqual('ROOT', synset.name())



if __name__ == '__main__':
    unittest.main()