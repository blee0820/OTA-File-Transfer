import sys
import os

"""
Parses commands.txt and reads file line-by-line to be used for
Linux terminal commands.
"""

def parse_commands():
        try:
            # returns commands as a list of commands
            with open(os.path.join(sys.path[0], 'commands.txt')) as f:
                commands = [line.rstrip('\n') for line in f]
                return commands
        except FileNotFoundError as ffe:
            print(ffe)
            sys.exit(1)
        except:
            print("Was not able to successfully parse commands.")
            sys.exit(1)

if __name__ == '__main__':
    parse_commands()