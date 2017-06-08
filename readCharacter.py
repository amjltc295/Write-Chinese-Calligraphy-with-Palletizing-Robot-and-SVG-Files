'''
    File name: readCharacter.py
    Author: Ya-Liang Chang b03901014@ntu.edu.tw
    Date created: 5/26/2017
    Date last modified: 5/26/2017
    Python Version: 3.6

    Path planning for 4 DOFs palletizing robot to write Chinese characters.

    Read characters from graphics.txt (See https://github.com/skishore/makemeahanzi).
    Each char is stored as a dictionary with three keys:
        character: The Unicode character for this glyph. Required.
        strokes: List of SVG path data for each stroke of this character, ordered by proper stroke order.
        medians: A list of stroke medians, in the same coordinate system as the SVG paths above.

        For example:
        {
        'character': '⺈',
        'strokes': ['M 441 666 Q 490 726 523 749 Q 525 750 526 751 Q 547 768 509 808 Q 486 830 469 833 Q 451 834 456 811 Q 461 792 441 757 Q 396 672 248 545 Q 232 535 232 528 Q 233 521 242 521 Q 288 521 423 651 L 441 666 Z', 'M 527 467 L 604 554 Q 653 615 705 653 Q 723 664 710 678 Q 696 692 655 714 Q 647 717 596 703 Q 454 668 441 666 L 423 651 Q 427 647 433 645 Q 457 637 541 651 Q 596 661 600 657 Q 604 653 598 639 Q 568 583 496 462 Q 521 466 527 467 Z'],
        'medians':[[[468, 819], [490, 772], [428, 689], [320, 583], [274, 547], [240, 529]], [[430, 652], [527, 665], [588, 681], [614, 681], [646, 664], [631, 632], [540, 504], [520, 478], [505, 469]]]
        }

    Then, write the character (use medians) in pygame, and transform to paths for palletizing robot.

'''
import json
import pygame
import sys
WIDTH = 500

"""
Each stroke is laid out on a 1024x1024 size coordinate system where:
    The upper-left corner is at position (0, 900).
    The lower-right corner is at position (1024, -124).
However, the upper-left corner of pygame is (0, 0), and there is no negative coordinate.
Moreover, the robot has different coordinate and scale.
So the stroke need not be shifted and flip.
The following are related constant.

Pygame
X' = x
Y' = -y + 900
Robot
X' = -x + 1024
Y' = -y + 900
"""
SCALE_X = 0.1
SCALE_Y = 0.1
X_B = 1024
Y_B = 900
SHIFT_X = 450
SHIFT_Y = 50
Y_CHAR_DIS = 90
Y_INIT_POS = -270
INK_POS = (INK_X, INK_Y) = (650, 50)


""" Constant for palletizing robot to touch the paper (down) and up. """
UP_Z = 200
DOWN_Z = 174

""" Constant for pygame color """
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Wrapper:
    def __init__(self, DBFilename):
        self.DBFilename = DBFilename
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, WIDTH))
        self.screen.fill(WHITE)

        """ Used to generate palletizing robot path code. """
        self.pathCodeList = []
        self.pointNo = 0
        self.create_robot_point(471, -6, 237)
        self.shift_y = Y_INIT_POS

    def write_sentence(self, sentence):
        """Find char data in the DB and write the sentence."""

        characters = list(sentence)
        print("Character list: ", characters)
        with open(self.DBFilename, "r") as f:
            all_char = f.readlines()
            charToWriteDataList = []
            charNotFoundList = []
            print("")
            count = 0
            for eachCharToWrite in sentence:
                print("Searching ", count, " / ", len(characters), " ...", end='\r')
                count += 1
                found = False
                for eachLine in all_char:
                    eachCharInDB = json.loads(eachLine)
                    #print (eachCharInDB['character'], end='')
                    if eachCharToWrite == eachCharInDB['character']:
                        charToWriteDataList.append(eachCharInDB)
                        found = True
                        self.write_character(eachCharInDB)
                        self.shift_y += Y_CHAR_DIS
                        break
                if not found:
                    charNotFoundList.append(eachCharToWrite)
                if count != len(sentence):
                    self.dipInk()

            print("Searching ", count, " / ", len(characters), " ... Done.")
        self.create_robot_point(0, 0, 0)
        print("Found: ", [char['character'] for char in charToWriteDataList])
        print("Not found: ", [char for char in charNotFoundList])

    def dipInk(self):
        #inkPath = [INK_POS, (INK_X-5, INK_Y)]
        #self.generate_path(inkPath)
        self.create_robot_point(INK_X, INK_Y, UP_Z)
        self.create_robot_point(INK_X-5, INK_Y, UP_Z)
    def write_character(self, char):
        """Write the character on Pygame."""
        self.screen.fill(WHITE)
        for eachLine in char['medians']:
            #X' = -x + 1024
            #Y' = -y + 900
            pointList = [((point[0] )*SCALE_X, (-point[1] + 900)*SCALE_Y) for point in eachLine]
            pygame.draw.lines(self.screen, BLACK, True, pointList)
            pygame.display.update()

            pointList = [((-point[0] + X_B)*SCALE_X + SHIFT_X, (-point[1] + Y_B)*SCALE_Y + self.shift_y) for point in eachLine]
            self.generate_path(pointList)

    def generate_path(self, pointList):
        count = 0
        for (x, y) in pointList:
            """ Move to the stating point. """
            if count == 0:
                self.create_robot_point(x, y, UP_Z)
            self.create_robot_point(x, y, DOWN_Z)
            """ Move to the last point. """
            if count == len(pointList) -1:
                self.create_robot_point(x, y, UP_Z)
            count += 1
        #self.create_robot_point(0, 0, 0)

    def create_robot_point(self, x_coor, y_coor, z_coor, spin=0):
        """ Create palletizing robot coordinate for the point. """
        self.pathCodeList.append(";************ Start Of Cartesian Coordinate Position/Pose Point #%d***************" % (self.pointNo) )
        #x
        self.pathCodeList.append("Q%d = %d" % (self.pointNo*4+1, x_coor))
        #y
        self.pathCodeList.append("Q%d = %d" % (self.pointNo*4+2, y_coor))
        #z
        self.pathCodeList.append("Q%d = %d" % (self.pointNo*4+3, z_coor))
        #spin
        self.pathCodeList.append("Q%d = %d" % (self.pointNo*4+4, spin))
        self.pathCodeList.append(";************ End Of Cartesian Coordinate Position/Pose Point   #%d***************" % (self.pointNo) )
        self.pathCodeList.append("")
        self.pointNo += 1


    def print_all(self):
        """ Print out all generated coordinates. """
        for eachLine in self.pathCodeList:
            print(eachLine)
        with open('out.txt', 'w') as write_file:
            for eachLine in self.pathCodeList:
                write_file.write(eachLine)
                write_file.write('\n')


def main():
    sentence = input("Sentence to write: ")
    DBFilename = 'graphics.txt'
    wrapper = Wrapper(DBFilename)
    wrapper.write_sentence(sentence)
    wrapper.print_all()
    pygame.display.quit()
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
