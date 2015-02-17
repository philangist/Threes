from sys import exit
from argparse import ArgumentParser


from matrix import GameBoard


def build_parser():
    parser = ArgumentParser('Threes. The hot new gaming sensation.')
    parser.add_argument('-r', '--row-size', default=5)
    parser.add_argument('-c', '--column-size', default=5)
    parser.add_argument('-f', '--fill-ratio', default=0.5)
    parsed_arguments = parser.parse_args()
    return parsed_arguments


if __name__ == '__main__':
    args = build_parser()
    row_size = int(args.row_size)
    column_size = int(args.column_size)
    fill_ratio = float(args.fill_ratio)

    print 'Game starting... \n'
    print 'You can end the current session by typing "exit".\n'
    print 'For more help, you can type "help"\n'

    board = GameBoard(row_size, column_size, fill_ratio)
    print(board)

    while True:
        command = raw_input("> Next command: ")
        if command == "exit":
            exit()
        elif command == "help":
            print (
                "Available commands: 'help', 'score', 'exit', "
                "'left', 'right', 'up', 'down'\n"
            )
        elif command == "score":
            print "Current score: ", board.score
        else:
            board.move(command)
            print(board)
            if board.game_over():
                print 'game over!'
                exit()
