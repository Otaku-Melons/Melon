from Source.CLI.Templates import PrintOptionStatus
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
HIDE_HEADERS = False

if CommandData is None:
	Objects.logger.critical("Unknown command!")
	Objects.logger.set_rule(3)
	Objects.logger.close()
	exit()

elif CommandData.name in ("help", "list", "classify"): HIDE_HEADERS = True

if not HIDE_HEADERS:
	if CommandData.check_flag("-f"): Objects.FORCE_MODE.enable()
	if Objects.MELON_VERSION: print(f"Melon: {Objects.MELON_VERSION}")
	PrintOptionStatus("Force mode", Objects.FORCE_MODE.status)
	PrintOptionStatus("Caching", Objects.CACHING.status)
	Objects.logger.header(CommandData.name)

try:
	Objects.logger.select_cli_point(CommandData.name)

	# if CommandData.check_key("--use"): Objects.select_parser(CommandData.get_position_value("PARSER", expected_type = str))
	CommandName = CommandData.name.replace("-", "_")

	if CommandName != "help": exec(f"Commands.com_{CommandName}(Objects, CommandData)")
	
except KeyboardInterrupt: pass

#==========================================================================================#
# >>>>> ЗАВЕРШЕНИЕ РАБОТЫ <<<<< #
#==========================================================================================#

if not HIDE_HEADERS: Objects.logger.header("End")
Objects.logger.close()
exit(Objects.EXIT_CODE)