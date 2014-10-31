import datetime
import os
import os.path
import pickle
import pdb
import numpy as np
import dictionary
import mouseTracker
from mouseTracker import *
from itertools import groupby
from operator import attrgetter

class FeatureSet:
    def __init__(self):
        self.totalTimeSpent = 0
        self.letter = ''
        self.directionInDotOut = 0
        self.usedInWord = False
    
def GetFiles(directory):
    directoryList = []
    for root, _, files in os.walk(directory):
        for f in files:
            # print str(f)
            fullpath = os.path.join(root, f)
            directoryList.append(fullpath)
    return directoryList

def Normalize(x):
    return x/np.linalg.norm(x) if np.linalg.norm(x) > 0 else x

def GetTrajectories(directory):
    for f in GetFiles(directory):
        yield pickle.load(open(f, 'r'))

def Contract(string):
    return ''.join([k for k, _ in groupby(string)])

def IsSubstring(small, big, n=0, L=[]):
    if small == "":
        return (True, L)
    elif big == "":
        return (False, L)
    elif small[0] == big[0]:
        return IsSubstring(small[1:], big[1:], n+1, L + [n])
    else:
        return IsSubstring(small, big[1:], n+1, L)
        
def AnalyzeTrajectory(trajectory):
    "Debug function to look at some basic data for each recorded trajectory"
    letters = trajectory.GetLetterSequence()
    substringWorked, _ = IsSubstring(Contract(trajectory.word), Contract(''.join(letters)))
    print trajectory.word
    print Contract(letters)
    myDict = dictionary.DictLookup()
    wordRankings = []
    for word in myDict.GetMatches(Contract(letters)):
        letterData = CollectTrajectoryData(trajectory, Contract(word))
        goodData = filter(lambda x: x.usedInWord, letterData)
        badData =  filter(lambda x: not x.usedInWord, letterData)
        wordRank = [word, []]
        goodDataTime = np.mean(map(attrgetter('totalTimeSpent'), goodData))
        badDataTime = np.mean(map(attrgetter('totalTimeSpent'), badData))
        goodDataAngle = np.mean(map(attrgetter('directionInDotOut'), goodData))
        badDataAngle = np.mean(map(attrgetter('directionInDotOut'), badData))
        score = goodDataTime * 1 + badDataTime * - 1 + goodDataAngle * -2 + badDataAngle * 1 + len(Contract(word)) * (1/3.0)
        wordRank[1] = [goodDataTime, badDataTime, goodDataAngle, badDataAngle, score]
        wordRankings.append(wordRank)

    for wordRank in sorted(wordRankings, key=lambda x: -(x[1][-1]))[:10]:
        print 'wordRank', wordRank

        
    # pdb.set_trace()
    

def LogData(trajectory, startIndex, endIndex):
    features = FeatureSet()
    totalTimeSpent = (trajectory._frameDataList[endIndex-1].time -
                     trajectory._frameDataList[startIndex].time).total_seconds()
    assert totalTimeSpent >= 0
    letter = trajectory._frameDataList[startIndex].closestLetter
    for frameNum in range(startIndex, endIndex):
        pass

    if endIndex - startIndex >= 3:
        frameList = [startIndex, startIndex + 1, endIndex -2, endIndex -1]
        positions = [trajectory._frameDataList[it].position for it in frameList]
        directionIn = Normalize(positions[1] - positions[0])
        directionOut = Normalize(positions[3] - positions[2])
        features.directionInDotOut = np.dot(directionIn, directionOut)

    features.totalTimeSpent = totalTimeSpent
    features.letter = letter
    return features
        
        
def CollectTrajectoryData(trajectory, word=None):
    "Get a set of features to score a substring against the Trajectory"

    if word == None:
        word = trajectory.word

    letters = trajectory.GetLetterSequence()
    substringWorked, usedIndices = IsSubstring(Contract(word), Contract(letters))
    if not substringWorked:
        return None

    trajectoryFeatures = []
    elementCounter = 0
    for groupCounter, (key, values) in enumerate(groupby(letters)):
        numValues = len(list(values))
        newFeatureSet = LogData(trajectory,
                                 elementCounter,
                                 elementCounter + numValues)
        if groupCounter in usedIndices:
            newFeatureSet.usedInWord = True
        else:
            newFeatureSet.usedInWord = False
        trajectoryFeatures.append(newFeatureSet)
        elementCounter += numValues
    return trajectoryFeatures
        
def main():
    trajectoryList = GetTrajectories("/home/russell/git/src/python/swype/training/")
    print "Starting new trajectory run"
    allGoodData = []
    allBadData = []
    for trajectory in trajectoryList:
        AnalyzeTrajectory(trajectory)
        # letterData = CollectTrajectoryData(trajectory)

    #     allGoodData += filter(lambda x: x.usedInWord, letterData)
    #     allBadData +=  filter(lambda x: not x.usedInWord, letterData)
    # fig = plt.figure()
    # ax1 = fig.add_subplot(111)
    # # x0 = [x.totalTimeSpent for x in allGoodData]
    # # x1 = [x.totalTimeSpent for x in allBadData]
    # x0 = [mouseTracker.QwertyOrd(x.letter) for x in allGoodData]
    # x1 = [mouseTracker.QwertyOrd(x.letter) for x in allBadData]
    # ax1.hist([x0, x1], 20)
    # # ax1 = fig.add_subplot(211)
    # # ax2 = fig.add_subplot(212)
    # # ax1.hist([x.totalTimeSpent for x in allGoodData], 20)
    # # ax2.hist([x.totalTimeSpent for x in allBadData], 20)
    # # ax1.hist([mouseTracker.QwertyOrd(x.letter) for x in allGoodData], 20)
    # # ax2.hist([mouseTracker.QwertyOrd(x.letter) for x in allBadData], 20)
    # # ax1.hist([x.directionInDotOut for x in allGoodData], 20)
    # # ax2.hist([x.directionInDotOut for x in allBadData], 20)
    # # ax1.set_title('Good Data')
    # # ax2.set_title('Bad Data')
    # # plt.show()

if (__name__ == '__main__'):
    main()
