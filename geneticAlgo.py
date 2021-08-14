import model as mdl
import LanguagesAndCommunities as lac
import random
import numpy
import math
import csv
import networkx as nx
# import pprint
# import matplotlib.pyplot as plt

random.seed(12345)


def diff(x_list):
    return(x_list[0] - x_list[1])


def invert(x):
    return(100 - x)


def run_model(model, steps, lossLimit):
    # print((model.mode, model.monitoring))
    stepCounter = 0
    for i in range(steps):
        model.step()
        # if(stepCounter % 5 == 0):
        #     for language in model.languages:
        #         language.lose_form(lossLimit)
        stepCounter += 1

    # determine percentage of lexical items which are shared between 2 languages connected by an edge in the network
    sharedVocabPerCents = []
    for edge in model.network.edges:
        lang1Forms = []
        lang2Forms = []
        language1, language2 = edge[0].communityLanguage, edge[1].communityLanguage
        # get all forms for language1 (node 0) and put them in a list
        for meaning in language1.formMeaningDict:
            for form in language1.formMeaningDict[meaning]:
                lang1Forms.append(form[0])
        # get all forms for language2 (node 1) and put them in a list
        for meaning in language2.formMeaningDict:
            for form in language2.formMeaningDict[meaning]:
                lang2Forms.append(form[0])
        # get the length of forms
        totalL1Forms = len(lang1Forms)
        totalL2Forms = len(lang2Forms)
        # get the forms which appear in both lists only
        sharedForms = [y for x in (lang1Forms, lang2Forms) for y in x if y in lang1Forms and y in lang2Forms]

        # calculate the percentage of items that are shared between the two lists.
        perCentShared = len(sharedForms) / (totalL1Forms + totalL2Forms)
        sharedVocabPerCents.append(perCentShared)  # also should have which edges they are for spotting issues

    listOfTables = [(i.languageName, model.datacollector.get_table_dataframe(i.languageName), i) for i in model.languages]
    for i in listOfTables:
        # make a filename
        filename = 'outputs/' + i[0] + ".csv"
        # write out csv files for each langauge.
        with open(filename, 'a+') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(("Chromosome", i[2].speakers[0].mode, i[2].speakers[0].monitoring, "Network Weights", nx.get_edge_attributes(model.network, "weight").values()))
            i[1].to_csv(csvfile, mode="a")

    # print([type(i[1]) for i in listOfTables])
    # pprint.pprint(listOfTables)
    # for i in listOfTables:
    #     plt.plot(i[1])
    #     plt.ylabel("frequency of form usage")
    #     plt.xlabel("step")
    #     plt.legend()
    #     plt.show()
    return(sharedVocabPerCents)
    # this is where i should calcualte the differences between each langauge pair and assign it to a list variable.
    # this is then returned as the individualLexicalDifference


def fitness_function(individual, weight, steps, lossLimit, networkSpecifier, languageList, communityList, fitnessComparisonList):
    # this function needs to call the simulation, building it with the specified community network edges parameters (the genes),
    model = None
    model = mdl.build_model(individual, weight, networkSpecifier, languageList, communityList)
    # builds the model to have the appropriate genes asigned to where they are meant to be
    # print((model.mode, model.monitoring))

    # and store the lexical difference from the simulation in a list
    # call the simulation and it should return a list of lexical differences based on the calculation to this variable (type list)
    individualLexicalDifference = run_model(model, steps, lossLimit)  # call the simulation to run.

    for lexical_diff in individualLexicalDifference:
        # get the difference between the measures of lexical difference (calculated and pre-determined)
        differenceList = [round(diff(x), 2) for x in zip(fitnessComparisonList, individualLexicalDifference)]
        absDifference = [round(abs(x), 2) for x in differenceList]
        closenessToZero = round(sum(absDifference), 2)
        return(invert(closenessToZero))


def selection(listOfIndividuals, numberToSelect):
    # this takes a list of (individual, fitness) tuples
    # uses a roulette wheel selection, where fitter individuals are more likely to be selected
    probabilityOfSelection = [i[1] for i in listOfIndividuals]
    norm = 1 / math.fsum(probabilityOfSelection)
    normProbOfSelection = [norm * i for i in probabilityOfSelection]
    chromosomeList = [i[0] for i in listOfIndividuals]
    # if(numberToSelect % 2 == 0 and numberToSelect < len(listOfIndividuals) / 2)
    chosenListIndices = numpy.random.choice(len(chromosomeList), size=4, replace=False, p=normProbOfSelection)
    chosenList = [chromosomeList[i] for i in chosenListIndices]

    # pair individuals
    random.shuffle(chosenList)
    list1 = chosenList[:int(len(chosenList) / 2)]  # first half of list
    list2 = chosenList[int(len(chosenList) / 2):]  # second half of list
    pairTuples = list(zip(list1, list2))

    return(pairTuples)


def crossover(pairTuples):
    lengthOfChromosome = len(pairTuples[0][0])
    listOfOffspring = []
    for pair in pairTuples:
        # define the parent individuals
        mAlpha = pair[0]
        dAlpha = pair[1]
        # choose how many genes will be crossed, less likely to cross more genes.
        lstChoices = [i + 1 for i in range(lengthOfChromosome)]
        numberOfCrossedGenes = random.choices(lstChoices, lstChoices.reverse(), k=1)
        numberOfCrossedGenes = numberOfCrossedGenes[0]

        # generate x random numbers between 1 and lenghtofchromosome-1. no redraws
        # where x is the prviously calculated number of crossed genes.
        sampledGenes = random.sample(range(lengthOfChromosome), k=numberOfCrossedGenes)
        offspring1 = []
        offspring2 = []
        # generate a list of beta values to modify the crossover genes
        betas = [round(random.uniform(0, 1), 2) for i in range(numberOfCrossedGenes)]
        index = 0
        betaIndex = 0
        # build the two offsrping chromosomes
        for i in range(lengthOfChromosome):
            if(index in sampledGenes):
                # p_{new1} = p_{m\alpha} - \beta[p_{m\alpha} - p_{d\alpha}]
                pNew1 = mAlpha[index] - (betas[betaIndex] * (mAlpha[index] - dAlpha[index]))
                offspring1.append(round(pNew1, 3))
                # p_{new2} = p_{d\alpha} + \beta[p_{m\alpha} - p_{d\alpha}]
                pNew2 = dAlpha[index] + (betas[betaIndex] * (mAlpha[index] - dAlpha[index]))
                offspring2.append(round(pNew2, 3))
                betaIndex += 1
            else:
                offspring1.append(mAlpha[index])
                offspring2.append(dAlpha[index])

            index += 1

        listOfOffspring.append(offspring1)
        listOfOffspring.append(offspring2)
    return(listOfOffspring)


def mutate(listOfOffspring):
    listOfMutants = []
    for individual in listOfOffspring:
        # chose at most a quarter of genes to mutate.
        mutationIndicies = random.sample(range(len(individual)), k=int(len(individual) / 4))
        index = 0
        mutatedIndividual = []
        for gene in individual:
            if(index in mutationIndicies):
                mutatedIndividual.append(round(random.uniform(0, 1), 2))
            else:
                mutatedIndividual.append(individual[index])
            index += 1

        listOfMutants.append(mutatedIndividual)

    return(listOfMutants)

# after this I need to add my mutants and the successful reproducers back into the pool to run the simulation again. Huzzah


def run_sim(listOfIndividuals, weight, steps, lossLimit, networkSpecifier, fitnessComparisonList):
    # this function takes a list of individuals (chromosomes) and runs the simulation over each one.
    fitList = []
    for individual in listOfIndividuals:
        # create languages (from mdl.Language class)
        # ensure the languages exist.
        languageList = lac.build_languageList()

        # make a list of the languages to give to the model.
        # define the communities to which agent's can belong.
        communityList = lac.build_communitiesList(languageList)

        fitness = fitness_function(individual, weight, steps, lossLimit, networkSpecifier, languageList, communityList, fitnessComparisonList)
        fitList.append((individual, fitness))
        print("Simulation Done! Mode: {}, Monitoring: {}, Weight: {}".format(individual[0], individual[1], weight))

        # languageList = None
        # communityList = Non

    return(fitList)


def main(populationList, generations, weight, steps, lossLimit, networkSpecifier, fitnessComparisonList):
    # to run the program without the genetic algorithm component, just set the generations variable to 1
    # networkSpecifier indicates which network the simulations should be building.
    for i in range(generations):
        # this determines which language they speak natively.
        # run the simulation to get the fitness levels of each chromosome
        assessedIndividuals = run_sim(populationList, weight, steps, lossLimit, networkSpecifier, fitnessComparisonList)

        # pprint.pprint(assessedIndividuals)
        # select some individuals primarily based on fitness, and pair them for reproduction
        pairTuples = selection(assessedIndividuals, 4)
        # generate offspring with a number of genes crossed over from each parent
        offspringList = crossover(pairTuples)
        # add mutations into the chromosomes to stimulate genetic diversity.
        mutants = mutate(offspringList)
        # add the children to the population along with their parents to try again
        # as well as 2 randomly defined individuals to increase genetic diversity further
        randomIndividual1, randomIndividual2 = [round(random.uniform(0, 1), 2) for i in range(2)], [round(random.uniform(0, 1), 2) for i in range(2)]
        parents1 = [i[0] for i in pairTuples]
        parents2 = [i[1] for i in pairTuples]
        populationList.clear()
        populationList = [i for i in mutants]
        populationList.append(randomIndividual1)
        populationList.append(randomIndividual2)
        populationList.extend(parents1)
        populationList.extend(parents2)

        # need a way to optimise this a bit. avoid recalculating the fitness of the parent generation (reduces the number of sims to run by 4 per generation.

# this is where I make the genetic algo do its thing
# initialise a population of individuals/chromosomes (7 genes)


populationList = [[round(random.uniform(0, 1), 2) for i in range(2)],
                  [round(random.uniform(0, 1), 2) for i in range(2)],
                  [round(random.uniform(0, 1), 2) for i in range(2)],
                  [round(random.uniform(0, 1), 2) for i in range(2)],
                  [round(random.uniform(0, 1), 2) for i in range(2)],
                  [round(random.uniform(0, 1), 2) for i in range(2)],
                  [round(random.uniform(0, 1), 2) for i in range(2)],
                  [round(random.uniform(0, 1), 2) for i in range(2)],
                  [round(random.uniform(0, 1), 2) for i in range(2)],
                  [round(random.uniform(0, 1), 2) for i in range(2)]]

# maintain an initial previous population that is different from the initialised population
previousPopulation = [[round(random.uniform(0, 1), 2) for i in range(2)],
                      [round(random.uniform(0, 1), 2) for i in range(2)],
                      [round(random.uniform(0, 1), 2) for i in range(2)],
                      [round(random.uniform(0, 1), 2) for i in range(2)],
                      [round(random.uniform(0, 1), 2) for i in range(2)],
                      [round(random.uniform(0, 1), 2) for i in range(2)],
                      [round(random.uniform(0, 1), 2) for i in range(2)],
                      [round(random.uniform(0, 1), 2) for i in range(2)],
                      [round(random.uniform(0, 1), 2) for i in range(2)],
                      [round(random.uniform(0, 1), 2) for i in range(2)]]


customPopulation = [[0.54, 1.00], [0.01, 0.99], [0.99, 0.01], [0.01, 0.01], [0.99, 0.99], [0.5, 0.5], [0.25, 0.75], [0.75, 0.25], [0.33, 0.66], [0.66, 0.33]]

effectOfMonitoring = [[0.54, 0.0], [0.54, 0.1], [0.54, 0.2], [0.54, 0.3], [0.54, 0.4], [0.54, 0.5], [0.54, 0.6], [0.54, 0.7], [0.54, 0.8], [0.54, 0.9], [0.54, 1.0]]
effectOfMode = [[0.0, 1.0], [0.1, 1.0], [0.2, 1.0], [0.3, 1.0], [0.4, 1.0], [0.5, 1.0], [0.6, 1.0], [0.7, 1.0], [0.8, 1.0], [0.9, 1.0], [1.0, 1.0]]
test = [[0.9, 0.99999], [0.91, 0.99999], [0.92, 0.99999], [0.93, 0.99999], [0.94, 0.99999], [0.95, 0.99999], [0.96, 0.99999], [0.97, 0.99999], [0.98, 0.99999], [0.99, 0.99999], [0.99999, 0.99999]]
internalSquare = [[0.25, 0.25], [0.25, 0.75], [0.75, 0.25], [0.75, 0.75]]

fullGraph = [[0.54, 1.0], [0.54, 0.0], [0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
slides = [[0.54, 1.0]]
weightDictList = [{('19', '18'): 0.5, ('18', '19'): 1.0}]
# index = 6
for i in weightDictList:  # [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 1.0]:
    main(slides, 1, i, 35, 1.0, "10b", [0.5])
    # print("Completed Network Weight = {} ({} simulations of 66)".format(i, index))
    # index += 6
    # customPopulation = [[0.54, 1.00], [0.01, 0.99], [0.99, 0.01], [0.01, 0.01], [0.99, 0.99], [0.5, 0.5], [0.25, 0.75], [0.75, 0.25], [0.33, 0.66], [0.66, 0.33]]
    # effectOfMonitoring = [[0.54, 0.0], [0.54, 0.1], [0.54, 0.2], [0.54, 0.3], [0.54, 0.4], [0.54, 0.5], [0.54, 0.6], [0.54, 0.7], [0.54, 0.8], [0.54, 0.9], [0.54, 1.0]]
    # effectOfMode = [[0.0, 1.0], [0.1, 1.0], [0.2, 1.0], [0.3, 1.0], [0.4, 1.0], [0.5, 1.0], [0.6, 1.0], [0.7, 1.0], [0.8, 1.0], [0.9, 1.0], [1.0, 1.0]]
    # test = [[0.9, 0.99999], [0.91, 0.99999], [0.92, 0.99999], [0.93, 0.99999], [0.94, 0.99999], [0.95, 0.99999], [0.96, 0.99999], [0.97, 0.99999], [0.98, 0.99999], [0.99, 0.99999], [0.99999, 0.99999]]
    # internalSquare = [[0.25, 0.25], [0.25, 0.75], [0.75, 0.25], [0.75, 0.75]]
    # fullGraph = [[0.54, 1.0], [0.54, 0.0], [0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
    slides = [[0.54, 1.0]]
# main([[0.54, 0.84]], 1, 0.5, 35, 1.0, "10b", [0.5])
