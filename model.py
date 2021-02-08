from mesa import Agent, Model
from mesa.time import RandomActivation
import math
import pandas
import csv
import networkx as nx  # used for connecting communtiy agents. Maybe used for connecting agents in large numbers in a more complex simulation.

class Language:
    '''
    A language in this model consists of a dictionary of meanings with associated forms as key values.
    associated with the form keys are a count of the number of times it has been used
    also associated is a count of the times it has been used in the current model step,
    so that this can be included added at the end of the step.
    '''

    # a language has a name, a form-meaning dictionary, and a list of speakers.
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
        if(type(formTupleList) is list and all(
                [True for t in formTupleList if type(t) is tuple])):
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
    '''
    A community is a grouping of speakers.
    It consists of a name, a list of its members,
    a 'native' community language which is spoken by the speakers,
    and a defined number of speakers.
    '''
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
    '''
    A speaker in this model is the agent.
    speakers belong to a community and have a repertoire of languages
    which they have the possibility of speaking,
    based on the connections between their community
    and others.
    '''
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
        if(type(language) is Language):
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
            if(0 <= monitoring and monitoring <= 1):
                self.monitoring = monitoring

    def select_meaning(self):
        # select randomly which meaning key is used,
        # from all possible meanings in one of the agent's languages.
        # meanings are the keys for the dictionary
        # I use L1 (the first language in the repertoire list)
        # out of convenience, all languages can express the same meanings.

        # make a random choice from a list of the dictionary keys.
        meaningChosen = self.random.choice(list(self.languageRepertoire[0].formMeaningDict.keys()))

        return(meaningChosen)

    # below this comment, is the calculations for the bilingual mode and monitoring model. E&M 2017.
    def Calculate_N_fs_l(self, form, meaning, language):
        # N(f,s|l) = |\{i \in 1..n_l|S_{l,i} = (f,s)\}|
        numberOfPairings = 0
        for formTuple in language.formMeaningDict[meaning]:
            if formTuple == form:
                numberOfPairings = formTuple[1]
                break

        return(numberOfPairings)

    def Calculate_R_fs_l(self, form, meaning, language):
        '''
        Using f for form, s for meaning, and l to denote the language, we express the relative
        frequency (R) with which a language learner hears a form-meaning combination, in the
        context of language l, as R( f, s|l). In this minimal model, the probability (in monolin-
        gual mode: P M ) of using form f on a future occasion to express meaning s in language l
        is the ratio of the relative frequency of the combination to the marginal frequency of
        using that meaning in that language (1).
        Overall frequency of f,s pairing in l, so it has to account for all meanings and words
        in that language.
        '''
        # R(F,s|l) = \frac{N(F,s|l)}{\sum_{s,l}N(f,s|l)}

        # Relative frequency with which a language learner hears a from-meaning combination,
        # in the context of language l
        '''
        currently the number of form-meaning pairings is determined by
        the use of a tally which records how many times a particular
        form has been used by an agent in a particular language.
        This a a quantity that can be set depending on the desired
        relative frequency of the forms for a meaning in a language.
        '''

        # this is the numerator: N(f,s|l)
        numberOfPairings = self.Calculate_N_fs_l(form, meaning, language)

        # double summation requires expanding the internal sigma and then computing the outer sigma.
        summationListL = []
        summationListS = []
        # this is the denominator
        # this first loop expands \sum_lN(f,s|l)
        for languages in self.languageRepertoire:
            # this second loop expands \sum_sN(f,s|l)
            for meanings in languages.formMeaningDict:
                # the values of N(f,s|l) for each meaning s
                # are appended onto the list.
                summationListS.append(self.Calculate_N_fs_l(form, meanings, languages))
            # the sums of the list of values from N(f,s |l) are appended
            # to a list which sums over all s within each language
            # in the agent's repertoire.
            summationListL.append(math.fsum(summationListS))
        # sum the frequencies for each language to get a total frequency
        # of occurence for the specific form in all the agent's languages.
        denominator = math.fsum(summationListL)

        # relativeFrequency gives frequency of f,s pair across all languages in the agent's
        # repertoire. Hopefully.
        relativeFrequency = numberOfPairings / denominator

        return(relativeFrequency)

    def Calculate_PM_f_sl(self, form, meaning, language):
        # Equation 1 in Ellison&Miceli 2017
        # P_M(f|s;l) = \frac{R(f,s|l)}{\sum_f R(f,s\l)}
        '''
        Using f for form, s for meaning, and l to denote the language, we express the relative
        frequency (R) with which a language learner hears a form-meaning combination, in the
        context of language l, as R( f, s|l). In this minimal model, the probability (in monolin-
        gual mode: P M ) of using form f on a future occasion to express meaning s in language l
        is the ratio of the relative frequency of the combination to the marginal frequency of
        using that meaning in that language (1).
        '''
        # calculate the relative ferquency of the form in language for meaning
        relativeFrequencyF = self.Calculate_R_fs_l(form, meaning, language)

        # calculate the marginal frequency of using that meaning in that language.
        marginalFrequencyList = []
        for form in language.formMeaningDict[meaning]:
            # calculates the frequency for each form in the language
            marginalFrequencyList.append(self.Calculate_R_fs_l(form, meaning, language))
        # sums the calculated values as in \sum_f R(f,s|l)
        marginalFrequency = math.fsum(marginalFrequencyList)

        return(relativeFrequencyF / marginalFrequency)

    def Calculate_P2M_f_st(self, form, meaning, target):
        # Equation 2 in Ellison&Miceli 2017
        # P_{2M}(f|s;t) = \sum_t \mathrm{\delta}_{l}^{t}P_M(f|s;l)

        # for each language, determine k, multiply k by PM_f_sl, add these to a list, then sum them using fsum.
        # return this value.

        # Summing over languages,, rather than targets here.
        # Instead of checking if each language is the given target,
        # should it instead be checking if each possible target is the given language?
        # Unsure if this makes a difference, as if t != l then the product of k
        # and P_M(f,s|l) is 0 anyway.
        summationList = []
        kroeneckerDelta = 0
        for language in self.languageRepertoire:
            if language is target:
                kroeneckerDelta = 1
            else:
                kroeneckerDelta = 0

            relativeFrequency = self.Calculate_PM_f_sl(form, meaning, language)
            summationList.append(kroeneckerDelta * relativeFrequency)

        p2M = math.fsum(summationList)

        return(p2M)

    def Calculate_PBM_f_s(self, form, meaning, language):
        # Equation 3 in Ellison&Miceli 2017
        # P_{BM}(f|s) = \sum_{l \in L}\frac{1}{|L|}P_M(f|s;l)

        # Don't know the scope of the sum here, may be doing something wrong.
        L = len(self.languageRepertoire)

        summationList = []  # declare a list to sum over.
        for language in self.languageRepertoire:
            # calculate PM for each language
            PM = self.Calculate_PM_f_sl(form, meaning, language)  
            summationList.append(1 / L * PM)  # add product of 1/L and PM to list for summation.

        PBM = math.fsum(summationList)  # sum list.
        return(PBM)

    def Calculate_PG_f_stb(self, form, meaning, target, b_mode, language):
        # Equation 4 in Ellison&Miceli 2017
        # P_G(f|s;t,b) = (1-b)P_{2M}(f|s;t)+bP_{BM}(f|s)

        P2M = self.Calculate_P2M_f_st(form, meaning, target)  # calculate 2M model
        PBM = self.Calculate_PBM_f_s(form, meaning, language)  # calcuclate BM model.

        return((1 - b_mode) * P2M + b_mode * PBM)  # calcualte PG

    def Calculate_k_L(self, form, meaning):
        # k_L(f,s,t,p_G) = k_L(f,s) = \frac{1}{\sum_{l} P_M(f|s;l)}

        # for each language in agent's repertoire, calculate PM
        denominator = math.fsum([self.Calculate_PM_f_sl(form, meaning, language) for language in self.languageRepertoire])
        # 1 / PM = k_L
        return(1 / denominator)

    def Calculate_PL_l_fstbm(self, form, meaning, language, target, b_mode, monitor):
        # Equation 8 in Ellison&Miceli 2017
        # P_L(l|f,s;t,p_G,m) = mk_LP_M(f|s;l)+\frac{1-m}{|L|}

        k_L = self.Calculate_k_L(form, meaning)
        CardinalityOfL = len(self.languageRepertoire)
        PM = self.Calculate_PM_f_sl(form, meaning, language)
        return(monitor * k_L * PM + (1 - monitor) / CardinalityOfL)

    def Calculate_QC_f_stbm(self, form, meaning, language, target, b_mode, monitor):
        # Q_C(f|s;t,b,m) = P_L(l=t|f,s;t,b,m) P_G(f|s;t,b)

        P_L = self.Calculate_PL_l_fstbm(form, meaning, language, target, b_mode, monitor)
        P_G = self.Calculate_PG_f_stb(form, meaning, target, b_mode, language)

        Q_C = P_L * P_G
        return(Q_C)

    def Calculate_PC_f_stbm(self, form, meaning, language, target, b_mode, monitor):
        # k_c(s;t,b,m) = \frac{1}{\sum_f Q_c(f|s;t,b,m)}

        summationList = []
        for forms in target.formMeaningDict[meaning]:
            summationList.append(self.Calculate_QC_f_stbm(forms, meaning, language, target, b_mode, monitor))
        k_C = 1 / math.fsum(summationList)

        # P_C(f|s;t,b,m) = k Q_C(f|s;t,b,m)
        P_C = k_C * self.Calculate_QC_f_stbm(form, meaning, language, target, b_mode, monitor)
        return(P_C)

    def step(self):
        print("step start:")
        #select a meaning to be produced at random. This is the target meaning.
        meaning = self.select_meaning()

        # a list to hold tuples containing the form, likelyhood of production,
        # and the language to which it belongs.
        likelyhoods = []

        # for every language in the agent's repertoire,
        # calculate the likelyhood of producing a form f
        # for the meaning s in that language.
        for language in self.languageRepertoire:
            for form in language.formMeaningDict[meaning]:
                likelyhoods.append((form,
                                    self.Calculate_PC_f_stbm(
                                        form, meaning, language,
                                        self.Community.communityLanguage,
                                        self.mode, self.monitoring),
                                    language.languageName))

            # a list to hold the likelyhood calculations to check they sum to 1
            totalOfLikelyhoods = []
            for i in range(len(likelyhoods)):
                # take the likelyhood calulated for each for from the tuple for summation.
                totalOfLikelyhoods.append(likelyhoods[i][1])
                # the total of the likelyhoods should sum to 1, I believe
                # it currently does not.

        # have some output.
        print("I am Agent {}, I am in community {}, and I speak {}".format(
            self.name, self.Community.communityName, str(
                [language.languageName for language in self.languageRepertoire])))
        print(meaning)
        print(likelyhoods)
        # the following is mostly not 1 as it should be
        print(math.fsum(totalOfLikelyhoods))
        print("step end\n")

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
            communityConnections = [tuple(elem for elem in sub if elem != community) for sub in
                                    list(network.edges.data("weight")) if community in sub]
            # calculate the weight of the native community l1
            weightOfCommunityL1 = 1 - math.fsum([i[1] for i in communityConnections])
            # include this in the possible choices for assigning a language.
            communityConnections.append((community, weightOfCommunityL1))
            for population in range(community.communitySize):
                # returns a list of the choices. This list is a single value as only 1 choice is being made.
                communityOfL1 = self.random.choices([i[0] for i in communityConnections],
                                                    [j[1] for j in communityConnections], k=1)
                # take the 0th item in the list (the language object) and select this as the l1.
                agentL1 = communityOfL1[0].communityLanguage
                speaker = Speaker_Agent(currentPopulation, self, agentL1, mode, monitoring)
                community.add_members(speaker)
                speaker.define_community(community)
                # make the agent speak the community language, if it is not their l1
                if(speaker.L1 is not community.communityLanguage):
                    speaker.language_repertoire_add(community.communityLanguage)
                # determine how many languages the agent can speak
                numberOfLanguagesSpoken = self.random.choices(
                    [i + 1 for i in range(len(languageObjectList))],
                    [0.6, 0.5, 0.4, 0.3, 0.2, 0.1], k=1)
                if(len(communityConnections) > 1
                   and numberOfLanguagesSpoken[0] > len(speaker.languageRepertoire)):
                    currentNumberOfLanguages = len(speaker.languageRepertoire)
                    for i in sorted(communityConnections, key=lambda x: x[1]):
                        if(i[0].communityLanguage not in
                           speaker.languageRepertoire
                           and currentNumberOfLanguages <= numberOfLanguagesSpoken[0]):
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
# from model import DivergenceModel
# from model import Language
# from model import Community
# import networkx as nx

# ensure the languages exist.
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
    # clear the dict to ensure the "vocabulary" is empty.
    eachlanguage.formMeaningDict.clear()
# for testing I include 2 meanings. All are 50-50 frequencies for ease,
# and there are some doppels.
language1.add_meaning("Lizard", ([("wiri-wiri", 50, 0), ("mirdi", 50, 0)]))
language2.add_meaning("Lizard", ([("wiri-wiri", 50, 0)]))
language3.add_meaning("Lizard", ([("wiri-wiri", 50, 0), ("mirdi", 50, 0), ("marnara", 50, 0)]))
language4.add_meaning("Lizard", ([("julirri", 50, 0), ("jindararda", 50, 0)]))
language5.add_meaning("Lizard", ([("jindararda", 50, 0), ("wiri-wiri", 50, 0)]))
language6.add_meaning("Lizard", ([("mirdi", 50, 0), ("jindararda", 50, 0)]))

language1.add_meaning("kangaroo", ([("yawarda", 50, 0), ("marlu", 50, 0)]))
language2.add_meaning("kangaroo", ([("yawarda", 50, 0)]))
language3.add_meaning("kangaroo", ([("marlu", 50, 0)]))
language4.add_meaning("kangaroo", ([("yawarda", 50, 0)]))
language5.add_meaning("kangaroo", ([("yawarda", 50, 0), ("marlu", 50, 0)]))
language6.add_meaning("kangaroo", ([("marlu", 50, 0)]))

# define the communities to which agent's can belong.
# this determines which language they speak natively.
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
socialNet.add_weighted_edges_from([
    (community1, community6, 0.125), (community6, community5, 0.5),
    (community1, community5, 0.1), (community2, community5, 0.1),
    (community6, community4, 0.01), (community2, community4, 0.4)])


# make the model.
testingModel = DivergenceModel(languageList, communityList, socialNet, 0.54, 0.84)
# step the model once.
# can be put in a loop to run many times.
# determining number of loops and other parameters will be done by the runner script
# when it is developed.
testingModel.step()
