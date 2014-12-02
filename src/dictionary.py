from itertools import groupby
import analysis
import time
import random


class DictLookup:
    def __init__(self):
        self.dictWords = []
        self.firstLetterWords = {}
        print "opening"
        with open('words', 'r') as f:
            self.dictWords = f.readlines()
            self.dictWords = list(set(self.dictWords))
            self.dictWords = [x[:-1].upper() for \
                              x in self.dictWords if len(x) >= 3]

            for firstLetter, group in groupby(sorted(self.dictWords), \
                                               key=lambda x: x[0]):
                self.firstLetterWords[firstLetter] = list(group)

    def GetMatches(self, letters):
        matchList = []
        if len(letters) == 0:
            return []

        for word in self.firstLetterWords.get(letters[0], []):
            if analysis.IsSubstring(analysis.Contract(word), letters)[0]:
                matchList.append(word)
        return matchList


def main():
    d = DictLookup()
    n = len(d.dictWords) - 1
    print d.GetMatches("morgue".upper())
    return
    for _ in range(100):
        k = random.randint(0, n)
        print d.dictWords[k]
        print d.GetMatches(d.dictWords[k])
        print "\n--\n"

if __name__ == "__main__":
    main()
