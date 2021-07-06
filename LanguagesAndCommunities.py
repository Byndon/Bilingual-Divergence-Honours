import csv

kulinDict = {}
yuinDict = {}
lowMurrayDict = {}
vicDict = {}
listOfDicts = [kulinDict, yuinDict, lowMurrayDict, vicDict]


def defineLists():
    KulinLanguages = ["Woiwurrung", "Boonwurrung", "Daungwurrung", "Wathawurrung", "Djabwurrung", "Djadjawurrung", "Wemba Wemba", "Baraba Baraba", "Nari Nari", "Madhi Madhi", "Wadi-wadi", "Yari Yari", "Ladji-Ladji", "Wotjobaluk", "Jardwadjali", "Kolakngat", "Warrnambool", "Buwandik", "Djadjala", "Werkaya", "Tjapwurrung"]
    YuinLanguages = ["Thawa", "Ngarigu", "Gundungurra", "Moneroo"]
    LowerMurrayLanguages = ["Ngarrindjeri", "Ngarkat", "Ngintait", "Keramin", "Yitha-Yitha"]
    VictorianOtherLanguages = ["Muk-Thang", "Thangguai", "Bidhawal", "Dhudhuroa", "Nulit", "Pallanganmiddang", "Kurnai", "Yorta-Yorta", "Yabula-Yabula"]
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
    
    # alternatesDict = {"Wotjobaluk": ["Werkaya", "Djadjala", "Buibadjal", "Weregadjal"], "Woiwurrung": ["Woiwurrung"],
    #                   "Daungwurrung": ["Thagungwurrung"], "Wadi-Wadi": ["Piangil"], "Keramin": ["Kureinji", "Paakantyi"],
    #                   "Ngarigu": ["Jaitmatang", "Gundungerre", "Yaithmathang", "Gundungurra", "Ngarigo"],
    #                   "Pallanganmiddang": ["Waywurru", "Waveroo", "Kwart-Kwart", "Mogullumbidj"], "Ngarkat": ["Yuyu", "Ngintait"]}
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


def main(csvfile, listOfLanguages):
    openfile(csvfile, listOfLanguages)
    [normaliseDict(i) for i in listOfDicts]
    return(defineLists)


KulinLanguages, YuinLanguages, LowerMurrayLanguages, VictorianOtherLanguages = defineLists()
main("Vicdata_minimal_.csv", [KulinLanguages, YuinLanguages, LowerMurrayLanguages, VictorianOtherLanguages])
