from pathlib import Path
import os

class confProcess:

    def __init__(self):
        self.pathWd=str(Path(os.path.realpath(__file__)).parents[1])+"/"