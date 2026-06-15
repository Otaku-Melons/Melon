# from Source.Core.Base.Builders.RanobeBuilder import RanobeBuilder
# from Source.Core.Base.Formats.Components import By, ContentTypes
# from Source.Core.Base.Builders.MangaBuilder import MangaBuilder
# from Source.Utils.Development import DevelopmeptAssistant
# from Source.Core.SystemObjects import SystemObjects
# from Source.Utils.Collector import Collector
# from Source.Utils.Installer import Installer
# from Source.Utils.Cacher import Cacher
# from Source import Utils
# from Source.Utils.Timer import Timer
# from Source.Core import Exceptions
# from Source.CLI.Legacy import Templates

# from dublib.CLI.TextStyler import FastStyler, GetStyledTextFromHTML
# from dublib.CLI.Templates.Bus import PrintError, PrintWarning
# from dublib.CLI.Terminalyzer import ParsedCommandData
# from dublib.Methods.Filesystem import WriteJSON
# from dublib.Engine.Bus import ExecutionResult

# from json.decoder import JSONDecodeError

# from time import sleep
# import traceback

from . import Templates

from Source.Core import Exceptions
from Source import Utils

from dublib.Methods.Filesystem import WriteJSON

from typing import TYPE_CHECKING
from pathlib import Path

import orjson

if TYPE_CHECKING:
	from Source.Core.SystemObjects import SystemObjects
	
	from dublib.CLI.Terminalyzer import ParsedCommandData

def com_classify(system_objects: "SystemObjects", command: "ParsedCommandData"):
	"""
	Кэширует пары ID-алиас для ускорения файловых операций.
		
	:param system_objects: Коллекция системных объектов.
	:type system_objects: SystemObjects
	:param command: Данные команды.
	:type command: ParsedCommandData
	"""

	#---> Парсинг параметров команды.
	#==========================================================================================#
	Target: str = command.get_position_value("VALUE", expected_type = str)
	IsOutputJSON: bool = command.check_flag("-j")
	FileToWrite: Path | None = command.get_key_value("--file", expected_type = Path)
	IgnoreCase: bool = command.check_flag("-i")

	#---> Выполнение команды.
	#==========================================================================================#
	ScriptPath: Path = Path("Configs/classificator.ini")

	if not ScriptPath.exists():
		system_objects.logger.critical(f"Script file \"{ScriptPath}\" doesn't exists.")
		return None
	
	ClassificatorObject = Utils.Classificator(ScriptPath)
	ExecutableLines = ClassificatorObject.read_script()
	ScriptValidationErrors = ClassificatorObject.validate_script(ExecutableLines)

	for ErrorData in ScriptValidationErrors:
		system_objects.logger.error(f"[{ErrorData.line.file.name}:{ErrorData.line.number}] {ErrorData.message}")

	if ScriptValidationErrors:
		system_objects.logger.critical("Script failure due to validation errors.")
		return None

	try:
		Procedures = ClassificatorObject.parse_procedures(ExecutableLines)
	except Exceptions.Utils.Classificator.ScriptRuntimeError as ExecutionData:
		system_objects.logger.critical(str(ExecutionData))
		return None
	
	ClassificationResult = ClassificatorObject.classify(Target, Procedures, ignore_case = IgnoreCase)

	if IsOutputJSON:
		print(orjson.dumps(ClassificationResult.to_dict()).decode())
	else:
		Templates.PrintClassificationResult(ClassificationResult, Target)

	if FileToWrite:
		WriteJSON(FileToWrite, ClassificationResult.to_dict())
		system_objects.logger.info(f"Classification result dumped in file: \"{FileToWrite}\".")