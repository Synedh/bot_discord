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
        self.defeat_message = 'Dommage, vous êtes pendu !\nLe mot était %s.' % self.word
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
            return 0, 'Valeur incorrecte : ' + value + '.\n' + self.turn_message 
        if value in self.triedchars:
            return 0, value + ' a déjà été testée !\n' + self.turn_message

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

        message = ''
        if result:
            message += value + ' n\'est pas dans le mot !\n' + self.print_stats()
        else:
            message += value + ' est bon !\n' + self.print_stats()
        if self.step == len(images) - 1:
            return 1, '%s\n%s\n%s' % (message, self.defeat_message, self.close_message)
        elif ''.join(self.foundword) == self.word:
            return 1, '%s\n%s\n%s' % (message, self.victory_message, self.close_message)
        else:
            return 0, message + '\n' + self.turn_message
