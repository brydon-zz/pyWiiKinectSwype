import datetime
import pygame
import numpy as np
import matplotlib.pyplot as plt
import pickle
import sys
import re
import analysis


qwertyString = "qwertyuiopasdfghjklzxcvbnm"
qwertyPositions = [(12, 74), (34, 72), (59, 76),
(82, 75), (106, 75), (130, 77), (152, 74),
(178, 75), (202, 75), (225, 75), (23, 113),
(49, 113), (73, 113), (96, 114), (120, 114),
(144, 114), (167, 114), (190, 114), (214, 114),
(41, 155), (65, 155), (90, 156), (113, 155),
(136, 154), (160, 153), (187, 153)]

def QwertyOrd(char):
    
    while index < len(qwertyString) and char != qwertyString[index]:
        index += 1
    return index

def Dist(pos1, pos2):
    diff = np.array([pos1[0] - pos2[0], pos1[1] - pos2[1]])
    return np.linalg.norm(diff) 

def Pad(x):
    return '0'*(4-len(str(x))) + str(x)

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
        pickle.dump( self, open( self._fileName, "wb" ) )
    def Load(self, fileName):
        self = pickle.load( open( fileName, "wb"))
    def GetLetterSequence(self):
        return ''.join([x.closestLetter for x in self._frameDataList])
        
        
def main ():
    pygame.display.set_caption('Testing')
    pygame.init()
    
    screen = pygame.display.set_mode((270,270))
    img = pygame.image.load("swype.jpeg")
    screen.blit(img,(0,0))
    pygame.display.flip()

    linesToDraw = []
    running = True
    recording = False
    oldpos = None

    trajectory = SwypeTrajectory("training/trajectory" + re.sub(r' ', r'_', str(datetime.datetime.now())))

    while running:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEMOTION and recording == True:
            linesToDraw.append(event.pos)
            trajectory.AddFrame(event.pos) 
            screen.blit(img, (0,0))
            pygame.draw.lines(screen, (255, 127, 80), False, linesToDraw, 4)
            pygame.display.update()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            linesToDraw = [event.pos]
            if recording:
                analysis.AnalyzeTrajectory(trajectory)
                while True:
                    event = pygame.event.poll()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        frameData = FrameData(event.pos)
                        if frameData.getClosestLetter() == 's':
                            trajectory.Pickle()
                        break
                        #     break
                        # elif frameData.getClosestLetter() == 'c':
                        #     break
                    elif event.type == pygame.KEYDOWN:
                        trajectory.word += chr(event.key)
                trajectory = SwypeTrajectory("training/trajectory" + re.sub(r' ', r'_', str(datetime.datetime.now())))
            recording = not recording
                

        screen.fill((0, 0, 0))
        # pygame.display.flip()

if (__name__ == '__main__'):
    main()

