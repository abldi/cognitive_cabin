import sys

from cognitive_cabin import CognitiveCabin

if __name__ == '__main__':
    argument = sys.argv[1] if len(sys.argv) > 1 else None
    CognitiveCabin(argument).cmdloop()
