import os
import sys

from dublib.Functions.System import CheckPythonMinimalVersion

from .cli import CommandsOrchestrator
from .core.system_objects import SystemObjects

def main():
	CheckPythonMinimalVersion(3, 12)
	sys.path.append(os.getcwd())
	Objects = SystemObjects()
	CommandsOrchestrator(Objects).run()

if __name__ == "__main__":
	main()