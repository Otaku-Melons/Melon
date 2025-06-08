from Source.Core.Base.Parser.Components.ParserSettings import ParserSettings
from Source.Core.SystemObjects.Logger import Portals
from Source.Core.SystemObjects import SystemObjects

from dublib.CLI.Terminalyzer import Command, ParsedCommandData, Terminalyzer
from dublib.WebRequestor import Protocols, WebConfig, WebLibs, WebRequestor
from dublib.Engine.Bus import ExecutionStatus

import shlex

#==========================================================================================#
# >>>>> ОПРЕДЕЛЕНИЯ <<<<< #
#==========================================================================================#

VERSION = None
NAME = None

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class BaseExtension:
	"""Базовое расширение."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def force_mode(self) -> bool:
		"""Состояние: включён ли глобальный режим перезаписи."""

		return self._SystemObjects.FORCE_MODE

	@property
	def parser_settings(self) -> ParserSettings:
		"""Настройки парсера."""

		return self._ParserSettings
	
	@property
	def portals(self) -> Portals:
		"""Настройки парсера."""

		return self._Portals

	@property
	def requestor(self) -> WebRequestor:
		"""Запросчик Web-контента."""

		return self._Requestor
	
	@property
	def settings(self) -> dict | None:
		"""Настройки расширения."""

		return self._Settings
	
	@property
	def system_objects(self) -> SystemObjects:
		"""Коллекция системных объектов."""

		return self._SystemObjects

	@property
	def temp(self) -> str:
		"""Путь к каталогу."""

		return self._Temper.get_extension_temp()

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GenerateCommandsList(self) -> list[Command]:
		"""Возвращает список описаний команд."""

		CommandsList = list()

		return CommandsList

	def _InitializeRequestor(self) -> WebRequestor:
		"""Инициализирует модуль WEB-запросов."""

		Config = WebConfig()
		Config.select_lib(WebLibs.requests)
		Config.set_retries_count(2)
		Config.generate_user_agent()
		Config.add_header("Referer", f"https://{self._SystemObjects.manager.parser_site}/")
		Config.requests.enable_proxy_protocol_switching(True)
		WebRequestorObject = WebRequestor(Config)
		
		if self._ParserSettings.proxy.enable: WebRequestorObject.add_proxy(
			Protocols.HTTPS,
			host = self._ParserSettings.proxy.host,
			port = self._ParserSettings.proxy.port,
			login = self._ParserSettings.proxy.login,
			password = self._ParserSettings.proxy.password
		)

		return WebRequestorObject

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

	def __init__(self, system_objects: SystemObjects):
		"""
		Базовое расширение.
			system_objects – коллекция системных объектов.
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self._SystemObjects = system_objects

		self._Temper = self._SystemObjects.temper
		self._Portals = self._SystemObjects.logger.portals
		self._ParserSettings = self._SystemObjects.manager.get_parser_settings()
		self._Settings = self._SystemObjects.manager.get_extension_settings()
		self._Requestor: WebRequestor = self._InitializeRequestor()

		self._PostInitMethod()

	def run(self, command: str | None) -> ExecutionStatus:
		"""
		Запускает расширение.
			command – передаваемая для обработки команда.
		"""

		Status = ExecutionStatus()

		if command: 
			command = shlex.split(command)
			Analyzer = Terminalyzer(command)
			Analyzer.helper.enable()
			ParsedCommand = Analyzer.check_commands(self._GenerateCommandsList())

			if not ParsedCommand:
				Status.push_error("Unknown command.")
				return Status

			self._ProcessCommand(ParsedCommand)

		else: Status.push_error("No command. Use \"--command\" key.")

		return Status