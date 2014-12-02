# -*- coding: utf-8 -*-

import sys
import pygame.locals
import datetime
import numpy as np
import pickle
import re
import analysis
import time

drawPath = False
backSpaceDrawn = False
INTEXTSIZE = 24
INPUTRECT_L = 50
INPUTRECT_T = 50
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

KEYSTARTY = 400
XOFFSET = KEYWIDTH / 2 + 100

KEYSRECT = pygame.Rect(XOFFSET - 0.5 * KEYWIDTH, KEYSTARTY - 0.5 * KEYHEIGHT, \
                10 * (KEYWIDTH + BORDERWIDTH), 3 * (KEYHEIGHT + BORDERWIDTH))

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

qwertyPositions = [(XOFFSET + x * (KEYWIDTH + 2 * BORDERWIDTH), KEYSTARTY) \
                   for x in range(10)]

BACKSPACEX, BACKSPACEY = XOFFSET + 9 * (KEYWIDTH + 2 * BORDERWIDTH) \
                                 + 1.25 * KEYWIDTH + 2 * BORDERWIDTH, KEYSTARTY

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

log1 = open("log1_" + str(int(time.time())) + "_.log", "w")
log2 = open("log2_" + str(int(time.time())) + "_.log", "w")

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
        text = inputFont.render(" ".join(wordsEntered), True, BLACK)
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
    if oldhi != -1:
        text = keys[oldhi]
        textRect = text.get_rect()
        # move em to right spot
        textRect.centerx, textRect.centery = qwertyPositions[\
                                            qwertyString.find(chr(65 + oldhi))]

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
    log1.write(str(stime) + "\n")


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

def close():
    log1.close()
    log2.close()
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
    if len(trajectory.GetLetterSequence()) == 1:
        wordsEntered.append(trajectory.GetLetterSequence())
    else:
        top4 = analysis.AnalyzeTrajectory(trajectory)
        if len(top4) != 0:
            wordsEntered.append(top4[0])
        for i, x in enumerate(top4[1:]):
            otherChoices[i] = x
    drawSuggestionText()
    log2.write(str(time.time() - stime) + "\n")
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

# run the game loop
trajectory = None

clock = pygame.time.Clock()

print keyBounds

while True:
    event = pygame.event.poll()
    if event.type == pygame.locals.QUIT or \
        (event.type == pygame.locals.KEYDOWN and event.key == pygame.K_ESCAPE):
        close()
    elif event.type == pygame.locals.KEYDOWN and event.key == pygame.K_u:
        pygame.display.update()
    elif event.type == pygame.locals.MOUSEBUTTONDOWN:
        trajectory = None
        if mouseInKBRange(event.pos):
            linesToDraw = [event.pos]
            drawPath = True
            trajectory = SwypeTrajectory("training/trajectory" + \
                            re.sub(r' ', r'_', str(datetime.datetime.now())))
            trajectory.AddFrame(event.pos)
        elif BACKSPACERECT.collidepoint(event.pos):
            if len(wordsEntered) > 0:
                wordsEntered.pop()
                otherChoices = ["", "", ""]
                drawUpperText()
                drawSuggestionText()
        else:
            checkMouseClickSuggestion(event.pos)
    elif event.type == pygame.locals.MOUSEBUTTONUP:
        if trajectory != None:
            print "mbu" + str(trajectory)
            drawPath = False
            linesToDraw = []
            work(trajectory)
            drawAllKeys()
            pygame.display.update(KEYSRECT)

    elif event.type == pygame.locals.MOUSEMOTION:
        mx, my = event.pos
        kc = keyCollision(mx, my)
        if BACKSPACERECT.collidepoint(event.pos):
            drawBackSpace(True)
            backSpaceDrawn = True
        elif backSpaceDrawn:
            drawBackSpace(False)

        if kc == None:
            # print "KC = NONE with mx,my = " + str(mx) + ", " + str(my)
            continue
        highlight(kc, mx, my)
        if drawPath:
            linesToDraw.append(event.pos)
            trajectory.AddFrame(event.pos)
