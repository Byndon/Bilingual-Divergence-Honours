#!/Documents/2020Honours/ABM/py3venv/bin
import mesa
from mesa import Agent, Model
import networkx
# look at pyCX https://github.com/hsayama/PyCX
# look at pyNSim https://umwrg.github.io/pynsim/architecture.html


class LanguageAgent(Agent):
    def __init__(self, x, y):
        super().__init__(x, y)
        pass


