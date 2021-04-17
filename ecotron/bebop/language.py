from beeper.robot_beeps import random_sentence
import random

SENTENCE_COMMENCING_SHORT_1 = random_sentence(2, 3)
SENTENCE_COMMENCING_SHORT_2 = random_sentence(3, 4)
SENTENCE_COMMENCING_MID_1 = random_sentence(3, 5)
    
SENTENCE_OK_SHORT_1 = random_sentence(2, 3)
SENTENCE_OK_SHORT_2 = random_sentence(2, 4)
SENTENCE_OK_MID_1 = random_sentence(4, 5)
SENTENCE_OK_MID_2 = random_sentence(4, 6)
SENTENCE_OK_LONG_1 = random_sentence(7, 12)

SENTENCES_COMMENCING = [SENTENCE_COMMENCING_SHORT_1, SENTENCE_COMMENCING_SHORT_2, SENTENCE_COMMENCING_MID_1]
SENTENCES_OK = [SENTENCE_OK_SHORT_1, SENTENCE_OK_SHORT_1, SENTENCE_OK_SHORT_2, SENTENCE_OK_SHORT_2, SENTENCE_OK_MID_1, SENTENCE_OK_MID_2, SENTENCE_OK_LONG_1]

def random_sentence_commencing():
    return random.choice(SENTENCES_COMMENCING)

def random_sentence_ok():
    return random.choice(SENTENCES_OK)


