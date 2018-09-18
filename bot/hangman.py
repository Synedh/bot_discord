import os
import random

images = [
    '        \n        \n        \n        \n        \n        \n        \n',
    '        \n        \n        \n        \n        \n        \n===     \n',
    '        \n|       \n|       \n|       \n|       \n|       \n===     \n',
    '--------\n|       \n|       \n|       \n|       \n|       \n===     \n',
    '--------\n| /     \n|/      \n|       \n|       \n|       \n===     \n',
    '--------\n| /   | \n|/      \n|       \n|       \n|       \n===     \n',
    '--------\n| /   | \n|/    o \n|       \n|       \n|       \n===     \n',
    '--------\n| /   | \n|/    o \n|    <|>\n|       \n|       \n===     \n',
    '--------\n| /   | \n|/    o \n|    <|>\n|    / \\\n|       \n===     \n',
]
dir_path = os.path.dirname(os.path.realpath(__file__))

class Hangman:
    def __init__(self):
        self.step = 0
        with open(dir_path + '/dict.txt') as file:
            words = file.readlines()
            self.word = words[random.randint(0, len(words) - 1)][:-1]
        self.foundword = list('_' * len(self.word))
        self.triedchars = []
        self.turn_message = 'Entrez un mot ou une lettre.'
        self.victory_message = 'Félicitation, vous avez trouvé le mot !'
        self.solution_message = 'Le mot était %s.' % self.word
        self.defeat_message = 'Dommage, vous êtes pendu !'
        self.close_message = 'Closing game.'

    def print_stats(self):
        # self.step = len(images) - 1
        # self.triedchars = ['A', 'B', 'C']

        printable = images[self.step].split('\n')
        printable[3] = printable[3] + '    ' + ''.join(self.foundword)
        printable.append('DEJA TEST: ' + ' '.join(self.triedchars))
        return '```\n' + '\n'.join(printable) + '```'

    def try_value(self, value):
        if len(value) != 1 and len(value) != len(self.word) or not value.isalpha():
            return 0, 'Valeur incorrecte : ' + value + '.'
        if value in self.triedchars:
            return 0, value + ' a déjà été testée !'

        result = False
        self.triedchars.append(value)
        if value == self.word:
            result = True
            self.foundword = value
        elif value in self.word:
            result = True
            tmp = list(self.word)
            while value in tmp:
                self.foundword[tmp.index(value)] = value
                tmp[tmp.index(value)] = '_'

        if not result:
            self.step += 1
            if self.step == len(images) - 1:
                return 2, value + ' n\'est pas dans le mot !'
            else:
                return 1, value + ' n\'est pas dans le mot !'
        else:
            if ''.join(self.foundword) == self.word:
                return 3, value + ' est bon !'
            else:
                return 1, value + ' est bon !'