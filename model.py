from mesa import Agent, Model
import multilevel_mesa as mlm
import pandas
import csv

class language:
    def __init__(self, LanguageName):
        self.LanguageName = LanguageName
        self.formMeaningDict = {}
        self.speakers = ()

    def add_from_file(filename):
        # this method will be able to take a file, formatted as CSV
        # and turn it into a dictionary with Meaning Keys, and
        # a list of tuples with Form and Relative frequency
        # relative frequency should be a parameter, but
        # can also be randomly determined.
        pass

    def add_speaker(self, SpeakerAgent):
        if(SpeakerAgent.L1 is self):
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
        self.monitoring = 0
        self.language_repertoire_add(L1)

    def language_repertoire_add(self, language):
        self.language_repertoire.append(language)

    def set_language_mode(self, mode, L1):
        if mode is False:
            self.mode = self.random.uniform(0, 1)
        elif mode is True:
          # This need to be checked for issues, I'm not thinking right now. 
            k = 0
            i = 0
            for sameLangSpeakers in L1.speakers:
                j = 0
                for lang in sameLangSpeakers:
                    if(lang in self.language_repertoire):
                        j += 1
                i += j/len(lang)
            k += i/len(sameLangSpeakers)
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
        # Whichever form was produced, add 1 to the usage of it.
        #     (if not in target language do nothing?)
        #     (It forms a tally of words, we can produce a percentage)
        pass

class DivergenceModel(Model):
    def __init__(self, seed=12345):
        super().__init__()
        self.schedule = mlm.Multilevel_Mesa(self)

        for a in range(model_population):
            a = Agent()
            self.schedule.add(a)

    def step(self):
        self.schedule.step()
