from Source.Core.SystemObjects import SystemObjects
from Source.CLI.Descriptions import CommandsList
from Source.CLI.Commands import *

from dublib.Methods.System import CheckPythonMinimalVersion, Shutdown
from dublib.Methods.Filesystem import MakeRootDirectories
from dublib.CLI.Terminalyzer import Terminalyzer

import sys

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ <<<<< #
#==========================================================================================#

CheckPythonMinimalVersion(3, 10)
MakeRootDirectories(["Parsers"])

VERSION = "0.2.0-alpha"

#==========================================================================================#
# >>>>> НАСТРОЙКА ОБРАБОТЧИКА КОМАНД <<<<< #
#==========================================================================================#

Analyzer = Terminalyzer()
Objects = SystemObjects()
Analyzer.enable_help(True)
CommandDataStruct = Analyzer.check_commands(CommandsList)

Objects.logger.info("====== Preparing to starting ======")
Objects.logger.info(f"Starting with Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} on {sys.platform}.")
Objects.logger.info("Command: \"" + " ".join(sys.argv[1:len(sys.argv)]) + "\".")

if CommandDataStruct == None:
	Objects.logger.set_rule(3)
	Objects.logger.close()
	print("Unknown command!")
	exit(0)

elif CommandDataStruct.name in ("help", "list", "tagger"): Objects.LIVE_MODE = True

if not Objects.LIVE_MODE:
	Objects.logger.templates.title(VERSION)

	if "f" in CommandDataStruct.flags: 
		Objects.FORCE_MODE = True
		Objects.logger.info("Force mode: ON.")

	if "s" in CommandDataStruct.flags:
		Objects.SHUTDOWN = True
		Objects.logger.info("Computer will be turned off after script is finished!")

	Objects.logger.templates.option_status("Force mode", Objects.FORCE_MODE)
	Objects.logger.templates.option_status("Shutdown after work", Objects.SHUTDOWN)
	Objects.logger.templates.header("PROCESSING")

#==========================================================================================#
# >>>>> ОБРАБОТКА КОММАНД <<<<< #
#==========================================================================================#

try: exec(f"com_{CommandDataStruct.name}(Objects, CommandDataStruct)")
except KeyboardInterrupt: exit(0)

#==========================================================================================#
# >>>>> ЗАВЕРШЕНИЕ РАБОТЫ <<<<< #
#==========================================================================================#

Objects.logger.close()

if Objects.SHUTDOWN:
	print("Shutdowning...")
	Shutdown()

exit(Objects.EXIT_CODE)