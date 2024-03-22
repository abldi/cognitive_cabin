from cognitive_cabin import CognitiveCabin
import os
if __name__ == '__main__':
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    
    CognitiveCabin().cmdloop()
