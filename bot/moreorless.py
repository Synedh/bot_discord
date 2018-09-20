import random

class MoreOrLess:
    def __init__(self):
        self.i = 0
        self.min_value = 1
        self.max_value = 0
        self.correct_value = 0
        self.selected_value = 0
        self.select_message = 'Please select a maximum value.'
        self.close_message = 'Closing game.'

    def message2(self):
        return 'Please pick a value between %d and %d.' % (self.min_value, self.max_value)

    def entry(self, value: int):
        if self.max_value == 0:
            return self.choose_max(value)
        elif self.selected_value != value:
            return self.try_value(value)
        else:
            return "else"

    def choose_max(self, value: int):
        if value > 0 and value < 1000000:
            self.max_value = value
            self.correct_value = random.randint(1, value)
            return 2, 'Max value selected : %d.' % value
        else:
            return 1, 'Incorrect value : must be between 1 and 1 000 000.'

    def try_value(self, value: int):
        self.i += 1
        if value < self.min_value or value > self.max_value:
            return 2, 'Incorrect value : must be between %d and %d.' % (self.min_value, self.max_value)
        elif value == self.correct_value:
            return 3, 'Value found !\nYou found the value in %d try !' % self.i
        elif value < self.correct_value:
            self.min_value = value
            return 2, 'Correct value is higher !'
        else:
            self.max_value = value
            return 2, 'Correct value is lower !'
