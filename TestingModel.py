# define language objects.
# i don't currently care about the words and stuff
from model import DivergenceModel
from model import language
from model import Community
import networkx as nx

Language1 = language("Language1")
Language2 = language("Language2")
Language3 = language("Language3")
Language4 = language("Language4")
Language5 = language("Language5")
Language6 = language("Language6")

# make a list of the languages to give to the model.
languageList = [Language1, Language2, Language3, Language4, Language5, Language6]

# input some meanings and forms into the languages
meaning_I = ("I", [("A", 10, 0), ("Ay", 10, 0), ("Ei", 30, 0)])
meaning_you = ("You", [("Yuh", 14, 0), ("Ye", 76, 0), ("thou", 32, 0)])
meaning_we = ("We", [("Wey", 34, 0), ("Wi", 76, 0), ("Wir", 30, 0)])
for eachlanguage in languageList:
    eachlanguage.add_meaning(meaning_I[0], meaning_I[1])
    eachlanguage.add_meaning(meaning_you[0], meaning_you[1])
    eachlanguage.add_meaning(meaning_we[0], meaning_we[1])

# define the communities which
community1 = Community("Com1", Language1)
community2 = Community("Com2", Language2)
community3 = Community("Com3", Language3, 300)
community4 = Community("Com4", Language4, 141)
community5 = Community("Com5", Language5)
community6 = Community("Com6", Language6)

communityList = [community1, community2, community3, community4, community5, community6]
# create network
socialNet = nx.Graph()
# create nodes from list of community objects
# community objects ARE the nodes in this model
socialNet.add_nodes_from(communityList)
# add weighted connections between the nodes.
socialNet.add_weighted_edges_from([(community1, community6, 0.125), (community6, community5, 0.5), (community1, community5, 0.1), (community2, community5, 0.1), (community6, community4, 0.01), (community2, community4, 0.4)])


# make the model. 
testingmodel = DivergenceModel(languageList, communityList, socialNet)
# step the model once.
testingmodel.step()
