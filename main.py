from dublib.Functions.System import CheckPythonMinimalVersion

from Source.CLI import CommandsOrchestrator
from Source.Core.SystemObjects import SystemObjects

CheckPythonMinimalVersion(3, 12)
Objects = SystemObjects()
CommandsOrchestrator(Objects).run()