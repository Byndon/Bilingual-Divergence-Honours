from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.batchrunner import BatchRunner
import math
import itertools
import numpy as np
import pandas
import csv
import networkx as nx  # used for connecting communtiy agents. Maybe used for connecting agents in large numbers in a more complex simulation.
import pprint


def get_frequencies(model):
    all = {}
    for language in model.languages:
        meanings = {}
        for meaning in language.formMeaningDict:
            forms = []
            frequencies = []
            for form in language.formMeaningDict[meaning]:
                forms.append(form[0])
                frequencies.append(form[1])
            zippedList = list(itertools.zip_longest(forms, frequencies, fillvalue=None))
            meanings[meaning] = zippedList
        all[language.languageName] = meanings
    return(all)  # perhaps retrn all langage dictionaries as separate variables?


def get_frequencies_table(language):
    dictionaryOfFreq = {}
    for meaning in language.formMeaningDict:
        for form in language.formMeaningDict[meaning]:
            dictionaryOfFreq[str(form[0] + ":" + meaning)] = form[1]

    return(dictionaryOfFreq)


class Idiolect:
    '''
    This is an individiual agent's internal representation of their languages.
    It is almost identical to the language class, in terms of the variables that it tracks,
    but doesn't have overhead in terms of importing or borrowing, or tracking speakers.

    Currently not in use
    '''
    def __init__(self, languagesList):
        self.speaker = None
        if(type(languagesList) is list):
            self.languages = languagesList
        else:
            print("Languages in idiolect are not a list: None")
            self.languagesList = None

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
        if(self in speakerAgent.languageRepertoire):
            self.speakers.append(speakerAgent)
            return(True)
        else:
            return(False)
        
    def calc_form_frequency(self, form, meaning):
        totalTally = 0
        formTally = form[1]
        for forms in self.formMeaningDict[meaning]:
            totalTally += forms[1]
        frequency = formTally / totalTally
        return(frequency)
            
    def borrow_form(self, meaning):
        # this has not been tested!
        # this function is for the chance for a language to gain a borrowing.
        # Borrowings should be marked accordingly with an addition to the
        # string indicating where they were brrowed from.

        # currently this won't work for monolingual communities,
        # as there are by definition no bilinguals

        # make a list of bilingual speakers, so that i don't choose something which will cause
        # an endless loop of this function calling itself.
        bilinguals = [speaker for speaker in self.speakers if len(speaker.languageRepertoire) > 1]

        # select a random bilingual. The selection biases of how probable it is to borow from another
        # language should be present in the population. So there is a very low chance that
        # this will borow a form from a language with few speakers.
        speaker = DivergenceModel.random.choice(bilinguals)

        # select a language to borrow from from the chosen biligual's repertoire.
        # to fix: just take out the damn community language from the list.
        speakerOtherLanguages = []
        for i in speaker.languageRepertoire:
            if(i is not self):
                speakerOtherLanguages.append(i)

        languageBorrowedFrom = DivergenceModel.random.choice(speakerOtherLanguages)
        # base case, no recursion
        if(languageBorrowedFrom is not self):
            borrowedForm = DivergenceModel.random.choice(languageBorrowedFrom.formMeaningDict[meaning])
        # call this function again if we choose this language to borrow from.
        elif(languageBorrowedFrom is self):
            self.borrow_form(meaning)
        # this shouldn't happen, but something might break, who knows.
        else:
            borrowedForm = (None, 0, 0+1e-20, languageBorrowedFrom)
            print("something has gone wrong when borrowing a form.")

        # edit the borrowed form to make a new "borrowed form" tuple.
        # the frequency of the borrowed form is maintained. Perhaps it should be an average of all the forms in use in this language?
        borrowedFormNew = (borrowedForm[0], borrowedForm[1] / 2, 0,
                           borrowedForm[3])
        # append the form onto the value list for the key meaning selected.
        self.formMeaningDict[meaning].append(borrowedFormNew)

    def lose_form(self, lossLimit):
        # this has not been tested!
        # this function is for the chance that a form becomes so obscure that
        # it is no longer used in the language.
        # This can also occur randomly to kick-start the bias process.
        # need to figure out the randomness before implementing.
        for meaning in self.formMeaningDict:
            for form in self.formMeaningDict[meaning]:
                if(form[1] < lossLimit):
                    # find the tuple that is "form" and delete it from the
                    # value list for the key "meaning".
                    oldList = self.formMeaningDict[meaning]
                    oldList.remove(form)
                    self.formMeaningDict[meaning] = oldList
                    print("removed: {} from {}".format(form[1], language.languageName))
                    if(len(oldList) == 0):  # i.e. no more forms for a meaning
                        # this is basically impossible to trigger, as if somebody only has one option, they will hav to use it to express the associated meaning and it will be 100% by default.
                        self.borrow_form(meaning)

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

    '''
    Current Issues:
    - Doppels can be > 50% chance. Anti-doppel bias should not allow this (?)
    -- e.g. speakers of language 4 and 6 will have the doppel "Marlu" as a certainty.
    -- i.e. probability = 1.0

    - currently, language target combinations where there is no exact match between the
    -- language forms and the forms present in the target language.
    -- i.e if target has 2 forms jindararda and wiri-wiri, but the loop has got to the form
    -- mirdi, which is also in the agent's repertoire, it often calculates probabilities > 1.0
    -- likley due to how I am looping through the forms, languages, and targets.
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
        self.lastMeaning = "Nothing"

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
        elif(0 <= mode and mode <= 1):
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
        # out of convenience. All languages can express the same meanings.

        # make a random choice from a list of the dictionary keys.
        meaningChosen = self.random.choice(list(self.languageRepertoire[0].formMeaningDict.keys()))

        return(meaningChosen)

    # below this comment, is the calculations for the bilingual mode and monitoring model. E&M 2017.
    def Calculate_N_fs_l(self, form, meaning, language):
        # N(f,s|l) = |\{i \in 1..n_l|S_{l,i} = (f,s)\}|
        numberOfPairings = 0
        for formString in language.formMeaningDict[meaning]:
            formItems = [i[0] for i in language.formMeaningDict[meaning]]
            if(formString[0] == form[0] and form[0] in formItems):
                numberOfPairings = formString[1]
                # there shouldn't be any occurences of more
                # than 1 of the same form for a particular meaning.
            # there was a break here
        return(numberOfPairings)

    def Calculate_R_fs_l(self, form, meaning, language):
        # currently unused as of 2021/20/05
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
        # R(F,s|l) = \frac{N(F,s|l)}{\sum_{s,f}N(f,s|l)}

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
        summationListL = []  # was previous summationListF
        summationListS = []

        # THERE MAY BE AN ERROR HERE:
        # does this actually do what it says?
        # it appears as if it doesn't sum over languages, as it only looks at one language right now.
        # this IS WRONG. Needs something along the lines of:

        for language in self.languageRepertoire:
            for meaning in language.formMeaningDict:
                for each_form in language.formMeaningDict[meaning]:
                    if(each_form[0] == form[0]):
                        summationListS.append(self.Calculate_N_fs_l(form, meaning, language))
            summationListL.append(math.fsum(summationListS))
        
        # this is the denominator
        # this first loop expands \sum_lN(f,s|l)
        # for languages in self.languageRepertoire:
        #     # this second loop expands \sum_sN(f,s|l)
        #     for meanings in languages.formMeaningDict:
        #         # the values of N(f,s|l) for each meaning s
        #         # are appended onto the list.
        #         summationListS.append(self.Calculate_N_fs_l(form, meanings, languages))
        #     # the sums of the list of values from N(f,s |l) are appended
        #     # to a list which sums over all s within each language
        #     # in the agent's repertoire.
        #     summationListL.append(math.fsum(summationListS))

        # for meanings in language.formMeaningDict:
        #     for forms in language.formMeaningDict[meanings]:
        #         summationListF.append(self.Calculate_N_fs_l(forms, meanings, language))
        #     summationListS.append(math.fsum(summationListF))
                                      
                
        # sum the frequencies for each language to get a total frequency
        # of occurence for the specific form in all the agent's languages.
        denominator = math.fsum(summationListS)

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
        # old code start
        # calculate the relative ferquency of the form in language for meaning
        # relativeFrequencyF = self.Calculate_R_fs_l(form, meaning, language)

        # # calculate the marginal frequency of using that meaning in that language.
        # marginalFrequencyList = []
        # for form in language.formMeaningDict[meaning]:
        #     # calculates the frequency for each form in the language
        #     marginalFrequencyList.append(self.Calculate_R_fs_l(form, meaning, language))
        # # sums the calculated values as in \sum_f R(f,s|l)
        # marginalFrequency = math.fsum(marginalFrequencyList)

        # return(relativeFrequencyF / marginalFrequency)
        # old code end

        #P_M(f|s;l) = \frac{N(f,s|l)}{\sum_fN(f,s|l)}
        n_fs__l = self.Calculate_N_fs_l(form, meaning, language)
        sum_n_fs__l_list = []
        for form in language.formMeaningDict[meaning]:
            sum_n_fs__l_list.append(self.Calculate_N_fs_l(form, meaning, language))

        sum_n_fs__l = math.fsum(sum_n_fs__l_list)

        return(n_fs__l / sum_n_fs__l)
    

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

    def Calculate_PL_l_fstbm(self, form, meaning, target, b_mode, monitor):
        # Equation 8 in Ellison&Miceli 2017
        # P_L(l|f,s;t,p_G,m) = mk_LP_M(f|s;l)+\frac{1-m}{|L|}

        k_L = self.Calculate_k_L(form, meaning)
        CardinalityOfL = len(self.languageRepertoire)
        PM = self.Calculate_PM_f_sl(form, meaning, target)  # pass target instead of language. No need for language argument. 
        return(monitor * k_L * PM + (1 - monitor) / CardinalityOfL)

    def Calculate_QC_f_stbm(self, form, meaning, language, target, b_mode, monitor):
        # Q_C(f|s;t,b,m) = P_L(l=t|f,s;t,b,m) P_G(f|s;t,b)

        P_L = self.Calculate_PL_l_fstbm(form, meaning, target, b_mode, monitor)
        P_G = self.Calculate_PG_f_stb(form, meaning, target, b_mode, language)

        Q_C = P_L * P_G
        return(Q_C)

    def Calculate_PC_f_stbm(self, form, meaning, language, target, b_mode, monitor):
        # k_c(s;t,b,m) = \frac{1}{\sum_f Q_c(f|s;t,b,m)}

        summationList = []
        '''
        print("Calculate_PC_f_stbm:")
        print("  target.formMeaningDict:", " ".join(map(
            lambda x: str(x[0]), target.formMeaningDict[meaning])), " = P(%s|%s,%s)" % (
                form, meaning, language.languageName))
        '''
        # lambda x: str(x[0]) takes the 0th item in the list x and converts it to a string.

        # this calculates probabilities for each form in the target.
        # fixing goes here: Need to do this for all forms from all languages in the repertoire,
        # but only with the target language as t. No feeding in other languages. 09042021##
        for language in self.languageRepertoire:
            for forms in language.formMeaningDict[meaning]:  # language was target on this line.j
                x = self.Calculate_QC_f_stbm(forms, meaning, target, target, b_mode, monitor)
                summationList.append(x)
        # then we sum the probabilities and create a normalising constant
        # such that they sum to 1 when multiplied by this constant
        k_C = 1.0 / math.fsum(summationList)

        # P_C(f|s;t,b,m) = k Q_C(f|s;t,b,m)
        # TME: When I print out all the forms (above) for a given meaning, I get a list which sometimes does not include
        #      the value of "form", e.g. the list is "julirri jindararda" and the value of form is "wiri-wiri"
        #      Agent 31, Language6
        #      As a result, k_C will be less than the sum of the values including P(wiri-wiri|..)

        ''' 
        CB:
        So the code in step() loops through each language in the agent's repertoire.
        Within this loop it loops through each form which exists
        for that meaning in the current language.

        This is for the purpose of getting a bunch of probabilities of how likely the agent
        is to produce any form, from any language for the given meaning.

        So, the forms in the target dictionary do not always correspond to the current form
        for which the probability of use (given the intended meaning) is being calculated.

        This means we could be calculating the probability of producing the (1) form wiri-wiri,
        from language4, given that the target language is language6,
        which has 2 forms: Julirri and Jindararda.

        This isthe agent asking: what is the probability that I produce a word from a language
        which is not my target language? This should be a relatively low probability.
        
        CB 20213003: I am not sure if I was correct here. The normalising constant should be capable of normalising for the language currently being used to compute the probability. ?
        '''
        '''
        print("k_C: ", k_C)
        print("  PC_f_stbm:", 1.0 / k_C, meaning, language.languageName, target.languageName)
        '''
        # CB: do we want to print 1.0/k_C here? 1/k_C is the inverse of the variable k_C.
        # so if k_C was 25, 1/k_C would be 0.04.
        # what is the range of values of k_C
        # Equation 11 in Ellison&Miceli 2017
        P_C = k_C * self.Calculate_QC_f_stbm(form, meaning, target, target, b_mode, monitor)

        # check for rounding error 0.99 recurring.
        # x = 10 * P_C
        # y = 9 * P_C
        # if(x - y == 1.0):
        #     P_C = 1.0
        return(P_C)

    def step(self):
        # make a list of meanings
        meanings = [i for i in self.L1.formMeaningDict]
        # make probabilites such that each form is equally likely to be selected for production
        probabilities = [1 for i in meanings]
        # select 100 random meanings from the list of meanings
        chooseMeanings = self.random.choices(meanings, probabilities, k=100)
        # ensure the list of chosen forms is unique
        chooseMeanings = list(np.unique(chooseMeanings))

        # define the target to be communityLanguage
        target = self.Community.communityLanguage
        # next step is to calculate probabilities for forms belonging to the meanings selected
        dictOfProbabilities = {}
        for meaning in chooseMeanings:
            allFormsForMeaning = []
            doppelDict = {}
            # ensure doppels are unique in the caclulations
            for language in self.languageRepertoire:
                for form in language.formMeaningDict[meaning]:
                    formStrings = [i[0] for i in allFormsForMeaning]
                    if(form[0] in formStrings):
                        currentForm = [i for i in allFormsForMeaning if i[0] is form[0]]
                        currentFrequency = currentForm[0][1]
                        if(form[0] not in doppelDict):
                            doppelDict[form[0]] = [currentFrequency, form[1]]
                        else:
                            doppelDict[form[0]].append(form[1])

                        # averageOfFrequencies = (currentFrequency + form[1]) / 2
                        # newForm = (form[0], averageOfFrequencies)
                        # index = allFormsForMeaning.index(currentForm[0])
                        # allFormsForMeaning[index] = newForm
                    else:
                        allFormsForMeaning.append(form[:2])
            # doppels need to be avaerage scores of the doppel form over all the agent's languages.
            for entry in doppelDict:
                average = math.fsum(doppelDict[entry]) / len(doppelDict[entry])
                newForm = (entry, average)
                indexingList = [i[0] for i in allFormsForMeaning]
                index = indexingList.index(entry)
                allFormsForMeaning[index] = newForm

            likelyhoods = []
            for form in allFormsForMeaning:
                p = self.Calculate_PC_f_stbm(
                    form, meaning, target, target,
                    self.mode, self.monitoring)
                likelyhoods.append((form, p))

            dictOfProbabilities[meaning] = likelyhoods

        for i in range(100):
            dictionaryList = []
            meaning = self.random.choice(list(dictOfProbabilities))
            formsAndPs = dictOfProbabilities[meaning]
            formChosenAsList = self.random.choices([i[0][0] for i in formsAndPs],
                                                   [i[1] for i in formsAndPs], k=1)
            formChosenString = formChosenAsList[0]
            for form in target.formMeaningDict[meaning]:
                if(formChosenString == form[0]):
                    form = (form[0], form[1], form[2] + 1, form[3])
                else:
                    form = form
                dictionaryList.append(form)
            target.formMeaningDict[meaning] = dictionaryList

        # pprint.pprint(target.formMeaningDict)


class DivergenceModel(Model):
    def __init__(self, languageObjectList, communityObjectList, network, mode=False, monitoring=False, seed=12345):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.model_population = sum([community.communitySize for community in communityObjectList])
        self.languages = languageObjectList
        self.network = network
        self.running = True

        currentPopulation = 0
        for community in communityObjectList:
            # get the current community's connections and their weights from the list of edges.
            # communities without any connections return an empty list
            # this particular list comprehension returns a list of tuples but strips the tuple of the current community for convenience.
            communityConnections = [tuple(elem for elem in sub if elem != community) for sub in
                                    list(network.edges.data("weight")) if community in sub]
            # calculate the weight of the native community l1
            # need to normalise this to conserve weights.
            weights = [i[1] for i in communityConnections]
            weightOfCommunityL1 = 1
            # the weight of the community will always be 1 (highest weight)
            weights.append(weightOfCommunityL1)
            normalisingTerm = 1 / math.fsum(weights)  # calculate nromalising term
            newWeights = [normalisingTerm * i for i in weights]
            # use normalising term to determine relative weights.
            # weightOfCommunityL1 = 1 - math.fsum([i[1] for i in communityConnections])  # OLD 
            # weightOfCommunityL1 =  # no longer needed as we are calculating the weights differently.
            # include this in the possible choices for assigning a language.
            communityConnections.append((community, weightOfCommunityL1))

            for population in range(community.communitySize):
                # returns a list of the choices. This list is a single value as only 1 choice is being made.
                communityOfL1 = self.random.choices([i[0] for i in communityConnections],
                                                    newWeights, k=1)  # weights was [j[1] for j in communityConnections] #restore to newWeights after testing 07-05-21: done
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
                    [0.6, 0.5], k=1)
                # [0.6, 0.5, 0.4, 0.3, 0.2, 0.1], k=1)  # has to be same number of these as number of languages, or else it has errors in random library.
                    
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


        # The next few list comprehensions are set up for ensuring the conditions of the simulation populations on p.275 of Ellison&Miceli 2017
        # use only the next two lines for 10a.
        [agent.languageRepertoire.remove(language2) for agent in self.schedule.agents if agent.Community != community2 and len(agent.languageRepertoire) > 1]
        [agent.languageRepertoire.remove(language1) for agent in self.schedule.agents if agent.Community != community1 and len(agent.languageRepertoire) > 1]
        # # use the following two lines in addition for 10c.
        [agent.languageRepertoire.append(language1) for agent in self.schedule.agents if agent.Community != community1 and agent.name <= 75]
        [agent.languageRepertoire.append(language2) for agent in self.schedule.agents if agent.Community != community2 and agent.name <= 25]
        # use the following in addition for 10b.
        # [agent.languageRepertoire.append(language1) for agent in self.schedule.agents if agent.Community != community1]
        # this is where that set up ends
        # add_speakers to speaker roster for each language
        for language in languageList:
            for agent in self.schedule.agents:
                language.add_speaker(agent)

        
        for agent in self.schedule.agents:
            print("Agent:", agent.name, "| Repertoire:",
                  ",".join([lang.languageName for lang in agent.languageRepertoire]),
                  "| Community:", agent.Community.communityName)
        self.datacollector = DataCollector(
            model_reporters={"Frequencies": get_frequencies},
            agent_reporters={"mode": "mode", "monitoring": "monitoring"}
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        # increase the tally based on how many times each form was prodcued by an agent
        for language in self.languages:
            # print(language.languageName)
            for meaning in language.formMeaningDict:
                # print("\t", meaning)
                dictionaryList = []
                normalisingTerm = 100 / sum([form[2] for form in language.formMeaningDict[meaning]])
                for form in language.formMeaningDict[meaning]:
                    form = (form[0], normalisingTerm * form[2], 0 + 1e-20, form[3])
                    # print("\t\t", form[:2])
                    # don't sum old tally and the new tally. Agents should instead be re-born with the new frequencies of the last generation, rather than having an infinitely long memory. - advice from Mark

                    dictionaryList.append(form)
                language.formMeaningDict[meaning] = dictionaryList
            
        # I want to normalise the frequency tallies here. Maybe
        # make a list of the total usages (index 1 in the tuple)
        # 100/math.fsum(list of usages)
        # make a new tuple, where normalisingTerm is multiplied by the original term.
        # OR do I? I want each step to be dependent only on the previous steps prodcutions.
        print("step start")
        for language in languageList:
            for meaning in language.formMeaningDict:
                for form in language.formMeaningDict[meaning]:
                    print(form[:2], language.languageName)
        print("step end")
# define language objects.
# i don't currently care about the words and stuff
# next 4 lines just for when it is split in org-source blocks
# from model import DivergenceModel
# from model import Language
# from model import Community
# import networkx as nx


# ensure the languages exist.
language1 = Language("Language1")
language2 = Language("Language2")
# language3 = Language("Language3")
# language4 = Language("Language4")
# language5 = Language("Language5")
# language6 = Language("Language6")

# make a list of the languages to give to the model.
languageList = [language1, language2]  # , language3]  # , language4, language5, language6]

# input some meanings and forms into the languages
for eachlanguage in languageList:
    # clear the dict to ensure the "vocabulary" is empty.
    eachlanguage.formMeaningDict.clear()
# for testing I include 2 meanings. All are 50-50 frequencies for ease,
# and there are some doppels.
language1.add_meaning("Lizard", [("mirdi", 45, 0 + 1e-20, language1), ("wiri-wiri", 55, 0 + 1e-20, language1)])# [("wiri-wiri", 50, 0 + 1e-20, language1), ("mirdi", 50, 0 + 1e-20, language1)])
language2.add_meaning("Lizard", [("julirri", 50, 0 + 1e-20, language2), ("wiri-wiri", 50, 0 + 1e-20, language2)])# [("wiri-wiri", 50, 0 + 1e-20, language2), ("julirri", 50, 0 + 1e-20, language2)])
# language3.add_meaning("Lizard", [("wiri-wiri", 100, 0, language3), ("mirdi", 100, 0, language3), ("marnara", 100, 0, language3)])
# language4.add_meaning("Lizard", [("julirri", 100, 0, language4), ("jindararda", 100, 0, language4)])
# language5.add_meaning("Lizard", [("jindararda", 100, 0, language5), ("wiri-wiri", 100, 0, language5)])
# language6.add_meaning("Lizard", [("mirdi", 100, 0, language6), ("jindararda", 100, 0, language6)])

language1.add_meaning("kangaroo", [("yawarda", 50, 0 + 1e-20, language1), ("marlu", 50, 0 + 1e-20, language1)])
language2.add_meaning("kangaroo", [("yawarda", 55, 0 + 1e-20, language2), ("ganguru", 45, 0 + 1e-20, language2)])

# language3.add_meaning("kangaroo", [("marlu", 100, 0, language3)])
# language4.add_meaning("kangaroo", [("yawarda", 100, 0, language4)])
# language5.add_meaning("kangaroo", [("yawarda", 100, 0, language5), ("marlu", 100, 0, language5)])
# language6.add_meaning("kangaroo", [("marlu", 100, 0, language6)])

# define the communities to which agent's can belong.
# this determines which language they speak natively.
community1 = Community("Com1", language1, 50)
community2 = Community("Com2", language2, 50)
# community3 = Community("Com3", language3, 50)
# community4 = Community("Com4", language4, 10)
# community5 = Community("Com5", language5, 10)
# community6 = Community("Com6", language6, 10)

communityList = [community1, community2]  # , community3]  #, community4, community5, community6]
# create network
socialNet = nx.Graph()
# create nodes from list of community objects
# community objects ARE the nodes in this model
socialNet.add_nodes_from(communityList)
# add weighted connections between the nodes.
# socialNet.add_edge(community1, community2, weight=0.0)
socialNet.add_weighted_edges_from([(community1, community2, 0.125)])  #, (community2, community3, 0.5)])
#     (community1, community6, 0.125), (community6, community5, 0.5),
#     (community1, community5, 0.1), (community2, community5, 0.1),
#     (community6, community4, 0.01), (community2, community4, 0.4)])


# make the model.
testingModel = DivergenceModel(languageList, communityList, socialNet, .5, .8)  #b, m
# step the model once.
# can be put in a loop to run many times.
# determining number of loops and other parameters will be done by the runner script
# when it is developed.
# self, languageObjectList, communityObjectList, network, mode=False, monitoring=False, seed=12345
# fixed_params = {
#     "languageObjectList": languageList,
#     "communityObjectList": communityList,
#     "network": socialNet
# }

# variable_params = {
#     "mode": numpy.arange(0.0, 1.1, 0.1),
#     "monitoring": numpy.arange(0.0, 1.1, 0.1)
# }

# batch_run = BatchRunner(
#     DivergenceModel,
#     variable_params,
#     fixed_params,
#     iterations=5,
#     max_steps=100,
#     model_reporters={"Frequencies": get_frequencies}
# )

# batch_run.run_all()
stepCounter = 0
for i in range(35):
    print(str(stepCounter))
    testingModel.step()
    stepCounter += 1
    if(stepCounter % 5 == 0):
        for language in languageList:
            language.lose_form(5.0)
        
    # need a better way of dealing with the model data. it's just a dictionary containing dictionaries, which is messy.
dataframeModel = testingModel.datacollector.get_model_vars_dataframe()
dataframeAgents = testingModel.datacollector.get_agent_vars_dataframe()
