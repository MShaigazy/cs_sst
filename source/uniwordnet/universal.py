from itertools import chain, groupby
from collections import defaultdict
import networkx as nx


class Relation(object):
    def __init__(self, wn, src_synset, target_synset_id, type, attrs={}):
        self.wn = wn
        self._src_synset = src_synset
        self._target_synset_id = target_synset_id
        self._type = type
        self._attrs = attrs

    def src_synset(self):
        return self._src_synset

    def target_synset(self):
        return self.wn.Synset(self.wn, self._target_synset_id)

    def type(self):
        return self._type

    def __repr__(self):
        return u"{}({}, {}, {})".format(self.__class__.__name__,
                                        self._src_synset.id,
                                        self._type,
                                        self._target_synset_id)


class Synset(object):

    def __init__(self, wn, id):
        self.wn = wn
        self.id = id

    def lex_units(self):
        return [self.wn.LexUnit(self.wn, target, self.id)
                for _, target, data in self.wn.G.out_edges(self.id, data=True)
                if data['type'] == u'synset_to_lex_unit']

    def related(self, type=None):
        return [r.target_synset() for r in self.relations(type)]

    def relations(self, type=None):
        return [r for r in self._unfiltered_relations()
                if type is None or type == r.type()]

    def _unfiltered_relations(self):
        return [Relation(self.wn, self, target_synset_id, data['type'], data)
                for _, target_synset_id, data in self.wn.G.out_edges(self.id, data=True)
                if data['type'] != u'synset_to_lex_unit']

    def attrs(self):
        return self.wn.G.node[self.id]

    def __getitem__(self, item):
        return self.wn.G.node[self.id][item]

    def __setitem__(self, key, value):
        self.wn.G.node[self.id][key] = value

    def name(self):
        return self.attrs()['name']

    def lemmas(self):
        return [lu.lemma() for lu in self.lex_units()]

    def hypernyms(self):
        if self.wn.hypernym_name is None:
            raise Exception("Hypernyms are not supported for this wordnet")
        return self.related(self.wn.hypernym_name)

    def hyponyms(self):
        if self.wn.hyponym_name is None:
            raise Exception("Hyponyms are not supported for this wordnet")
        return self.related(self.wn.hyponym_name)

    def hypernym_paths(self):
        return [[self] + path
                for h in self.hypernyms()
                for path in h.hypernym_paths()] \
            or [[self]]

    def __repr__(self):
        return u"{}({}, '{}')".format(self.__class__.__name__, self.id, self.name())


class LexUnit(object):

    def __init__(self, wn, id, synset_id):
        self.wn = wn
        self.id = id
        self.synset_id = synset_id

    def attrs(self):
        return self.wn.G.node[self.id]

    def lemma(self):
        return self.attrs()['lemma']

    def __repr__(self):
        return u"{}({}, '{}' in synset {})".format(self.__class__.__name__,
                                            self.id, self.lemma(), self.synset_id)


class Wordnet(object):
    Synset = Synset
    LexUnit = LexUnit
    """A wordnet graph structure that allows lookup of synsets by lemma and synset id

    The graph is directly accessible as an attribute and need not be manipulated through this class
    as long it adheres to the structure and naming convention described below.

    Lexical units (words associated with synsets) are autonomous nodes in the structure since
    it's possible to have direct links between lexical units. The link between a synset and a lexical unit
     is directed and goes from the synset to the lexical unit.

    Synsets and lexical units are associated with unique IDs, both of which live in the same namespace.
    Additionally, synsets can also be retrieved by one or more lookup keys.
    """

    def __init__(self):
        self.G = nx.MultiDiGraph()
        self._synset_map = defaultdict(lambda: set())
        self._synsets = set()
        self._lex_units = set()
        self.hypernym_name = 'has_hyperonym'
        self.hyponyn_name = 'has_hyponym'

    def add_synset(self, id, lookup_keys=[], name=None, attrs={}):
        for k in lookup_keys:
            self.add_synset_lookup(id, k)
        if name is None:
            name = unicode(id)
        attrs.update({'name': name})
        self.G.add_node(id, attrs)
        self._synsets.add(id)

    def add_synset_lookup(self, synset_id, lookup_key):
        self._synset_map[lookup_key].add(synset_id)

    def add_lex_unit(self, id, synset_id, lemma, attrs={}):
        attrs.update({'lemma': lemma})
        self.G.add_node(id, attrs)
        self.G.add_edge(synset_id, id, type=u'synset_to_lex_unit')
        self.G.add_edge(id, synset_id, type=u'lex_unit_to_synset')
        self._lex_units.add(id)

    def link_synsets(self, src_id, link_type, target_id, attrs={}):
        self.G.add_edge(src_id, target_id, type=link_type, attr_dict=attrs)

    def link_lex_units(self, src_id, link_type, target_id, attrs={}):
        self.G.add_edge(src_id, target_id, type=link_type, attr_dict=attrs)

    def synsets(self, lookup):
        if lookup in self._synset_map:
            return [self.synset_by_id(synset_id)
                    for synset_id in self._synset_map[lookup]]
        else:
            return []

    def synset_by_id(self, id):
        if id not in self._synsets or id not in self.G:
            raise Exception(u"id={} is not a synset in the wordnet".format(id))
        return self.Synset(self, id)

    def all_synsets(self):
        for id in self._synsets:
            yield self.Synset(self, id)

    def relation_counts(self):
        edges = chain.from_iterable(self.G[src_n][target_n].values() for src_n, target_n in nx.edges_iter(self.G))
        types = [e['type'] for e in edges]
        grouped = groupby(sorted(types))
        return dict((name, len(list(vals))) for name, vals in grouped)

    def __repr__(self):
        return u"{}({} synsets, {} lexical units)".format(self.__class__.__name__,
                                                          len(self._synsets), len(self._lex_units))
