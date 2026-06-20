from Source.Core.SystemObjects import SystemObjects
from Source.CLI.Descriptions import COMMANDS
from Source.CLI import Commands as Commands

from dublib.Methods.System import CheckPythonMinimalVersion
from dublib.CLI.Terminalyzer import Terminalyzer

import sys

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ <<<<< #
#==========================================================================================#

CheckPythonMinimalVersion(3, 12)
Objects = SystemObjects()

Objects.logger.info(f"Running with Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} on {sys.platform}.", stdout = False)
Objects.logger.info("Command: \"" + " ".join(sys.argv[1:len(sys.argv)]) + "\".", stdout = False)

#==========================================================================================#
# >>>>> ОБРАБОТКА КОММАНД <<<<< #
#==========================================================================================#

Analyzer = Terminalyzer()
Analyzer.helper.enable()
CommandData = Analyzer.check_commands(COMMANDS)

if CommandData is None:
	Objects.logger.critical("Unknown command!")
	Objects.logger.set_rule(3)
	Objects.logger.close()
	exit()

try:
	CommandName = CommandData.name.replace("-", "_")
	if CommandName != "help": exec(f"Commands.com_{CommandName}(Objects, CommandData)")
except KeyboardInterrupt:
	pass

#==========================================================================================#
# >>>>> ЗАВЕРШЕНИЕ РАБОТЫ <<<<< #
#==========================================================================================#

Objects.logger.close()
exit(Objects.EXIT_CODE)