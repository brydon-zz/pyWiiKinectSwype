# -*- coding: utf-8 -*-

import sys
import pygame.locals
import datetime
import numpy as np
import pickle
import analysis
import time
import random
import math

if len(sys.argv) > 1:
    partName = sys.argv[1]
else:
    partName = raw_input("Please enter participant number: ")

textmode = raw_input("Enter the mode (KB,KS,WB,WS): ")

logDir = "../logs/"

WII_SWYPE = 1
KIN_SWYPE = 2
WII_BASIC = 3
KIN_BASIC = 4

if textmode == "KB":
    mode = KIN_BASIC
elif textmode == "KS":
    mode = KIN_SWYPE
elif textmode == "WB":
    mode = WII_BASIC
elif textmode == "WS":
    mode = WII_SWYPE

phrasesFile = open("phrases", "r")
phrases = phrasesFile.read().upper().split("\r\n")
phraseEntryTimes = []
mouseLog = []
wordEntryTimes = []
totalWordsEntered = []

phrasesFile.close()
experimentStartTime = 0
experimentRunning = False
phrasesToEnter = []


NUM_PHRASES_PER_TRIAL = 5
openFileList = []
drawPath = False
backSpaceDrawn = False

PHRASERECT_L = 50
PHRASERECT_T = 50
PHRASERECT_HEIGHT = 25
PHRASERECT_WIDTH = 1000

INTEXTSIZE = 24
INPUTRECT_L = 50
INPUTRECT_T = 100
INPUTRECT_HEIGHT = 25
INPUTRECT_WIDTH = 1000

OTHERRECT_HEIGHT = 25
OTHERRECT_WIDTH = 100

OTHERRECT_L = [50, 200, 350]
OTHERRECT_T = 150

MOUSEBOXW = MOUSEBOXH = 100


KEYWIDTH = 100
KEYHEIGHT = 125

oldhi = hi = -1

BORDERWIDTH = 4
TEXTSIZE = 150

KEYSTARTY = 275
XOFFSET = KEYWIDTH / 2 + 100

SPACEBAR_TLX = XOFFSET + 2 * (KEYWIDTH + 2 * BORDERWIDTH)
SPACEBAR_TLY = 605

SPACEBAR_WIDTH = 5 * KEYWIDTH

KEYSRECT = pygame.Rect(XOFFSET - 0.5 * KEYWIDTH, KEYSTARTY - 0.5 * KEYHEIGHT, \
                10 * (KEYWIDTH + BORDERWIDTH), 3 * (KEYHEIGHT + BORDERWIDTH))

SPACEBARRECT = pygame.Rect(SPACEBAR_TLX, \
                     SPACEBAR_TLY, \
                     SPACEBAR_WIDTH + 2 * BORDERWIDTH, \
                     KEYHEIGHT + 2 * BORDERWIDTH)

suggestionRect = [pygame.Rect(OTHERRECT_L[i] - BORDERWIDTH, \
                                        OTHERRECT_T - BORDERWIDTH, \
                                        OTHERRECT_WIDTH + 2 * BORDERWIDTH, \
                                        OTHERRECT_HEIGHT + 2 * BORDERWIDTH)\
                  for i in range(3)]

# set up pygame
pygame.init()

# set up the window
windowSurface = pygame.display.set_mode((1366, 768), pygame.FULLSCREEN, 32)

pygame.display.set_caption('Eastman-Prins HCI Experiment 2014')

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GREY = (40, 40, 40)

LINECOLOUR = BLUE
LINEWIDTH = 4

basicFont = pygame.font.SysFont(None, TEXTSIZE)
inputFont = pygame.font.SysFont(None, INTEXTSIZE)
# backSpaceFont = pygame.font.Font("Cyberbit.ttf", 24)
backSpaceFont = pygame.font.SysFont(None, 32)

keys = [basicFont.render(chr(x), True, WHITE) for x in range(65, 91)]


qwertyString = "QWERTYUIOPASDFGHJKLZXCVBNM"

bspace = u"⌫"

adjacentKeys = {"Q":"WSA", "W":"QEDSA", "E":"WRFDS", "R":"ETDFG", "T":"RYFGH", \
                "Y":"TUGHJ", "U":"YIHJK", "I":"UOJKL", "O":"IPKL", \
                "P":"OL", "A":"QWSXZ", "S":"QWEADZXC", "D":"WERSFXCV", \
                "F":"ERTDGCVB", "G":"RTYFHVBN", "H":"TYUGJBNM", "J":"YUIHKBNM", "K":"UIOJLM", \
                "L":"IOPKM", "Z":"ASX", "X":"ASDZC", "C":"SDFXV", "V":"DFGCB", "B":"FGHVN", "N":"GHJBM", "M":"JKLN"}

backSpaceAdjacent = ["p"]
spaceBarAdjacent = ["xcvbnm"]

qwertyPositions = [(XOFFSET + x * (KEYWIDTH + 2 * BORDERWIDTH), KEYSTARTY) \
                   for x in range(10)]

BACKSPACEX, BACKSPACEY = 1275, KEYSTARTY

BACKSPACERECT = pygame.Rect(BACKSPACEX - 0.75 * KEYWIDTH - BORDERWIDTH, \
                            BACKSPACEY - 0.75 * KEYHEIGHT - BORDERWIDTH, \
                            1.5 * KEYWIDTH + 2 * BORDERWIDTH, \
                            1.5 * KEYHEIGHT + 2 * BORDERWIDTH)

qwertyPositions.extend([(XOFFSET + int(KEYWIDTH / 3. + \
                        x * (KEYWIDTH + 2 * BORDERWIDTH)), \
                KEYSTARTY + KEYHEIGHT + 2 * BORDERWIDTH) for x in range(9)])

qwertyPositions.extend([(XOFFSET + 2 * KEYWIDTH / 3. + \
                        x * (KEYWIDTH + 2 * BORDERWIDTH), \
            KEYSTARTY + KEYHEIGHT * 2 + 4 * BORDERWIDTH) for x in range(9)])

keyBounds = []
linesToDraw = []
wordsEntered = []
oldWE = [-1]
otherChoices = []
oldOC = [-1]

# log1 = open("log1_" + str(int(time.time())) + "_.log", "w")
# log2 = open("log2_" + str(int(time.time())) + "_.log", "w")

# White BG
windowSurface.fill(WHITE)


def drawSuggestionText():
    global otherChoices, oldOC

    if oldOC != otherChoices:
        for i in range(len(otherChoices)):
            pygame.draw.rect(windowSurface, BLACK, \
                        (OTHERRECT_L[i] - BORDERWIDTH, \
                         OTHERRECT_T - BORDERWIDTH, \
                         OTHERRECT_WIDTH + 2 * BORDERWIDTH, \
                         OTHERRECT_HEIGHT + 2 * BORDERWIDTH))

            pygame.draw.rect(windowSurface, WHITE, \
                    (OTHERRECT_L[i], OTHERRECT_T, OTHERRECT_WIDTH, OTHERRECT_HEIGHT))
            # Input text
            text = inputFont.render(otherChoices[i], True, BLACK)
            textRect = text.get_rect()

            textRect.x = OTHERRECT_L[i] + BORDERWIDTH
            textRect.y = OTHERRECT_T + BORDERWIDTH

            windowSurface.blit(text, textRect)
            pygame.display.update(suggestionRect[i])


def updatePhraseText():
    phraseEntryTimes.append(time.time() - experimentStartTime)
    pygame.draw.rect(windowSurface, BLACK, \
                    (PHRASERECT_L - BORDERWIDTH, \
                     PHRASERECT_T - BORDERWIDTH, \
                     PHRASERECT_WIDTH + 2 * BORDERWIDTH, \
                     PHRASERECT_HEIGHT + 2 * BORDERWIDTH))

    pygame.draw.rect(windowSurface, WHITE, \
            (PHRASERECT_L, PHRASERECT_T, PHRASERECT_WIDTH, PHRASERECT_HEIGHT))
    # Input text
    text = inputFont.render(phrasesToEnter[-1], True, BLACK)
    textRect = text.get_rect()

    textRect.x = PHRASERECT_L + BORDERWIDTH
    textRect.y = PHRASERECT_T + BORDERWIDTH

    windowSurface.blit(text, textRect)

    pygame.display.update(pygame.Rect(PHRASERECT_L - BORDERWIDTH, \
                                      PHRASERECT_T - BORDERWIDTH, \
                                      PHRASERECT_WIDTH + 2 * BORDERWIDTH, \
                                      PHRASERECT_HEIGHT + 2 * BORDERWIDTH))


def drawUpperText():
    global wordsEntered, oldWE
    if wordsEntered != oldWE:
    # Input text rectangles
        pygame.draw.rect(windowSurface, BLACK, \
                    (INPUTRECT_L - BORDERWIDTH, \
                     INPUTRECT_T - BORDERWIDTH, \
                     INPUTRECT_WIDTH + 2 * BORDERWIDTH, \
                     INPUTRECT_HEIGHT + 2 * BORDERWIDTH))

        pygame.draw.rect(windowSurface, WHITE, \
                (INPUTRECT_L, INPUTRECT_T, INPUTRECT_WIDTH, INPUTRECT_HEIGHT))
        # Input text
        text = inputFont.render("_".join(wordsEntered), True, BLACK)
        textRect = text.get_rect()

        textRect.x = INPUTRECT_L + BORDERWIDTH
        textRect.y = INPUTRECT_T + BORDERWIDTH

        windowSurface.blit(text, textRect)
        oldWE = list(wordsEntered)

        pygame.display.update(pygame.Rect(INPUTRECT_L - BORDERWIDTH, \
                                          INPUTRECT_T - BORDERWIDTH, \
                                          INPUTRECT_WIDTH + 2 * BORDERWIDTH, \
                                          INPUTRECT_HEIGHT + 2 * BORDERWIDTH))


def drawAllKeys():
    for i, text in enumerate(keys):
        if i == hi:
            continue

        textRect = text.get_rect()
        # move em to right spot
        textRect.centerx, textRect.centery = \
        qwertyPositions[qwertyString.find(chr(65 + i))]

        # draw a rect around them
        pygame.draw.rect(windowSurface, BLACK, \
                         (textRect.centerx - KEYWIDTH / 2 - BORDERWIDTH, \
                          textRect.centery - KEYHEIGHT / 2 - BORDERWIDTH, \
                          KEYWIDTH + BORDERWIDTH * 2, \
                          KEYHEIGHT + BORDERWIDTH * 2))

        pygame.draw.rect(windowSurface, RED, \
                         (textRect.centerx - KEYWIDTH / 2, \
                         textRect.centery - KEYHEIGHT / 2, \
                         KEYWIDTH, KEYHEIGHT))

        # if this is the first time, set up our keybounds
        if len(keyBounds) < 26:
            keyBounds.append(((textRect.centerx - KEYWIDTH / 2 - BORDERWIDTH, \
                            textRect.centerx + KEYWIDTH / 2 - BORDERWIDTH), \
                            (textRect.centery - KEYHEIGHT / 2 + BORDERWIDTH, \
                             textRect.centery + KEYHEIGHT / 2 + BORDERWIDTH)))

        # blit it
        windowSurface.blit(text, textRect)


def drawSpaceBar(over=False):
    if mode in [WII_BASIC, KIN_BASIC]:
        text = basicFont.render("Space", True, WHITE)
        textRect = text.get_rect()
        textRect.centerx, textRect.centery = SPACEBAR_TLX + SPACEBAR_WIDTH / 2. + BORDERWIDTH, \
                                                SPACEBAR_TLY + KEYHEIGHT / 2. + BORDERWIDTH
        pygame.draw.rect(windowSurface, BLACK, \
                         (SPACEBAR_TLX, \
                         SPACEBAR_TLY, \
                         SPACEBAR_WIDTH + 2 * BORDERWIDTH, \
                         KEYHEIGHT + 2 * BORDERWIDTH))

        pygame.draw.rect(windowSurface, GREY if over else RED, \
                         (SPACEBAR_TLX + BORDERWIDTH, \
                         SPACEBAR_TLY + BORDERWIDTH, \
                         SPACEBAR_WIDTH, \
                         KEYHEIGHT))
        windowSurface.blit(text, textRect)
        pygame.display.update(SPACEBARRECT)


def drawBackSpace(over=False):
    text = backSpaceFont.render("<--Backspace", True, WHITE)
    textRect = text.get_rect()
    textRect.centerx, textRect.centery = BACKSPACEX, BACKSPACEY

    pygame.draw.rect(windowSurface, BLACK, \
                         (textRect.centerx - 1.5 * KEYWIDTH / 2 - BORDERWIDTH, \
                          textRect.centery - KEYHEIGHT / 2 - BORDERWIDTH, \
                          1.5 * KEYWIDTH + BORDERWIDTH * 2, \
                          KEYHEIGHT + BORDERWIDTH * 2))

    pygame.draw.rect(windowSurface, GREY if over else RED, \
                         (textRect.centerx - 1.5 * KEYWIDTH / 2, \
                         textRect.centery - KEYHEIGHT / 2, \
                         1.5 * KEYWIDTH, KEYHEIGHT))

    windowSurface.blit(text, textRect)
    pygame.display.update(pygame.Rect((textRect.centerx - 1.5 * KEYWIDTH / 2 - BORDERWIDTH, \
                          textRect.centery - KEYHEIGHT / 2 - BORDERWIDTH, \
                          1.5 * KEYWIDTH + BORDERWIDTH * 2, \
                          KEYHEIGHT + BORDERWIDTH * 2)))


def highlightKeys():
    global oldhi, hi

    redrawKeys = []
    if hi != -1:
        redrawKeys = [ord(x) - 65 for x in adjacentKeys[chr(65 + hi)]]
    if oldhi != -1:
        redrawKeys += [oldhi]

    for key in redrawKeys:
        text = keys[key]
        textRect = text.get_rect()
        # move em to right spot
        textRect.centerx, textRect.centery = qwertyPositions[\
                                            qwertyString.find(chr(65 + key))]

        # draw a rect around them
        pygame.draw.rect(windowSurface, BLACK, \
                         (textRect.centerx - KEYWIDTH / 2 - BORDERWIDTH, \
                          textRect.centery - KEYHEIGHT / 2 - BORDERWIDTH, \
                           KEYWIDTH + BORDERWIDTH * 2, \
                           KEYHEIGHT + BORDERWIDTH * 2))

        pygame.draw.rect(windowSurface, RED, \
                         (textRect.centerx - KEYWIDTH / 2, \
                          textRect.centery - KEYHEIGHT / 2, \
                          KEYWIDTH, \
                          KEYHEIGHT))

        # blit it
        windowSurface.blit(text, textRect)
        drawLines(None)
        pygame.display.update(\
                pygame.Rect(textRect.centerx - KEYWIDTH / 2 - BORDERWIDTH * 2, \
                            textRect.centery - KEYHEIGHT / 2 - BORDERWIDTH * 2, \
                            KEYWIDTH + 4 * BORDERWIDTH, \
                            KEYHEIGHT + 4 * BORDERWIDTH))

    if hi != -1:
        text = keys[hi]
        textRect = text.get_rect()
        # move em to right spot
        textRect.centerx, textRect.centery = qwertyPositions[\
                                            qwertyString.find(chr(65 + hi))]

        # draw a rect around them
        pygame.draw.rect(windowSurface, BLACK, \
                         (textRect.centerx - KEYWIDTH / 2 - BORDERWIDTH, \
                          textRect.centery - KEYHEIGHT / 2 - BORDERWIDTH, \
                          KEYWIDTH + BORDERWIDTH * 2, \
                          KEYHEIGHT + BORDERWIDTH * 2))

        pygame.draw.rect(windowSurface, GREY, \
                         (textRect.centerx - KEYWIDTH / 2, \
                          textRect.centery - KEYHEIGHT / 2, \
                          KEYWIDTH, \
                          KEYHEIGHT))

        # blit it
        windowSurface.blit(text, textRect)
        drawLines(None)
        pygame.display.update(\
            pygame.Rect(textRect.centerx - KEYWIDTH / 2 - 2 * BORDERWIDTH, \
                       textRect.centery - KEYHEIGHT / 2 - 2 * BORDERWIDTH, \
                       KEYWIDTH + 4 * BORDERWIDTH,
                       KEYHEIGHT + 4 * BORDERWIDTH))


def drawLines(rect):
    # if there are lines to draw from the swyping
    if len(linesToDraw) > 2:
        pygame.draw.lines(windowSurface, LINECOLOUR, False, \
                          linesToDraw, LINEWIDTH)


def drawScreen(rect=None):
    stime = time.time()

    drawUpperText()

    highlightKeys()

    stime = time.time() - stime
    # log1.write(str(stime) + "\n")


def QwertyOrd(char):
    index = 0
    while index < len(qwertyString) and char != qwertyString[index]:
        index += 1
    return index


def Dist(pos1, pos2):
    diff = np.array([pos1[0] - pos2[0], pos1[1] - pos2[1]])
    return np.linalg.norm(diff)


def Pad(x):
    return '0' * (4 - len(str(x))) + str(x)


class FrameData:
    def __init__(self, pos):
        self.position = np.array(pos)
        self.time = datetime.datetime.now()
        self.velocity = 0
        self.accel = 0
        self.closestLetter = 'z'
        self.letterDistance = 0
        self.updateQwertyInfo()

    def updateQwertyInfo(self):
        distances = [Dist(self.position, p) for p in qwertyPositions]
        minDistIndex = np.argmin(distances)
        if 0 <= minDistIndex < len(qwertyString):
            self.closestLetter = qwertyString[minDistIndex]
            self.letterDistance = distances[minDistIndex]

    def getClosestLetter(self):
        return self.closestLetter


class SwypeTrajectory:

    def __init__(self, fileName):
        self._fileName = fileName
        self._frameDataList = []
        self.word = ""

    def AddFrame(self, pos):
        newFrame = FrameData(pos)
        self._frameDataList.append(newFrame)

    def Pickle(self):
        pickle.dump(self, open(self._fileName, "wb"))

    def Load(self, fileName):
        self = pickle.load(open(fileName, "wb"))

    def GetLetterSequence(self):
        return ''.join([x.closestLetter for x in self._frameDataList])

    def __str__(self):
        return self.GetLetterSequence()


drawScreen()
drawAllKeys()
pygame.display.update()

drawBackSpace()
drawSpaceBar()


def close():
    f1 = open(logDir + "log_Mouse_" + partName + "_" + str(experimentStartTime) + "_" + textmode + "_.log", 'w')
    f1.write("\n".join([" ".join([str(y) for y in x]) for x in mouseLog]))
    f1.close()

    f1 = open(logDir + "log_WETimes_" + partName + "_" + str(experimentStartTime) + "_" + textmode + "_.log", 'w')
    f1.writelines("\n".join([str(x) for x in wordEntryTimes]))
    f1.close()

    f1 = open(logDir + "log_PETimes_" + partName + "_" + str(experimentStartTime) + "_" + textmode + "_.log", 'w')
    f1.writelines("\n".join([str(x) for x in phraseEntryTimes]))
    f1.close()

    f1 = open(logDir + "log_AllWords_" + partName + "_" + str(experimentStartTime) + "_" + textmode + "_.log", 'w')
    f1.writelines("\n".join([str(x) for x in totalWordsEntered]))
    f1.close()

    # log1.close()
    # log2.close()
    pygame.quit()
    sys.exit()


def keyCollision(mx, my):
    for i, (x, y) in enumerate(keyBounds):
        if x[0] <= mx <= x[1] and y[0] <= my <= y[1]:
            return i


def work(trajectory):
    global wordsEntered, otherChoices
    stime = time.time()
    otherChoices = ["", "", ""]
    if len(set(str(trajectory))) == 1:
        wordsEntered.append(list(set(str(trajectory)))[0])
    else:
        top4 = analysis.AnalyzeTrajectory(trajectory)
        if len(top4) != 0:
            wordsEntered.append(top4[0])
            wordEntryTimes.append(time.time() - experimentStartTime)
            totalWordsEntered.append(wordsEntered[-1])
        for i, x in enumerate(top4[1:]):
            otherChoices[i] = x

    drawSuggestionText()
    # log2.write(str(time.time() - stime) + "\n")
    drawScreen()


def highlight(i, mx, my):
    global oldhi, hi
    if i == None:
        return
    oldhi = -1 if hi == i else hi
    hi = i
    drawScreen(pygame.Rect(mx - MOUSEBOXW, my - MOUSEBOXH, \
                           2 * MOUSEBOXW, 2 * MOUSEBOXH))


def mouseInKBRange((x, y)):
    return KEYSRECT.collidepoint(x, y)


def checkMouseClickSuggestion((x, y)):
    for i in range(3):
        if suggestionRect[i].collidepoint(x, y):
            wordsEntered[-1], otherChoices[i] = otherChoices[i], wordsEntered[-1]
            drawUpperText()
            drawSuggestionText()


def startExperiment():
    global experimentRunning, experimentStartTime, wordsEntered, otherChoices

    experimentRunning = True
    experimentStartTime = time.time()
    wordsEntered = []
    otherChoices = ["", "", ""]
    drawUpperText()
    drawSuggestionText()
    for _ in range(NUM_PHRASES_PER_TRIAL):
        phrasesToEnter.append(phrases[random.randint(0, len(phrases) - 1)])
    print phrasesToEnter
    updatePhraseText()


def pathStart():
    global trajectory, event, linesToDraw, drawPath
    trajectory = None
    linesToDraw = [event.pos]
    drawPath = True
    trajectory = SwypeTrajectory("")
    trajectory.AddFrame(event.pos)
    if experimentRunning:
        mouseLog.append(["MouseDown-Keys", event.pos[0], event.pos[1], drawPath])


def pathEnd():
    global trajectory, event, linesToDraw, drawPath
    if trajectory != None:
        print "mbu " + str(trajectory)
        drawPath = False
        linesToDraw = []
        work(trajectory)
        drawAllKeys()
        pygame.display.update(KEYSRECT)
        if experimentRunning:
            mouseLog.append(["MouseUp-GoodTraj", event.pos[0], event.pos[1], drawPath])
    else:
        if experimentRunning:
            mouseLog.append(["MouseUp-BadTraj", event.pos[0], event.pos[1], drawPath])


def singleClick():
    # BOOBS
    global event
    mx, my = event.pos
    key = keyCollision(mx, my)
    if key is None:
        return

    key = chr(65 + key)

    if len(wordsEntered) == 0:
        wordsEntered.append(key)
    else:
        wordsEntered[-1] += key

    drawUpperText()

# run the game loop
spaceBarDown = False
trajectory = None

rightClickTimeStamp = 0
mx, my = 0, 0
while True:
    event = pygame.event.poll()

    mouseState = pygame.mouse.get_pressed()
    if mouseState[-1] == 0 and rightClickTimeStamp != 0:
        print "got one!"
        rightClickTimeStamp = 0

    if rightClickTimeStamp > 0:
        ts = time.time()
        rect = pygame.Rect(mx - 25, my - 25, 50, 50)
        if (ts - rightClickTimeStamp) * 2 > 1:
            rightClickTimeStamp = 0
        else:
            finAngle = (ts - rightClickTimeStamp) * 4 * math.pi
            # mx, my = event.pos
            pygame.draw.arc(windowSurface, GREEN, rect, 0, finAngle, 15)
        pygame.display.update(rect)

    if event.type == pygame.locals.QUIT or \
        (event.type == pygame.locals.KEYDOWN and event.key == pygame.K_ESCAPE):
        close()
    elif event.type == pygame.locals.KEYDOWN and event.key == pygame.K_u:
        pygame.display.update()
    elif event.type == pygame.locals.KEYDOWN and event.key == pygame.K_s \
            and not experimentRunning:
        startExperiment()
    elif event.type == pygame.locals.MOUSEBUTTONDOWN:
        mouseState = pygame.mouse.get_pressed()
        if mouseState[-1] == 0 and rightClickTimeStamp != 0:
            print "got one!"
            rightClickTimeStamp = 0

        # we have three different modes.
        # one avec click and drag (wii swype)
        # one where click does peck input (wii basic and kinect basic)
        # and one wehre swypes are deliminited by clicks (kinect swype)
        if mouseInKBRange(event.pos):
            if mode == WII_SWYPE:
                print "WWIIIII"
                print drawPath
                pathStart()
                print drawPath
                print "--"
            elif mode == KIN_SWYPE:
                if mouseState[0] == 1:
                    if drawPath:
                        pathEnd()
                    else:
                        pathStart()
                elif mouseState[-1] == 1:
                    # right click
                    if rightClickTimeStamp == 0:
                        rightClickTimeStamp = time.time()
            else:
                singleClick()
        elif BACKSPACERECT.collidepoint(event.pos):
            if pygame.mouse.get_pressed() == (0, 0, 1): continue
            if mode in [KIN_SWYPE, WII_SWYPE]:
                if len(wordsEntered) > 0:
                    wordsEntered.pop()
                    otherChoices = ["", "", ""]
                    drawUpperText()
                    drawSuggestionText()
            else:
                if len(wordsEntered) > 0:
                    if len(wordsEntered[-1]) == 0:
                        wordsEntered.pop()
                        drawUpperText()
                    else:
                        wordsEntered[-1] = wordsEntered[-1][:-1]
                        drawUpperText()
            if experimentRunning:
                mouseLog.append(["MouseDown-BACKSPACE", event.pos[0], event.pos[1], drawPath])
        elif SPACEBARRECT.collidepoint(event.pos):
            if pygame.mouse.get_pressed() == (0, 0, 1): continue
            if mode in [WII_BASIC, KIN_BASIC]:
                wordsEntered.append("")
                drawUpperText()
        else:
            if pygame.mouse.get_pressed() == (0, 0, 1): continue
            checkMouseClickSuggestion(event.pos)
            if experimentRunning:
                mouseLog.append(["MouseDown-ElseWhere", event.pos[0], event.pos[1], drawPath])
    elif event.type == pygame.locals.MOUSEBUTTONUP:
        if mode == WII_SWYPE and drawPath:
            pathEnd()

    elif event.type == pygame.locals.MOUSEMOTION:
        mx, my = event.pos
        if experimentRunning:
                mouseLog.append(["MouseMove", event.pos[0], event.pos[1], drawPath])
        kc = keyCollision(mx, my)
        if BACKSPACERECT.collidepoint(event.pos):
            drawBackSpace(True)
            backSpaceDrawn = True
        elif backSpaceDrawn:
            drawBackSpace(False)

        if SPACEBARRECT.collidepoint(event.pos):
            drawSpaceBar(True)
            spaceBarDown = True
        elif spaceBarDown:
            drawSpaceBar(False)

        if kc == None:
            # print "KC = NONE with mx,my = " + str(mx) + ", " + str(my)
            continue
        highlight(kc, mx, my)
        if drawPath:
            linesToDraw.append(event.pos)
            trajectory.AddFrame(event.pos)

    if experimentRunning and " ".join(wordsEntered) == phrasesToEnter[-1]:
        if len(phrasesToEnter) > 1:
            phrasesToEnter.pop()
            updatePhraseText()
            wordsEntered = []
            otherChoices = ["", "", ""]
            drawUpperText()
            drawSuggestionText()
        else:
            phraseEntryTimes.append(time.time() - experimentStartTime)
            wordsEntered = ["You", "Are", "Done!"]
            otherChoices = ["", "", ""]
            drawUpperText()
            drawSuggestionText()
            experimentRunning = False
