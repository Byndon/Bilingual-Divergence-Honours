import csv
import model as mdl

kulinDict = {}
yuinDict = {}
lowMurrayDict = {}
vicDict = {}
listOfDicts = [kulinDict, yuinDict, lowMurrayDict, vicDict]


def defineLists():
    KulinLanguages = ["Woiwurrung", "Boonwurrung", "Daungwurrung", "Wathawurrung", "Djabwurrung", "Djadjawurrung", "Wemba Wemba", "Baraba Baraba", "Nari Nari", "Madhi Madhi", "Wadi Wadi", "Yari Yari", "Ladji Ladji", "Wotjobaluk", "Jardwadjali", "Kolakngat", "Warrnambool", "Buwandik", "Djadjala", "Werkaya", "Tjapwurrung"]
    YuinLanguages = ["Thawa", "Ngarigu", "Gundungurra", "Moneroo"]
    LowerMurrayLanguages = ["Ngarrindjeri", "Ngarkat", "Ngintait", "Keramin", "Yitha Yitha"]
    VictorianOtherLanguages = ["Muk-Thang", "Thangguai", "Bidhawal", "Dhudhuroa", "Nulit", "Pallanganmiddang", "Kurnai", "Yorta Yorta", "Yabula Yabula"]
    return((KulinLanguages, YuinLanguages, LowerMurrayLanguages, VictorianOtherLanguages))


def openfile(filename, listOfLanguages):
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            makeDicts(row, listOfDicts, listOfLanguages)


def makeDicts(line, listOfDicts, listOfLanguages):
    KulinLanguages, YuinLanguages, LowerMurrayLanguages, VictorianOtherLanguages = listOfLanguages
    # have a dictionary of form meaning dictionaries to apply to languages
    # possible of 4 dictionaries, ans each is seeded with a language dictionary dependant on it's grouping by Bowern
    # takes a row (csv in a list)
    # decides whether to consider the row (non-nominals are not considered)
    # determines which dictionary it goes into:
    # adds the meaning and form to the dictionary (meaning key, list of form values), assuming the form isn't blank or already in the dictionary list.
    if((line[5].lower().strip() == "n") or (line[5].lower().strip() == "adj")):
        if(line[1] in KulinLanguages):
            if(line[3].lower().strip() in listOfDicts[0].keys()):
                if(line[2].lower().strip() not in listOfDicts[0][line[3].lower().strip()] and line[2].lower().strip() and not line[2].lower().strip().isspace()):
                    listOfDicts[0][line[3].lower().strip()].append(line[2].lower().strip())
            else:
                listOfDicts[0][line[3].lower().strip()] = [line[2].lower().strip()]
        if(line[1] in YuinLanguages):
            if(line[3].lower().strip() in listOfDicts[1].keys()):
                if(line[2].lower().strip() not in listOfDicts[1][line[3].lower().strip()] and line[2].lower().strip() and not line[2].lower().strip().isspace()):
                    listOfDicts[1][line[3].lower().strip()].append(line[2].lower().strip())
            else:
                listOfDicts[1][line[3].lower().strip()] = [line[2].lower().strip()]
        if(line[1] in LowerMurrayLanguages):
            if(line[3].lower().strip() in listOfDicts[2].keys()):
                if(line[2].lower().strip() not in listOfDicts[2][line[3].lower().strip()] and line[2].lower().strip() and not line[2].lower().strip().isspace()):
                    listOfDicts[2][line[3].lower().strip()].append(line[2].lower().strip())
            else:
                listOfDicts[2][line[3].lower().strip()] = [line[2].lower().strip()]
        if(line[1] in VictorianOtherLanguages):
            if(line[3].lower().strip() in listOfDicts[3].keys()):
                if(line[2].lower().strip() not in listOfDicts[3][line[3].lower().strip()] and line[2].lower().strip() and not line[2].lower().strip().isspace()):
                    listOfDicts[3][line[3].lower().strip()].append(line[2].lower().strip())
            else:
                listOfDicts[3][line[3].lower().strip()] = [line[2].lower().strip()]


def normaliseDict(formMeaningDictionary):
    for meaning in formMeaningDictionary:
        formMeaningDictionary[meaning] = [i.replace("\\", "").replace("?", "") for i in formMeaningDictionary[meaning]]


def build_languageList():
    language1 = None
    language2 = None
    language3 = None
    language4 = None
    language5 = None
    language6 = None
    language7 = None
    language8 = None
    language9 = None
    language10 = None
    language11 = None
    language12 = None
    language13 = None
    language14 = None
    language15 = None
    language16 = None
    language17 = None
    language18 = None
    language19 = None
    language20 = None
    language21 = None
    language22 = None
    language23 = None
    language24 = None
    language25 = None
    language26 = None
    language27 = None
    language28 = None
    language29 = None
    language30 = None
    language31 = None
    language32 = None
    language33 = None
    language34 = None

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
    language24 = mdl.Language("Yari Yari")
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

    languageList = [language1, language2, language3, language4, language5, language6, language7, language8, language9, language10, language11, language12, language13, language14, language15, language16, language17, language18, language19, language20, language21, language22, language23, language24, language25, language26, language27, language28, language29, language30, language31, language32, language33, language34]
    return(languageList)


def build_communitiesList(languageList):
    community1 = None
    community2 = None
    community3 = None
    community4 = None
    community5 = None
    community6 = None
    community7 = None
    community8 = None
    community9 = None
    community10 = None
    community11 = None
    community12 = None
    community13 = None
    community14 = None
    community15 = None
    community16 = None
    community17 = None
    community18 = None
    community19 = None
    community20 = None
    community21 = None
    community22 = None
    community23 = None
    community24 = None
    community25 = None
    community26 = None
    community27 = None
    community28 = None
    community29 = None
    community30 = None
    community31 = None
    community32 = None
    community33 = None
    community34 = None
    
    community1 = mdl.Community(languageList[0].languageName, languageList[0], 50)
    community2 = mdl.Community(languageList[1].languageName, languageList[1], 50)
    community3 = mdl.Community(languageList[2].languageName, languageList[2], 50)
    community4 = mdl.Community(languageList[3].languageName, languageList[3], 50)
    community5 = mdl.Community(languageList[4].languageName, languageList[4], 50)
    community6 = mdl.Community(languageList[5].languageName, languageList[5], 50)
    community7 = mdl.Community(languageList[6].languageName, languageList[6], 50)
    community8 = mdl.Community(languageList[7].languageName, languageList[7], 50)
    community9 = mdl.Community(languageList[8].languageName, languageList[8], 50)
    community10 = mdl.Community(languageList[9].languageName, languageList[9], 50)
    community11 = mdl.Community(languageList[10].languageName, languageList[10], 50)
    community12 = mdl.Community(languageList[11].languageName, languageList[11], 50)
    community13 = mdl.Community(languageList[12].languageName, languageList[12], 50)
    community14 = mdl.Community(languageList[13].languageName, languageList[13], 50)
    community15 = mdl.Community(languageList[14].languageName, languageList[14], 50)
    community16 = mdl.Community(languageList[15].languageName, languageList[15], 50)
    community17 = mdl.Community(languageList[16].languageName, languageList[16], 50)
    community18 = mdl.Community(languageList[17].languageName, languageList[17], 50)
    community19 = mdl.Community(languageList[18].languageName, languageList[18], 50)
    community20 = mdl.Community(languageList[19].languageName, languageList[19], 50)
    community21 = mdl.Community(languageList[20].languageName, languageList[20], 50)
    community22 = mdl.Community(languageList[21].languageName, languageList[21], 50)
    community23 = mdl.Community(languageList[22].languageName, languageList[22], 50)
    community24 = mdl.Community(languageList[23].languageName, languageList[23], 50)
    community25 = mdl.Community(languageList[24].languageName, languageList[24], 50)
    community26 = mdl.Community(languageList[25].languageName, languageList[25], 50)
    community27 = mdl.Community(languageList[26].languageName, languageList[26], 50)
    community28 = mdl.Community(languageList[27].languageName, languageList[27], 50)
    community29 = mdl.Community(languageList[28].languageName, languageList[28], 50)
    community30 = mdl.Community(languageList[29].languageName, languageList[29], 50)
    community31 = mdl.Community(languageList[30].languageName, languageList[30], 50)
    community32 = mdl.Community(languageList[31].languageName, languageList[31], 50)
    community33 = mdl.Community(languageList[32].languageName, languageList[32], 50)
    community34 = mdl.Community(languageList[33].languageName, languageList[33], 50)

    communityList = [community1, community2, community3, community4, community5, community6, community7, community8, community9, community10, community11, community12, community13, community14, community15, community16, community17, community18, community19, community20, community21, community22, community23, community24, community25, community26, community27, community28, community29, community30, community31, community32, community33, community34]

    return(communityList)


def main(csvfile, listOfLanguages):
    openfile(csvfile, listOfLanguages)
    [normaliseDict(i) for i in listOfDicts]
    return(defineLists)


KulinLanguages, YuinLanguages, LowerMurrayLanguages, VictorianOtherLanguages = defineLists()
main("Vicdata_minimal_possum.csv", [KulinLanguages, YuinLanguages, LowerMurrayLanguages, VictorianOtherLanguages])
