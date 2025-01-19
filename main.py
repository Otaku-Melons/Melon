from Source.Core.SystemObjects import SystemObjects
from Source.CLI.Descriptions import CommandsList
from Source.CLI.Commands import *

from dublib.Methods.System import CheckPythonMinimalVersion
from dublib.Methods.Filesystem import MakeRootDirectories
from dublib.CLI.Terminalyzer import Terminalyzer

import sys

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ <<<<< #
#==========================================================================================#

CheckPythonMinimalVersion(3, 10)
MakeRootDirectories(["Parsers"])

#==========================================================================================#
# >>>>> НАСТРОЙКА ОБРАБОТЧИКА КОМАНД <<<<< #
#==========================================================================================#

Analyzer = Terminalyzer()
Objects = SystemObjects()
Analyzer.enable_help(True)
CommandDataStruct = Analyzer.check_commands(CommandsList)

Objects.logger.info("====== Preparing to starting ======", stdout = False)
Objects.logger.info(f"Starting with Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} on {sys.platform}.", stdout = False)
Objects.logger.info("Command: \"" + " ".join(sys.argv[1:len(sys.argv)]) + "\".", stdout = False)

if CommandDataStruct == None:
	Objects.logger.set_rule(3)
	Objects.logger.close()
	print("Unknown command!")
	exit(0)

elif CommandDataStruct.name in ("help", "list", "tagger"): Objects.LIVE_MODE = True

if not Objects.LIVE_MODE:
	Objects.logger.templates.title(SystemObjects.VERSION)

	if "f" in CommandDataStruct.flags: 
		Objects.FORCE_MODE = True
		Objects.logger.info("Force mode: ON.")

	Objects.logger.templates.option_status("Force mode", Objects.FORCE_MODE)

#==========================================================================================#
# >>>>> ОБРАБОТКА КОММАНД <<<<< #
#==========================================================================================#

try: exec(f"com_{CommandDataStruct.name}(Objects, CommandDataStruct)")
except KeyboardInterrupt: exit(0)

#==========================================================================================#
# >>>>> ЗАВЕРШЕНИЕ РАБОТЫ <<<<< #
#==========================================================================================#

Objects.logger.close()
exit(Objects.EXIT_CODE)