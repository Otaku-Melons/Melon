from Source.Core.SystemObjects import SystemObjects
from Source.CLI.Commands import *

from dublib.CLI.Terminalyzer import Command, ParametersTypes, Terminalyzer
from dublib.Methods.System import CheckPythonMinimalVersion, Shutdown

import sys

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ <<<<< #
#==========================================================================================#

CheckPythonMinimalVersion(3, 10)

Objects = SystemObjects()

Objects.logger.info("====== Preparing to starting ======")
Objects.logger.info(f"Starting with Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} on {sys.platform}.")
Objects.logger.info("Command: \"" + " ".join(sys.argv[1:len(sys.argv)]) + "\".")

#==========================================================================================#
# >>>>> НАСТРОЙКА ОБРАБОТЧИКА КОМАНД <<<<< #
#==========================================================================================#

CommandsList = list()

Com = Command("build", "Build readable content.")
ComPos = Com.create_position("FILENAME", "Source file.", important = True)
ComPos.add_argument(description = "Filename of locally saved title.")
ComPos = Com.create_position("PARSER", "Used parser.", important = True)
ComPos.add_key("use", ParametersTypes.Text, "Parser name.")
Com.add_flag("cbz", "Make *.CBZ archives.")
CommandsList.append(Com)

Com = Command("collect", "Collect titles slugs into Collection.txt file.")
ComPos = Com.create_position("PARSER", "Used parser.", important = True)
ComPos.add_key("use", ParametersTypes.Text, "Parser name.")
Com.add_flag("f", "Enable force mode.")
Com.add_flag("s", "Shutdown PC after script finish.")
Com.add_flag("sort", "Enable slugs sorting.")
Com.add_key("filters", description = "Query string for filtering titles (supporting optional).")
Com.add_key("pages", ParametersTypes.Number, "Count of pages to collecting.")
Com.add_key("period", ParametersTypes.Number, "Period in hours for parsing updates.")
CommandsList.append(Com)

Com = Command("get", "Download image.")
ComPos = Com.create_position("URL", "Image source.")
ComPos.add_argument(ParametersTypes.URL, "Link to image.")
ComPos = Com.create_position("PARSER", "Used parser.", important = True)
ComPos.add_key("use", ParametersTypes.Text, "Parser name.")
ComPos = Com.create_position("NAME", "Type of naming.")
ComPos.add_key("fullname", description = "Full name of file.")
ComPos.add_key("name", "Name of file without type.")
Com.add_flag("f", "Enable force mode.")
Com.add_flag("s", "Shutdown PC after script finish.")
Com.add_flag("sid", "Disable custom imege downloader.")
Com.add_key("dir", ParametersTypes.ValidPath, "Output directory.")
CommandsList.append(Com)

Com = Command("list", "Print list of installed parsers.")
Com.add_flag("s", "Shutdown PC after script finish.")
CommandsList.append(Com)

Com = Command("parse", "Start titles parsing.")
ComPos = Com.create_position("TARGET", "Target for parsing.", important = True)
ComPos.add_argument(description = "Title slug.")
ComPos.add_flag("collection", "Parse slugs from Collection.txt file.")
ComPos.add_flag("local", "Parse all locally saved titles.")
ComPos.add_flag("updates", "Parse titles updated for last 24 hours.")
ComPos = Com.create_position("PARSER", "Used parser.", important = True)
ComPos.add_key("use", ParametersTypes.Text, "Parser name.")
Com.add_key("period", ParametersTypes.Number, "Period in hours for parsing updates.")
Com.add_flag("f", "Enable force mode.")
Com.add_flag("s", "Shutdown PC after script finish.")
CommandsList.append(Com)

Com = Command("repair", "Repair chapter content in locally saved title.")
ComPos = Com.create_position("FILENAME", "Source file.", important = True)
ComPos.add_argument(description = "Filename of locally saved title.")
ComPos = Com.create_position("TARGET", "Target for repairing.", important = True)
ComPos.add_key("chapter", ParametersTypes.Number, "Chapter ID.")
ComPos = Com.create_position("PARSER", "Used parser.", important = True)
ComPos.add_key("use", ParametersTypes.Text, "Parser name.")
Com.add_flag("s", "Shutdown PC after script finish.")
CommandsList.append(Com)

Analyzer = Terminalyzer()
Analyzer.enable_help(True)
CommandDataStruct = Analyzer.check_commands(CommandsList)

if CommandDataStruct == None:
	Objects.logger.close(clean = True)
	print("Unknown command.")
	exit(0)

#==========================================================================================#
# >>>>> ОБРАБОТКА НЕСПЕЦИФИЧЕСКИХ ФЛАГОВ <<<<< #
#==========================================================================================#

if "f" in CommandDataStruct.flags:
	Objects.FORCE_MODE = True
	Objects.logger.info("Force mode: ON.")
	Objects.MSG_FORCE_MODE = "Force mode: ON\n"

if "s" in CommandDataStruct.flags:
	Objects.SHUTDOWN = True
	Objects.logger.info("Computer will be turned off after script is finished!")
	Objects.MSG_SHUTDOWN = "Computer will be turned off after script is finished!\n"

if CommandDataStruct.check_key("use"): Objects.PARSER_NAME = CommandDataStruct.get_key_value("use")

#==========================================================================================#
# >>>>> ОБРАБОТКА КОММАНД <<<<< #
#==========================================================================================#


if "build" == CommandDataStruct.name: com_build(Objects, CommandDataStruct)
if "collect" == CommandDataStruct.name: com_collect(Objects, CommandDataStruct)
if "get" == CommandDataStruct.name: com_get(Objects, CommandDataStruct)
if "list" == CommandDataStruct.name: com_list(Objects)
if "parse" == CommandDataStruct.name: com_parse(Objects, CommandDataStruct)
if "repair" == CommandDataStruct.name: com_repair(Objects, CommandDataStruct)

#==========================================================================================#
# >>>>> ЗАВЕРШЕНИЕ РАБОТЫ <<<<< #
#==========================================================================================#

if Objects.REMOVE_LOG: Objects.logger.close(clean = True)
else: Objects.logger.close()
if Objects.SHUTDOWN: Shutdown()