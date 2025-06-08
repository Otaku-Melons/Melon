from Source.Core.Exceptions import ParsingError, TitleNotFound
from Source.Core.Base.Extension.BaseExtension import BaseExtension

from ...main import NAME as PARSER_NAME
from ...main import TYPE as PARSER_TYPE
from ...main import SITE

from dublib.CLI.Terminalyzer import Command, ParsedCommandData
from dublib.Engine.Bus import ExecutionStatus

#==========================================================================================#
# >>>>> ОПРЕДЕЛЕНИЯ <<<<< #
#==========================================================================================#

VERSION = None
NAME = None

#==========================================================================================#
# >>>>> РАСШИРЕНИЕ <<<<< #
#==========================================================================================#

class Extension(BaseExtension):

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GenerateCommandsList(self) -> list[Command]:
		"""Возвращает список описаний команд."""

		CommandsList = list()

		pass

		return CommandsList

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	def _ProcessCommand(self, command: ParsedCommandData):
		"""
		Вызывается для обработки переданной расширению команды.
			command – данные команды.
		"""

		pass

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	