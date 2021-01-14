from mesa import Agent, Model
from mesa.time import RandomActivation
import math
import pandas
import csv
import random
import networkx as nx  # used for connecting communtiy agents. Maybe used for connecting agents in large numbers in a more complex simulation.

class Language:
    def __init__(self, languageName):
        self.languageName = languageName
        self.formMeaningDict = {}
        self.speakers = []

    def add_from_file(self, filename):
        # this method will be able to take a file, formatted as CSV
        # and turn it into a dictionary with Meaning Keys, and
        # a list of tuples with Form and Relative frequency
        # relative frequency should be a parameter
        # if we have enough information, BUT
        # can also be randomly determined.
        pass

    def add_meaning(self, meaning, formTupleList):
        if(type(formTupleList) is list and all([True for t in formTupleList if type(t) is tuple])):
            # check if the formTupleList given is a list, and that the list contains tuples. 
            self.formMeaningDict[meaning] = formTupleList
            return(True)
        else:
            print("need a list of tuples for the forms of meanings.")
            return(False)

    def add_speaker(self, speakerAgent):
        if(speakerAgent.language_repertoire[0] is self):
            self.speakers.append(speakerAgent)
            return(True)
        else:
            return(False)

    def borrow_form(self):
        # this function is for the chance for a language to gain a borrowing.
        # Borrowings should be marked accordingly with an addition to the
        # string indicating where they were brrowed from.
        pass

    def lose_form(self):
        # this function is for the chance that a form becomes so obscure that
        # it is no longer used in the language.
        # This can also occur randomly to kick-start the bias process.
        # need to figure out the randomness before implementing.
        pass

class Community:
    def __init__(self, name, language, size=150):
        self.communityName = name
        self.communityMembers = []
        self.communityLanguage = language
        self.communitySize = size

    def add_members(self, Speaker):
        if(type(Speaker) is Speaker_Agent):
            self.communityMembers.append(Speaker)
        else:
            print("not a speakerAgent")

    def list_members(self):
        print(self.communityMembers)

class Speaker_Agent(Agent):
    def __init__(self, name, model, L1, mode=False, monitoring=False):
        super().__init__(name, model)
        self.name = name
        self.languageRepertoire = []
        self.mode = 0
        self.set_language_mode(mode, L1)
        self.monitoring = 0
        self.set_monitoring_level(monitoring)
        self.language_repertoire_add(L1)
        self.L1 = L1
        self.Community = None

    def language_repertoire_add(self, language):
        self.languageRepertoire.append(language)

    def define_community(self, community):
        if(type(community) is Community):
            self.Community = community

            # For setting this up, after agents are assigned to a community,
            # loop through them and set their community.

    def set_language_mode(self, mode, L1):
        if mode is False:
            self.mode = self.random.uniform(0, 1)
        elif mode is True:
            # This need to be checked for issues, I'm not thinking right now.
            mode = 0
            i = 0  # keeps track of the current average for self to the current speaker from L1.speakers
            for sameLangSpeakers in L1.speakers:
                j = 0  # keeps track of the numbers of shared languages between self and speaker.
                for langObj in sameLangSpeakers.language_repertoire:
                    if(langObj in self.languageRepertoire):
                        j += 1  # tally increase, another shared language is found.
                i += j / len(langObj)  # calculate the percentage of shared languages between self and currentspeaker.
            mode += i / len(sameLangSpeakers)  # set mode to the average of repertoire.
        elif(0 < mode and mode < 1):
            self.mode = mode
        else:
            print("something went wrong, monitoring is a value between 0 and 1.")

    def set_monitoring_level(self, monitoring):
        if monitoring is False:
            self.monitoring = self.random.uniform(0, 1)
        if monitoring is True:
            # determine monitoring based on others in the community
            pass
        else:
            if(0 < monitoring and monitoring < 1):
                self.monitoring = monitoring

    def select_meaning(self):
        # randint is inclusive of the begin and end numbers.
        # select which meaning key is used from all possible meanings in one of the agent's languages.
        # meanaings are the keys for the dictionary
        # I use L1 just out of convenience, all languages can express the same meanings.

        meaning_chosen = self.random.choice(list(self.languageRepertoire[0].formMeaningDict.keys()))

        return(meaning_chosen)
    # below this comment, is the calculations for the bilingual mode and monitoring model. E&M 2017.
    def Calculate_R_fs_l(self, form, meaning, language):
        # what is the frequency of this form being associated with
        # this meaning in this language?

        # find the index of the form in the list of forms.
        formTally = 0
        for formTuple in language.formMeaningDict[meaning]:
            if formTuple == form:
                formTally = formTuple[1]
                break

        # find the total number of usages of the meaning.
        total_meaning_tally = 0
        for languages in self.languageRepertoire:
            for formTuple in languages.formMeaningDict[meaning]:
                total_meaning_tally += formTuple[1]

        # return the percentage of the form to the total usage of the meaning
        # i.e. how frequent this form is when expressing this meaning.
        return(formTally / total_meaning_tally)

    def Calculate_PM_f_sl(self, form, meaning, language):
        # Equation 1 in Ellison&Miceli 2017
        # calculate the relative ferquency of the form in language for meaning
        relative_frequency_f = self.Calculate_R_fs_l(form, meaning, language)

        # what I THINK This is doing:
        # creating a list of the results from Cacluate_R_fs_l
        # and summing the contents of the list with math.fsum()
        # i KNOW this will be inefficient, as it is calculating the total_meaning_tally each time.

        # old code, the debugger apparently doesn't play nicely with namespaces in list comprehensions.
        # marginal_frequency = math.fsum([self.Calculate_R_fs_l(form[0], meaning, language) for form in language.formMeaningDict[meaning]])

        marginal_frequency_list = []
        for form in language.formMeaningDict[meaning]:
            marginal_frequency_list.append(self.Calculate_R_fs_l(form, meaning, language))

        marginal_frequency = math.fsum(marginal_frequency_list)

        return(relative_frequency_f / marginal_frequency)

    def Calculate_P2M_f_st(self, form, meaning, language, target):
        # Equation 2 in Ellison&Miceli 2017
        k_delta = 0
        if language.languageName is target:
            k_delta = 1

        return(k_delta * self.Calculate_R_fs_l(form, meaning, language))

    def Calculate_PBM_f_s(self, form, meaning, language):
        # Equation 3 in Ellison&Miceli 2017
        L = len(self.languageRepertoire)

        PBM = 0
        for language in self.languageRepertoire:
            PM = self.Calculate_PM_f_sl(form, meaning, language)
            PBM += 1 / L * PM

        return(PBM)

    def Calculate_PG_f_stb(self, form, meaning, target, b_mode, language):
        # Equation 4 in Ellison&Miceli 2017
        P2M = self.Calculate_P2M_f_st(form, meaning, language, target)
        PBM = self.Calculate_PBM_f_s(form, meaning, language)

        return((1 - b_mode) * P2M + b_mode * PBM)

    def Calculate_k_L(self, form, meaning):
        # k_L = \frac{1}{\sum_{l \in L} P_M(f|s;l)}
        # turn this into a list comprehension and sum it's values with fsum.
        # for language in self.language_repertoire:
        #     self.Calculate_PM_f_sl(form, meaning, language)
        denominator = math.fsum([self.Calculate_PM_f_sl(form, meaning, language) for language in self.languageRepertoire])

        return(1 / denominator)

    def Calculate_PL_l_fstbm(self, form, meaning, language, target, b_mode, monitor):
        # Equation 8 in Ellison&Miceli 2017
        k_L = self.Calculate_k_L(form, meaning)
        Cardinality_L = len(self.languageRepertoire)
        PM = self.Calculate_PM_f_sl(form, meaning, language)
        return(monitor * k_L * PM + (1 - monitor) / Cardinality_L)

    def Calculate_QC_f_stbm(self, form, meaning, language, target, b_mode, monitor):
        # Q_C(f|s;t,b,m) = P_L(l=t|f,s;t,b,m) P_G(f|s;t,b)
        Q_C = self.Calculate_PL_l_fstbm(form, meaning, language, target, b_mode, monitor) * self.Calculate_PG_f_stb(form, meaning, target, b_mode, language)
        return(Q_C)

    def Calculate_PC_f_stbm(self, form, meaning, language, target, b_mode, monitor):
        # k = \frac{1}{\sum_f Q_c(f|s;t,b,m)}

        # old code, a  bit spaghetti
        # k = 1 / math.fsum([self.Calculate_QC_f_stbm(all_form, meaning, language, target, b_mode, monitor) for all_form in [language.formMeaningDict[meaning] for language in self.language_repertoire]])
        QC_f_stbm_list = []
        for language in self.languageRepertoire:
            for all_forms in language.formMeaningDict[meaning]:
                QC_f_stbm_list.append(self.Calculate_QC_f_stbm(all_forms, meaning, language, target, b_mode, monitor))

        k = 1 / math.fsum(QC_f_stbm_list)
        # this should be summing the values gained from calculating Q-c_f_stbm over all forms which have the same meaning in each language in the repertoire. 

        # P_C(f|s;t,b,m) = k Q_C(f|s;t,b,m)
        P_C = k * self.Calculate_QC_f_stbm(form, meaning, language, target, b_mode, monitor)
        return(P_C)

    def step(self):
        print("I am Agent {}, I am in community {}, and I speak {}".format(self.name, self.Community.communityName, str([language.languageName for language in self.languageRepertoire])))
        meaning = self.select_meaning()
        print(meaning)
        likelyhoods = []
        for language in self.languageRepertoire:
            for form in language.formMeaningDict[meaning]:
                # the code in the next line just prints the results
                # print((form, self.Calculate_PC_f_stbm(form, meaning, language, self.community.communityLanguage, self.mode, self.monitoring)))
                likelyhoods.append((form, self.Calculate_PC_f_stbm(form, meaning, language, self.Community.communityLanguage, self.mode, self.monitoring)))
        print(likelyhoods)
        print((self.mode, self.monitoring))

        # pick a random meaning from agent's L1.
        # calculate the relative frequency of form f.
        # expressed_meaning = self.select_meaning()

class DivergenceModel(Model):
    def __init__(self, languageObjectList, communityObjectList, network, mode=False, monitoring=False, seed=12345):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.model_population = sum([community.communitySize for community in communityObjectList])
        self.languages = languageObjectList
        self.network = network

        currentPopulation = 0
        for community in communityObjectList:
            # get the current community's connections and their weights from the list of edges.
            # communities without any connections return an empty list
            # this particular list comprehension returns a list of tuples but strips the tuple of the current community for convenience.
            communityConnections = [tuple(elem for elem in sub if elem != community) for sub in list(network.edges.data("weight")) if community in sub]
            # calculate the weight of the native community l1
            weightOfCommunityL1 = 1 - math.fsum([i[1] for i in communityConnections])
            # include this in the possible choices for assigning a language.
            communityConnections.append((community, weightOfCommunityL1))
            for population in range(community.communitySize):
                # returns a list of the choices. This list is a single value as only 1 choice is being made.
                communityOfL1 = self.random.choices([i[0] for i in communityConnections], [j[1] for j in communityConnections], k=1)
                # take the 0th item in the list (the language object) and select this as the l1.
                agentL1 = communityOfL1[0].communityLanguage
                speaker = Speaker_Agent(currentPopulation, self, agentL1, mode, monitoring)
                community.add_members(speaker)
                speaker.define_community(community)
                # make the agent speak the community language, if it is not their l1
                if(speaker.L1 is not community.communityLanguage):
                    speaker.language_repertoire_add(community.communityLanguage)
                # determine how many languages the agent can speak
                numberOfLanguagesSpoken = self.random.choices([i + 1 for i in range(len(languageObjectList))], [0.6, 0.5, 0.4, 0.3, 0.2, 0.1], k=1)
                if(len(communityConnections) > 1 and numberOfLanguagesSpoken[0] > len(speaker.languageRepertoire)):
                    currentNumberOfLanguages = len(speaker.languageRepertoire)
                    for i in sorted(communityConnections, key=lambda x: x[1]):
                        if(i[0].communityLanguage not in speaker.languageRepertoire and currentNumberOfLanguages <= numberOfLanguagesSpoken[0]):
                            speaker.language_repertoire_add(i[0].communityLanguage)
                            currentNumberOfLanguages += 1
                self.schedule.add(speaker)
                currentPopulation += 1

    def step(self):
        self.schedule.step()
        print("done")
        # here i must also set the NewTally equal to the Tally, so that the new frequencies can be used in the next time step, unless the frequency being updated with each use is intended.

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
