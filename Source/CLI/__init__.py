import importlib
import sys
from typing import TYPE_CHECKING, cast

from dublib.CLI.Terminalyzer import Command, ParsedCommandData, Terminalyzer
from dublib.Functions.Filesystem import ListDir

if TYPE_CHECKING:
	from Source.Core.SystemObjects import Printer, SystemObjects

	from .BaseProcessor import BaseCommandProcessor

class CommandsOrchestrator:
	"""Оркестратор команд."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	@property
	def printer(self) -> "Printer":
		"""Оператор вывода."""

		return self.__SystemObjects.printer

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GetCommandsModulesNames(self) -> tuple[str, ...]:
		"""
		Получает список имён доступных модулей обработки команд.

		:return: Последовательность имён доступных модулей обработки команд.
		:rtype: tuple[str, ...]
		"""

		ProcessorsFiles: list[str] = ListDir("Source/CLI/Commands")

		if "__pycache__" in ProcessorsFiles:
			ProcessorsFiles.remove("__pycache__")

		for Index in range(len(ProcessorsFiles)):
			Buffer: str = ProcessorsFiles[Index]
			Buffer = Buffer[:-3]
			ProcessorsFiles[Index] = Buffer

		return tuple(ProcessorsFiles)

	def __LoadProcessors(self):
		"""Загружает обработчики команд."""

		self.__Processors.clear()
		self.__Commands.clear()

		for ProcessorModuleName in self.__GetCommandsModulesNames():
			Module = importlib.import_module(f"Source.CLI.Commands.{ProcessorModuleName}")
			Processor = cast("BaseCommandProcessor", Module.CommandProcessor(self.__SystemObjects))
			CommandData = Processor.command
			
			self.__Processors[CommandData.name] = Processor
			self.__Commands.append(CommandData)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: "SystemObjects"):
		"""
		Базовый обработчик команды.

		:param system_objects: Коллекция системных объектов.
		:type system_objects: SystemObjects
		"""

		self.__SystemObjects: "SystemObjects" = system_objects

		self.__Processors: "dict[str, BaseCommandProcessor]" = {}
		self.__Commands: list[Command] = []

		self.__LoadProcessors()

		self.__IgnoredCommandsNames: tuple[str, ...] = ("help",)
		
		self.__Terminanalyzer = Terminalyzer()
		self.__Terminanalyzer.helper.enable()

	def run(self):
		"""Запускает разовую проверку команды из аргументов скрипта."""

		self.__Terminanalyzer.set_input(None)
		CommandData: ParsedCommandData | None = self.__Terminanalyzer.check_commands(self.__Commands)

		if CommandData is None:
			self.printer.critical("Unknown command!")
			sys.exit(1)

		if CommandData.name in self.__IgnoredCommandsNames:
			return

		self.__Processors[CommandData.name].process(CommandData)