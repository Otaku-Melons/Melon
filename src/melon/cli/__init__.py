import importlib
import sys
from importlib import resources
from typing import TYPE_CHECKING, cast

from dublib.cli.terminalyzer import Command, ParsedCommandData, Terminalyzer

if TYPE_CHECKING:
	from ..core.system_objects import Printer, SystemObjects
	from .base_processor import BaseCommandProcessor

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

		CommandsPackage: str = f"{__package__}.commands"
		CommandModulesNames: list[str] = [
			file.name[:-3]
			for file in resources.files(CommandsPackage).iterdir()
			if file.name.endswith(".py")
		]

		return tuple(CommandModulesNames)
	
	def __LoadProcessors(self):
		"""Загружает обработчики команд."""

		self.__Processors.clear()
		self.__Commands.clear()

		for ProcessorModuleName in self.__GetCommandsModulesNames():
			Module = importlib.import_module(f"melon.cli.commands.{ProcessorModuleName}")
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