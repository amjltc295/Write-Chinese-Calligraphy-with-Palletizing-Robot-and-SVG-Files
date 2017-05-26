'''
    File name: readCharacter.py
    Author: Ya-Liang Chang b03901014@ntu.edu.tw
    Date created: 5/26/2017
    Date last modified: 5/26/2017
    Python Version: 3.6

    Path planning for palletizing robot to write Chinese characters.

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

    Then, write the medians in pygame, and transform to paths for palletizing robot.

'''
import json
import pygame
WIDTH = 500

"""
Each stroke is laid out on a 1024x1024 size coordinate system where:
    The upper-left corner is at position (0, 900).
    The lower-right corner is at position (1024, -124).
However, the upper-left corner of pygame is (0, 0), and there is no negative coordinate.
So the stroke need not be shifted and flip.
"""
SCALE_X = 0.5
SCALE_Y = -0.5
SHIFT_X = 0
SHIFT_Y = 900

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def write_sentence(DBFilename, sentence):
    """Find char data in the DB and write the sentence."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, WIDTH))
    screen.fill(WHITE)

    characters = list(sentence)
    print("Character list: ", characters)
    with open(DBFilename, "r") as f:
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
                    write_character(screen, eachCharInDB)
                    break
            if not found:
                charNotFoundList.append(eachCharToWrite)

        print("Searching ", count, " / ", len(characters), " ... Done.")
    print("Found: ", [char['character'] for char in charToWriteDataList])
    print("Not found: ", [char for char in charNotFoundList])

def write_character(screen, char):
    """Write the char on Pygame."""
    screen.fill(WHITE)
    for eachLine in char['medians']:
        pointList = [((point[0] - SHIFT_X)*SCALE_X, (point[1] - SHIFT_Y)*SCALE_Y) for point in eachLine]
        pygame.draw.lines(screen, BLACK, True, pointList)
        pygame.display.update()


if __name__ == '__main__':

    sentence = "床前明月光a疑是地上霜"
    sentence = input("Sentence to write: ")
    DBFilename = 'graphics.txt'
    write_sentence(DBFilename, sentence)
