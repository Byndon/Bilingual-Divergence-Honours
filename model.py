from mesa import Agent, Model
from mesa.time import RandomActivation
import math
import pandas
import csv
import networkx as nx  # used for connecting communtiy agents. Maybe used for connecting agents in large numbers in a more complex simulation.

class language:
    def __init__(self, LanguageName):
        self.LanguageName = LanguageName
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

    def add_speaker(self, SpeakerAgent):
        if(SpeakerAgent.language_repertoire[0] is self):
            self.speakers.append(SpeakerAgent)
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
        self.communityname = name
        self.communitymembers = []
        self.communityLanguage = language
        self.communitySize = size

    def add_members(self, Speaker):
        if(type(Speaker) is SpeakerAgent):
            self.communitymembers.append(Speaker)
        else:
            print("not a speakerAgent")

    def list_members(self):
        print(self.communitymembers)

class SpeakerAgent(Agent):
    def __init__(self, name, model, L1, mode=False, monitoring=False):
        super().__init__(name, model)
        self.name = name
        self.language_repertoire = []
        self.mode = 0
        self.set_language_mode(mode, L1)
        self.monitoring = 0
        self.set_monitoring_level(monitoring)
        self.language_repertoire_add(L1)
        self.L1 = L1
        self.community = None

    def language_repertoire_add(self, language):
        self.language_repertoire.append(language)

    def define_community(self, community):
        if(type(community) is Community):
            self.community = community

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
                    if(langObj in self.language_repertoire):
                        j += 1  # tally increase, another shared language is found.
                i += j / len(langObj)  # calculate the percentage of shared languages between self and currentspeaker.
            mode += i / len(sameLangSpeakers)  # set mode to the average of repertoire.
        else:
            if(0 < mode and mode < 1):
                self.mode = mode

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

        meaning_chosen = self.random.choice(list(self.language_repertoire[self.L1].formMeaningDict.keys()))

        return meaning_chosen

    def Calculate_R_fs_l(self, form, meaning, language):
        # what is the frequency of this form being associated with
        # this meaning in this language?

        # find the index of the form in the list of forms.
        formTally = 0
        for formTuple in language.formMeaningDict[meaning]:
            if formTuple[0] == form:
                formTally = formTuple[1]
                break

        # find the total number of usages of the meaning.
        total_meaning_tally = 0
        for formTuple in language.formMeaningDict[meaning]:
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
        marginal_frequeny = math.fsum([self.Calculate_R_fs_l(form[0], meaning, language) for form in language.formMeaningDict[meaning]])

        return(relative_frequency_f / marginal_frequeny)

    def Calculate_P2M_f_st(self, form, meaning, language, target):
        # Equation 2 in Ellison&Miceli 2017
        k_delta = 0
        if language.LanguageName == target:
            k_delta = 1

        return(k_delta * self.Calculate_R_fs_l(form, meaning, language))

    def Calculate_PBM_f_s(self, form, meaning, language):
        # Equation 3 in Ellison&Miceli 2017
        L = len(self.language_repertoire)

        PBM = 0
        for language in self.language_repertoire:
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
        denominator = math.fsum([self.Calculate_PM_f_sl(form, meaning, language) for language in self.language_repertoire])

        return(1 / denominator)

    def Calculate_PL_l_fstbm(self, form, meaning, language, target, b_mode, monitor):
        # Equation 8 in Ellison&Miceli 2017
        k_L = self.Calculate_k_L(form, meaning)
        Cardinality_L = len(self.language_repertoire)
        PM = self.Calculate_PM_f_sl(form, meaning, language)
        return(monitor * k_L * PM + (1 - monitor) / Cardinality_L)

    def Calculate_QC_f_stbm(self, form, meaning, language, target, b_mode, monitor):
        # Q_C(f|s;t,b,m) = P_L(l=t|f,s;t,b,m) P_G(f|s;t,b)
        Q_C = self.Calculate_PL_l_fstbm(form, meaning, language, target, b_mode, monitor) * self.Calculate_PG_f_stb(form, meaning, target, b_mode, monitor)
        return(Q_C)

    def Calculate_PC_f_stbm(self, form, meaning, language, target, b_mode, monitor):
        # k = \frac{1}{\sum_f Q_c(f|s;t,b,m)}
        k = 1 / math.fsum([self.Calculate_QC_f_stbm(all_form, meaning, language, target, b_mode, monitor) for all_form in [language.formMeaningDict[meaning] for language in self.language_repertoire]])
        # this should be summing the values gained from calculating Q-c_f_stbm over all forms which have the same meaning in each language in the repertoire. 

        # P_C(f|s;t,b,m) = k Q_C(f|s;t,b,m)
        P_C = k * self.Calculate_QC_f_stbm(form, meaning, language, target, b_mode, monitor)
        return(P_C)

    def step(self):
        print("I am Agent {}, I am in community {}, and my L1 is {}".format(self.name, self.community.communityname, self.L1.LanguageName))
        # pick a random meaning from agent's L1.
        # calculate the relative frequency of form f.
        # expressed_meaning = self.select_meaning()

class DivergenceModel(Model):
    def __init__(self, language_object_list, community_object_list, network, seed=12345):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.model_population = sum([community.communitySize for community in community_object_list])
        self.languages = language_object_list
        self.network = network

        current_population = 0
        for community in community_object_list:
            # get the current community's connections and their weights from the list of edges.
            # communities without any connections return an empty list
            # this particular list comprehension returns a list of tuples but strips the tuple of the current community for convenience.
            community_connections = [tuple(elem for elem in sub if elem != community) for sub in list(network.edges.data("weight")) if community in sub]
            # calculate the weight of the native community l1
            weight_of_community_l1 = 1 - math.fsum([i[1] for i in community_connections])
            # include this in the possible choices for assigning a language.
            community_connections.append((community, weight_of_community_l1))
            for population in range(community.communitySize):
                # returns a list of the choices. This list is a single value as only 1 choice is being made.
                communityofl1 = self.random.choices([i[0] for i in community_connections], [j[1] for j in community_connections], k=1)
                # take the 0th item in the list (the language object) and select this as the l1.
                agent_l1 = communityofl1[0].communityLanguage
                speaker = SpeakerAgent(current_population, self, agent_l1)
                community.add_members(speaker)
                speaker.define_community(community)
                self.schedule.add(speaker)
                current_population += 1

    def step(self):
        self.schedule.step()
        print("done")
        # here i must also set the NewTally equal to the Tally, so that the new frequencies can be used in the next time step, unless the frequency being updated with each use is intended.
