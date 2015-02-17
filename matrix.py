import math
import random

PLACEHOLDER = None
EMPTY = 0
SCORE = 0

LEFT = 'left'
RIGHT = 'right'
DOWN = 'down'
UP = 'up'


class _Score(object):
    def __init__(self, value=0):
        self.value = value

    def update(self, value):
        self.value += value

score = _Score()


class Matrix(object):

    def __str__(self):
        output_string = ""
        for each_row in self.elements:
            for val in each_row:
                output_string += "|%s\t" % val
            output_string += "|\n"

        return output_string

    def __init__(self, elements, row_size, column_size):
        self.elements = elements
        self.row_size = row_size
        self.column_size = column_size

    def get_column_at_position(self, column_index):
        return [row[column_index] for row in self.elements]

    def get_row_at_position(self, row_index):
        return self.elements[row_index]

    def update_row_at_position(self, row_index, values):
        self.elements[row_index] = values

    def update_column_at_position(self, column_index, values):
        for i in range(len(values)):
            self.elements[i][column_index] = values[i]


class GameBoard(Matrix):
    def __init__(self, row_size, column_size, fill_ratio, score_handler=score):
        elements = self.populate(row_size, column_size, fill_ratio)
        super(GameBoard, self).__init__(elements, row_size, column_size)
        self.score_handler = score_handler

    def populate(self, row_size, column_size, fill_ratio):
        # determine total number of elements that should be filled
        chance_of_one = random.random()

        total = row_size * column_size
        fill = int(math.ceil(fill_ratio * (row_size * column_size)))
        filled = [
            1 if random.random() <= chance_of_one else 2 for x in range(fill)]

        if len(filled) < total:
            filled += [EMPTY] * (total - len(filled))

        random.shuffle(filled)
        elements = [
            filled[i:i + row_size] for i in range(0, len(filled), row_size)
        ]
        return elements

    def move(self, direction):
        # import ipdb; ipdb.set_trace()
        if direction in [LEFT, RIGHT]:
            row_values = self.elements[:]
            if direction == RIGHT:
                row_values = [row[::-1] for row in row_values]

            for row_index in range(self.row_size):
                row_value = row_values[row_index]
                translated_row_value = translate_matrix_values(row_value)
                if translated_row_value == row_value:
                    continue
                if direction == RIGHT:
                    translated_row_value.reverse()

                self.update_row_at_position(row_index, translated_row_value)

        elif direction in [UP, DOWN]:
            column_values = []
            for column_index in range(self.column_size):
                column_value = self.get_column_at_position(column_index)
                if direction == DOWN:
                    column_value.reverse()

                column_values.append(column_value)

            for column_index in range(self.column_size):
                column_value = column_values[column_index]
                translated_column_value = translate_matrix_values(
                    column_value)
                if translated_column_value == column_value:
                    continue
                if direction == DOWN:
                    translated_column_value.reverse()

                self.update_column_at_position(
                    column_index, translated_column_value)

    def game_over(self):
        for row_index in range(self.row_size):
            row = self.elements[row_index]
            if row != translate_matrix_values(row):
                return False
            row.reverse()
            if row != translate_matrix_values(row):
                return False
        for column_index in range(self.column_size):
            column = self.elements[column_index]
            if column != translate_matrix_values(column):
                return False
            column.reverse()
            if column != translate_matrix_values(column):
                return False
        return True

    @property
    def score(self):
        return self.score_handler.value


class RecentItems(object):
    def __init__(self):
        self.seen = [EMPTY, EMPTY]
        self.fixed_translate = False

    @property
    def just_seen(self):
        return self.seen[0]

    @just_seen.setter
    def just_seen(self, val):
        self.seen[0] = val

    @property
    def previously_seen(self):
        return self.seen[1]

    @previously_seen.setter
    def previously_seen(self, val):
        self.seen[1] = val

    def should_collapse(self):
        if (self.just_seen == EMPTY and self.previously_seen == EMPTY):
            return False

        if (self.just_seen == 1 and self.previously_seen == 1):
            return False

        if (
            (self.just_seen == 1 and self.previously_seen == 2) or
            (self.just_seen == 2 and self.previously_seen == 1)
        ):
            return True

        if self.just_seen == self.previously_seen:
            return True
        return False

    def should_shift(self):
        if (self.just_seen == EMPTY and self.previously_seen == EMPTY):
            if not self.fixed_translate:
                self.fixed_translate = True
                return True

        if self.just_seen != EMPTY:
            self.fixed_translate = True
            if self.previously_seen == EMPTY:
                return True

        return False

    def flush(self):
        self.seen = [EMPTY, EMPTY]

    def partial_flush(self):
        self.previously_seen = EMPTY

    def push(self, value):
        self.seen = ([value] + self.seen)[:2]


def collapse_if_adjacent(values):
    final = []
    recent_items = RecentItems()

    for item in values:
        recent_items.push(item)
        if recent_items.should_collapse():
            item = final[-1] + item
            score.update(item)
            final = final[:-1]  # remove last duplicate element
            final.append(PLACEHOLDER)
            recent_items.flush()
        final.append(item)

    return final


def shift_if_possible(values):
    final = []
    recent_items = RecentItems()
    for item in values:
        item = item or EMPTY
        recent_items.push(item)
        if recent_items.should_shift():
            final = final[:-1]
            recent_items.partial_flush()
        final.append(item)
    return final


def pad_if_neccessary(values, original):
    number_seen = False

    cleaned_values = []
    padding = []

    for element in values:
        if element == PLACEHOLDER:
            if not number_seen:
                padding.append(EMPTY)
        else:
            number_seen = True

        cleaned_values.append(element or EMPTY)

    cleaned_values += padding

    if len(cleaned_values) < len(original):
        cleaned_values += [EMPTY] * (len(original) - len(cleaned_values))

    return cleaned_values


def translate_matrix_values(values):
    translated_values = collapse_if_adjacent(values)
    translated_values = shift_if_possible(translated_values)
    translated_values = pad_if_neccessary(translated_values, values)

    chance_new_tile = 0.5

    if translated_values[-1] == EMPTY:
        if random.random() <= chance_new_tile:
            translated_values[-1] = random.choice([1, 2])

    return translated_values
