import pdb
from itertools import groupby
import analysis

class DictLookup:
    def __init__(self):
        self.dictWords = []
        self.firstLetterWords = {}
        with open('words', 'r') as f:
            self.dictWords = f.readlines()
            self.dictWords = list(set(self.dictWords))
            self.dictWords = [x[:-1].lower() for x in self.dictWords if len(x) >= 4]
            for firstLetter, group in groupby(sorted(self.dictWords), key=lambda x: x[0]):
                self.firstLetterWords[firstLetter] = list(group)


    def GetMatches(self, letters):
        matchList = []
        if len(letters) == 0: return []
        for word in self.firstLetterWords.get(letters[0], []):
            if analysis.IsSubstring(analysis.Contract(word), letters)[0]:
                matchList.append(word)
        return matchList

def main():
    myDict = DictLookup()
    print myDict.GetMatches('ziptat.c,auhlcehot')

if (__name__ == '__main__'):
    main()

