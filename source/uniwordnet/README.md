This software implements a Python interface, which allows wordnets from various sources,
and possibly guided by different philosophies and linguistic theories, to be accessed in a uniform way.

A few assumptions are made about the structure of the wordnet. It must have synsets,
collections of synonymous "words" that together form a concept, linked together by means of typed relations.
Associated with each synset should be a number of lexical units, typically the synonymous words mentioned above,
although there's no requirement that they're single words.

The wordnet is represented as a graph structure. Both synsets and lexical units are modelled as nodes in the graph,
and edges link synsets to synsets, synsets to lexical units, and lexical units to other lexical units.
Arbitrary information can be attached to a dictionary of properties on both nodes and edges.

The graph structure, a [MultiDiGraph] from the [networkx] can be accessed directly, and is
for many purposes the best way to access the wordnets.
The package also features a convenient object-oriented interface for quering the wordnet.

A typical session using the query interface might look like this:

    from dannet import Dannet


    In [5]: wordnet = dannet.Dannet.load('/users/anders/data/dannet/DanNet-2.1_csv')
    In [6]: wordnet.synsets("hejre")
    Out[6]:
    [Synset(11308, '{hejre,1_1}'),
     Synset(4320, '{harpe_2; havgasse_1; hejre,1_2}'),
     Synset(35454, '{hejre,2_1}')]
    In [7]: synset = wordnet.synsets("hejre")[1]
    In [7]: synset.lemmas()
    Out[7]: [u'harpe', u'hejre', u'havgasse']


At the moment the interface loads

- [Dannet] 2.1, the Danish wordnet, which also has a [graphical interface]
- Germanet 5.7, a German wordnet
- UKB, a format used by the graph-based [word sense disambiguation software] of Eneko Agirre
- [Princeton Wordnet] 3.0

(Note that only Dannet is checked into the repository,
because the other interfaces need a small refactoring to work)

[word sense disambiguation software]: http://ixa2.si.ehu.es/ukb/
[Dannet]: http://wordnet.dk/
[graphical interface]: http://andreord.dk
[Princeton Wordnet]: http://wordnet.princeton.edu/
[networkx]: http://networkx.github.com/
[MultiDiGraph]: http://networkx.github.com/documentation/latest/reference/classes.multidigraph.html
