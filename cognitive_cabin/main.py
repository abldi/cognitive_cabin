import sys
from AppInterface import AppInterface

from cognitive_cabin import CognitiveCabin

if __name__ == '__main__':
    argument = sys.argv[1] if len(sys.argv) > 1 else 'dev'
    interface = AppInterface()
    interface.startThreadInterface()
    CognitiveCabin(interface,argument).cmdloop()
