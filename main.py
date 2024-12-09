from Source.Core.SystemObjects import SystemObjects
from Source.CLI.Commands import *

from dublib.CLI.Terminalyzer import Command, ParametersTypes, Terminalyzer
from dublib.Methods.System import CheckPythonMinimalVersion, Shutdown
from dublib.Methods.Filesystem import MakeRootDirectories

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

CommandsList = list()

Com = Command("build", "Build readable content.")
ComPos = Com.create_position("FILENAME", "Source file.", important = True)
ComPos.add_argument(description = "Filename of locally saved title.")
ComPos = Com.create_position("PARSER", "Name of parser.", important = True)
ComPos.add_key("use", ParametersTypes.Text, "Parser name.")
Com.add_flag("cbz", "Make *.CBZ archives.")
CommandsList.append(Com)

Com = Command("collect", "Collect titles slugs into Collection.txt file.")
ComPos = Com.create_position("PARSER", "Name of parser.", important = True)
ComPos.add_key("use", ParametersTypes.Text, "Parser name.")
Com.add_flag("f", "Enable force mode.")
Com.add_flag("s", "Shutdown PC after script finish.")
Com.add_flag("local", "Scan local titles and put into collection.")
Com.add_flag("sort", "Enable slugs sorting.")
Com.add_key("filters", description = "Query string for filtering titles (supporting optional).")
Com.add_key("pages", ParametersTypes.Number, "Count of pages to collecting.")
Com.add_key("period", ParametersTypes.Number, "Period in hours for parsing updates.")

CommandsList.append(Com)

Com = Command("get", "Download image.")
ComPos = Com.create_position("URL", "Image source.")
ComPos.add_argument(ParametersTypes.URL, "Link to image.")
ComPos = Com.create_position("PARSER", "Name of parser.", important = True)
ComPos.add_key("use", ParametersTypes.Text, "Parser name.")
ComPos = Com.create_position("NAME", "Type of naming.")
ComPos.add_key("fullname", description = "Full name of file.")
ComPos.add_key("name", "Name of file without type.")
Com.add_flag("f", "Enable force mode.")
Com.add_flag("s", "Shutdown PC after script finish.")
Com.add_key("dir", ParametersTypes.ValidPath, "Output directory.")
CommandsList.append(Com)

Com = Command("install", "Install parsers.")
ComPos = Com.create_position("PARSER", "Name of parser.", important = True)
ComPos.add_argument(ParametersTypes.Text, "Name of parser.")
ComPos.add_flag("all", "Install all parsers.")
Com.add_flag("f", "Enable force mode.")
Com.add_flag("ssh", "Use SSH mode for repositories cloning.")
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
ComPos = Com.create_position("PARSER", "Name of parser.", important = True)
ComPos.add_key("use", ParametersTypes.Text, "Parser name.")
Com.add_key("period", ParametersTypes.Number, "Period in hours for parsing updates.")
Com.add_key("from", description = "Skip titles before this slug.")
Com.add_flag("f", "Enable force mode.")
Com.add_flag("s", "Shutdown PC after script finish.")
CommandsList.append(Com)

Com = Command("repair", "Repair chapter content in locally saved title.")
ComPos = Com.create_position("FILENAME", "Source file.", important = True)
ComPos.add_argument(description = "Filename of locally saved title.")
ComPos = Com.create_position("TARGET", "Target for repairing.", important = True)
ComPos.add_key("chapter", ParametersTypes.Number, "Chapter ID.")
ComPos = Com.create_position("PARSER", "Name of parser.", important = True)
ComPos.add_key("use", ParametersTypes.Text, "Parser name.")
Com.add_flag("s", "Shutdown PC after script finish.")
CommandsList.append(Com)

Com = Command("tagger", "Process titles classificators.")
ComPos = Com.create_position("INPUT", "Input data.", important = True)
ComPos.add_key("classificator", ParametersTypes.All, "Unknown type of classificator.")
ComPos.add_key("genre", ParametersTypes.All, "Genre.")
ComPos.add_key("franchise", ParametersTypes.All, "Franchise.")
ComPos.add_key("tag", ParametersTypes.All, "Tag.")
ComPos = Com.create_position("PARSER", "Parser name to determine source rules.")
ComPos.add_key("use", ParametersTypes.Text, "Parser name.")
ComPos = Com.create_position("OUTPUT", "Output mode.")
ComPos.add_flag("print", "Styled print in console (default).")
ComPos.add_flag("json", "Prints JSON-string in console.")
ComPos.add_key("file", description = "Path to dump JSON file.")
CommandsList.append(Com)

Com = Command("uninstall", "Uninstall parsers.")
ComPos = Com.create_position("PARSER", "Name of parser.", important = True)
ComPos.add_argument(ParametersTypes.Text, "Name of parser.")
ComPos.add_flag("all", "Uninstall all parsers.")
Com.add_flag("f", "Also remove configs.")
CommandsList.append(Com)

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

elif CommandDataStruct.name in ["help", "list", "tagger"]: Objects.LIVE_MODE = True

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