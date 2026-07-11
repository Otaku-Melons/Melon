from Source.Core.SystemObjects import SystemObjects
from Source.CLI.Descriptions import COMMANDS
from Source.CLI import Commands as Commands

from dublib.Methods.System import CheckPythonMinimalVersion
from dublib.CLI.Terminalyzer import Terminalyzer

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ <<<<< #
#==========================================================================================#

CheckPythonMinimalVersion(3, 12)
Objects = SystemObjects()

#==========================================================================================#
# >>>>> ОБРАБОТКА КОММАНД <<<<< #
#==========================================================================================#

Analyzer = Terminalyzer()
Analyzer.helper.enable()
CommandData = Analyzer.check_commands(COMMANDS)

if CommandData is None:
	Objects.printer.critical("Unknown command!")
	exit()

try:
	CommandName = CommandData.name.replace("-", "_")
	if CommandName != "help": exec(f"Commands.com_{CommandName}(Objects, CommandData)")
except KeyboardInterrupt:
	pass