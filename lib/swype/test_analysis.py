import numpy as np
from analysis import IsSubstring
from analysis import Contract
from analysis import Normalize
from mouseTracker import QwertyOrd
from dictionary import DictLookup

def testIsSubstring():
    assert IsSubstring('a','a') == (True, [0])
    assert IsSubstring('cat', 'catabc') == (True, [0,1,2])
    assert IsSubstring('dog', 'daoagc') == (True, [0,2,4])
    assert IsSubstring('ba', 'ab')[0] == False

def testContract():
    assert Contract('aaaabbcbbbeffffaa') == 'abcbefa'
    assert Contract('abbcbbbeffffaa') == 'abcbefa'
    assert Contract('abbcbbbeffffa') == 'abcbefa'
    assert Contract('a') == 'a'
    assert Contract('aa') == 'a'

def testQwertyOrd():
    assert QwertyOrd('q') == 0
    assert QwertyOrd('a') == 10
    assert QwertyOrd(';') == 26

def testGetMatches():
    myDict = DictLookup()
    assert isinstance(myDict.GetMatches('aatoeust') , list)
    assert isinstance(myDict.GetMatches('') , list)

def testNormalize():
    assert all(Normalize(np.zeros(3)) - np.zeros(3) == 0.0)
    assert all(Normalize(np.zeros(1)) - np.zeros(1) == 0.0)
    assert all(Normalize(np.ones(3)) - np.ones(3) / np.linalg.norm(np.ones(3)) == 0.0)
    
