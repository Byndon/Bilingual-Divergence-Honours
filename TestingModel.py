# define language objects.
# i don't currently care about the words and stuff
from model import DivergenceModel
from model import Language
from model import Community
import networkx as nx

language1 = Language("Language1")
language2 = Language("Language2")
language3 = Language("Language3")
language4 = Language("Language4")
language5 = Language("Language5")
language6 = Language("Language6")

# make a list of the languages to give to the model.
languageList = [language1, language2, language3, language4, language5, language6]

# input some meanings and forms into the languages
for eachlanguage in languageList:
    eachlanguage.formMeaningDict = {}

language1.add_meaning("Lizard", ([("wiri-wiri", 75, 0), ("mirdi", 10, 0)]))
language2.add_meaning("Lizard", ([("wiri-wiri", 15, 0)]))
language3.add_meaning("Lizard", ([("wiri-wiri", 50, 0), ("mirdi", 10, 0)]))
language4.add_meaning("Lizard", ([("julirri", 80, 0), ("jindararda", 40, 0)]))
language5.add_meaning("Lizard", ([("jindararda", 70, 0), ("wiri-wiri", 50, 0)]))
language6.add_meaning("Lizard", ([("mirdi", 60, 0), ("jindararda", 60, 0)]))

# define the communities which
community1 = Community("Com1", language1, 10)
community2 = Community("Com2", language2, 10)
community3 = Community("Com3", language3, 10)
community4 = Community("Com4", language4, 10)
community5 = Community("Com5", language5, 10)
community6 = Community("Com6", language6, 10)

communityList = [community1, community2, community3, community4, community5, community6]
# create network
socialNet = nx.Graph()
# create nodes from list of community objects
# community objects ARE the nodes in this model
socialNet.add_nodes_from(communityList)
# add weighted connections between the nodes.
socialNet.add_weighted_edges_from([(community1, community6, 0.125), (community6, community5, 0.5), (community1, community5, 0.1), (community2, community5, 0.1), (community6, community4, 0.01), (community2, community4, 0.4)])


# make the model.
testingModel = DivergenceModel(languageList, communityList, socialNet, 0.54, 1)
# step the model once.
testingModel.step()
