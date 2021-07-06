import model as mdl
import random
import numpy
import math
import csv
# import pprint
# import matplotlib.pyplot as plt

random.seed(12345)


def diff(x_list):
    return(x_list[0] - x_list[1])


def invert(x):
    return(100 - x)


def run_model(model, steps, lossLimit):
    stepCounter = 0
    for i in range(steps):
        model.step()
        if(stepCounter % 5 == 0):
            for language in model.languages:
                language.lose_form(lossLimit)
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
            writer.writerow(("Chromosome", i[2].speakers[0].mode, i[2].speakers[0].monitoring))
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
    model = mdl.build_model(individual, weight, networkSpecifier, languageList, communityList)  # builds the model to have the appropriate genes asigned to where they are meant to be

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
    list1 = chosenList[:int(len(chosenList)/2)]  # first half of list
    list2 = chosenList[int(len(chosenList)/2):]  # second half of list
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
        lstChoices = [i+1 for i in range(lengthOfChromosome)]
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


def run_sim(listOfIndividuals, weight, steps, lossLimit, networkSpecifier, languageList, communityList, fitnessComparisonList):
    # this function takes a list of individuals (chromosomes) and runs the simulation over each one.
    fitList = []
    for individual in listOfIndividuals:
        fitness = fitness_function(individual, weight, steps, lossLimit, networkSpecifier, languageList, communityList, fitnessComparisonList)
        fitList.append((individual, fitness))

    return(fitList)


def main(populationList, generations, weight, steps, lossLimit, networkSpecifier, languageList, communityList, fitnessComparisonList):
    # to run the program without the genetic algorithm component, just set the generations variable to 1
    # networkSpecifier indicates which network the simulations should be building.
    for i in range(generations):
        # run the simulation to get the fitness levels of each chromosome
        assessedIndividuals = run_sim(populationList, weight, steps, lossLimit, networkSpecifier, languageList, communityList, fitnessComparisonList)

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

# create languages (from mdl.Language class)
# ensure the languages exist.
language1 = mdl.Language("Ngarigu")
language2 = mdl.Language("Thawa")
language3 = mdl.Language("Bidhawal")
language4 = mdl.Language("Thangguai")
language5 = mdl.Language("Muk-Thang")
language6 = mdl.Language("Dhudhuroa")
language7 = mdl.Language("Nulit")
language8 = mdl.Language("Pallanganmiddang")
language9 = mdl.Language("Kurnai")
language10 = mdl.Language("Yorta Yorta")
language11 = mdl.Language("Yabula Yabula")
language12 = mdl.Language("Woiwurrung")
language13 = mdl.Language("Boonwurrung")
language14 = mdl.Language("Daungwurrung")
language15 = mdl.Language("Wathawurrung")
language16 = mdl.Language("Djabwurrung")
language17 = mdl.Language("Djadjala")
language18 = mdl.Language("Wemba Wemba")
language19 = mdl.Language("Baraba Baraba")
language20 = mdl.Language("Nari Nari")
language21 = mdl.Language("Madhi Madhi")
language22 = mdl.Language("Yitha Yitha")
language23 = mdl.Language("Wadi Wadi")
language24 = mdl.Language("yari Yari")
language25 = mdl.Language("Keramin")
language26 = mdl.Language("Ladji Ladji")
language27 = mdl.Language("Ngintait")
language28 = mdl.Language("Wotjobaluk")
language29 = mdl.Language("Jardwadjali")
language30 = mdl.Language("Kolakngat")
language31 = mdl.Language("Warrnambool")
language32 = mdl.Language("Buwandik")
language33 = mdl.Language("Ngarkat")
language34 = mdl.Language("Ngarrindjeri")

# make a list of the languages to give to the model.
languageList = [language1, language2, language3, language4, language5, language6, language7, language8, language9, language10, language11, language12, language13, language14, language15, language16, language17, language18, language19, language20, language21, language22, language23, language24, language25, language26, language27, language28, language29, language30, language31, language32, language33, language34]


# define the communities to which agent's can belong.
# this determines which language they speak natively.
community1 = mdl.Community(language1.languageName, language1, 10)
community2 = mdl.Community(language2.languageName, language1, 10)
community3 = mdl.Community(language3.languageName, language3, 10)
community4 = mdl.Community(language4.languageName, language4, 10)
community5 = mdl.Community(language5.languageName, language5, 10)
community6 = mdl.Community(language6.languageName, language6, 10)
community7 = mdl.Community(language7.languageName, language7, 10)
community8 = mdl.Community(language8.languageName, language8, 10)
community9 = mdl.Community(language9.languageName, language9, 10)
community10 = mdl.Community(language10.languageName, language10, 10)
community11 = mdl.Community(language11.languageName, language11, 10)
community12 = mdl.Community(language12.languageName, language12, 10)
community13 = mdl.Community(language13.languageName, language13, 10)
community14 = mdl.Community(language14.languageName, language14, 10)
community15 = mdl.Community(language15.languageName, language15, 10)
community16 = mdl.Community(language16.languageName, language16, 10)
community17 = mdl.Community(language17.languageName, language17, 10)
community18 = mdl.Community(language18.languageName, language18, 10)
community19 = mdl.Community(language19.languageName, language19, 10)
community20 = mdl.Community(language20.languageName, language20, 10)
community21 = mdl.Community(language21.languageName, language21, 10)
community22 = mdl.Community(language22.languageName, language22, 10)
community23 = mdl.Community(language23.languageName, language23, 10)
community24 = mdl.Community(language24.languageName, language24, 10)
community25 = mdl.Community(language25.languageName, language25, 10)
community26 = mdl.Community(language26.languageName, language26, 10)
community27 = mdl.Community(language27.languageName, language27, 10)
community28 = mdl.Community(language28.languageName, language28, 10)
community29 = mdl.Community(language29.languageName, language29, 10)
community30 = mdl.Community(language30.languageName, language30, 10)
community31 = mdl.Community(language31.languageName, language31, 10)
community32 = mdl.Community(language32.languageName, language32, 10)
community33 = mdl.Community(language33.languageName, language33, 10)
community34 = mdl.Community(language34.languageName, language34, 10)

communityList = [community1, community2, community3, community4, community5, community6, community7, community8, community9, community10, community11, community12, community13, community14, community15, community16, community17, community18, community19, community20, community21, community22, community23, community24, community25, community26, community27, community28, community29, community30, community31, community32, community33, community34]


main(populationList, 1, 1, 35, 1.0, 1, languageList, communityList, [0.5])