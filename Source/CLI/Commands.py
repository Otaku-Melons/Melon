from . import Templates

from Source.Core.Base.Formats.Components.Enums import ContentTypes
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

def com_list(system_objects: "SystemObjects", command: "ParsedCommandData"):
	"""
	Выводит список парсеров.
		
	:param system_objects: Коллекция системных объектов.
	:type system_objects: SystemObjects
	:param command: Данные команды.
	:type command: ParsedCommandData
	"""

	TableData: dict[str, list[str]] = {
		"NAME": [],
		"VERSION": [],
		"TYPES": [],
		"SITE": [],
		"collect": []
	}

	for ParserName in system_objects.driver.parsers_names:
		EntryPoint = system_objects.driver.get_entry_point(ParserName)
		TypesEmoji = {
			ContentTypes.Anime: "a",
			ContentTypes.Manga: "m",
			ContentTypes.Ranobe: "r"
		}

		ParserVersion = EntryPoint.version or ""
		ParserContentTypes: list[str] = [TypesEmoji[CurrentType] for CurrentType in EntryPoint.manifest.content_types]
		ParserSite: str = "https://" + EntryPoint.manifest.site

		TableData["NAME"].append(ParserName)
		TableData["VERSION"].append(ParserVersion)
		TableData["TYPES"].append(", ".join(ParserContentTypes))
		TableData["SITE"].append(ParserSite)
		TableData["collect"].append(str(EntryPoint.is_supported_collect))

	Templates.PrintParsersTable(TableData)