from mesa import Agent, Model
import multilevel_mesa as mlm
import pandas

class language:
    def __init__(self):
        self.formMeaningDict = {}

    def add_from_file(file):
        # this method will be able to take a file, formatted as CSV
        # and turn it into a dictionary with Meaning Keys, and
        # a list of tuples with Form and Relative frequency
        # relative frequency should be a parameter, but
        # can also be randomly determined.
        pass

class SpeakerAgent(Agent):
    def __init__(self, name, model):
        super().__init__(name, model)
        self.name = name
        self.language_repertoire = []
        self.mode = 0
        self.monitoring = 0

    def language_repertoire_add(self, language):
        self.language_repertoire.append(language)

    def language_mode(self, mode):
        if mode is False:
            self.mode = self.random.uniform(0, 1)
        elif mode is True:
            # determine mode based on others in the community.
            pass
        else:
            if(0 < mode and mode < 1):
                self.mode = mode

    def monitoring_level(self, monitoring):
        if monitoring is False:
            self.monitoring = random.uniform(0,1)
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
    def __init__(self):
        super().__init__()

    def step(self):
        self.schedule.step()
