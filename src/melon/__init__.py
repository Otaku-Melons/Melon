import os
import sys

from dublib.functions.system import CheckPythonMinimalVersion

from .cli import CommandsOrchestrator
from .core.system_objects import SystemObjects

def main():
	CheckPythonMinimalVersion(3, 12)
	Objects = SystemObjects()

	CalledCommand: str = sys.argv[0].split("/")[-1]
	WorkingDirectory: str = os.getcwd()

	sys.path.append(WorkingDirectory)
	CommandsOrchestrator(Objects, CalledCommand).run()

if __name__ == "__main__":
	main()