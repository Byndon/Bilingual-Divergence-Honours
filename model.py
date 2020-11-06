from mesa import Agent, Model
from mesa.time import RandomActivation
import multilevel_mesa as mlm
import pandas
import csv


def function():
    pass

class language:
    def __init__(self, LanguageName):
        self.LanguageName = LanguageName
        self.formMeaningDict = {}
        self.speakers = []

    def add_from_file(filename):
        # this method will be able to take a file, formatted as CSV
        # and turn it into a dictionary with Meaning Keys, and
        # a list of tuples with Form and Relative frequency
        # relative frequency should be a parameter
        # if we have enough information, BUT
        # can also be randomly determined.
        pass

    def add_meaning(self, meaning, formTupleList):
        if(type(formTupleList) is list):
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

    def language_repertoire_add(self, language):
        self.language_repertoire.append(language)

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
                i += j/len(langObj)  # calculate the percentage of shared languages between self and currentspeaker.
            mode += i/len(sameLangSpeakers) # set mode to the average of repertoire.
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

    def step(self):
        # implement step here.
        # From community/group language, choose
        #     a meaning at random.
        # Attempt to produce the target form
        #     using the Pc Model
        # Whichever form was produced, add 1 to the NewTally, for use in the next step.
        #     (if not in target language do nothing?)
        #     (It forms a tally of words, we can produce a percentage)
        print("I am SpeakerAgent {}, my language is {}, I am monitoring with an intensity of {} and my bilingual mode is {}".format(self.name, self.language_repertoire[0].LanguageName, str(self.monitoring), str(self.mode)))
        return(True)

class DivergenceModel(Model):
    def __init__(self, model_population, language_object_list, seed=12345):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.model_population = model_population
        self.languages = language_object_list

        current_l1 = 0
        speakers_per_language = int(model_population/len(language_object_list))
        speaker_count = 1
        for i in range(model_population):
            if(speaker_count <= speakers_per_language):
                speaker = SpeakerAgent(i, self, language_object_list[current_l1])
                self.schedule.add(speaker)
                language_object_list[current_l1].add_speaker(speaker)  # added here
                speaker_count += 1
            elif(speaker_count > speakers_per_language):
                current_l1 += 1
                speaker_count = 0

    def step(self):
        self.schedule.step()
        print("done")
        # here i must also set the NewTally equal to the Tally, so that the new frequencies can be used in the next time step, unless the frequency being updated with each use is intended.

# define language objects.
# i don't currently care about the words and stuff
Language1 = language("Language1")
Language2 = language("Language2")
Language3 = language("Language3")
# make a list of the languages to give to the model.
languageList = [Language1, Language2, Language3]

# make the model. 
testingmodel = DivergenceModel(30, languageList)
# step the model once.
testingmodel.step()

# fix this it needs to step over each agent and add another random language to its language repertoire
# for i in languageList:
#     for j in languageList[i].speakers:
#         randomLang = random.randint(0,2)
#         languageList[i].speakers[j].language_repertoire_add(languageList[randomLang])
