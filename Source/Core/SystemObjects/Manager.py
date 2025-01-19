from Source.Core.ParserSettings import ParserSettings

from dublib.Methods.Filesystem import ReadJSON
from dublib.CLI.TextStyler import TextStyler

from typing import Any

import subprocess
import importlib
import os

class Manager:
	"""Менеджер парсеров."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def all_parsers_names(self) -> list[str]:
		"""Список названий доступных парсеров."""

		Parsers = os.listdir("Parsers")
		if "Templates" in Parsers: Parsers.remove("Templates")

		return Parsers

	@property
	def extension_settings(self) -> ParserSettings:
		"""Настройки используемого расширения."""

		return self.get_extension_settings(cache = True)

	@property
	def parser_settings(self) -> ParserSettings:
		"""Настройки используемого парсера."""

		return self.get_parser_settings(cache = True)

	@property
	def parser_site(self) -> str:
		"""Название источника."""

		return self.get_parser_site()

	@property
	def parser_version(self) -> str:
		"""Версия используемого парсера."""

		return self.get_parser_version()

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CheckParser(self, parser: str | None) -> str:
		"""
		Проверяет наличие парсера.
			parser – название парсера.
		"""

		if not parser: parser = self.__Parser

		if parser != None and parser not in self.all_parsers_names:
			self.__SystemObjects.logger.critical(f"No parser \"{parser}\".")
			print(f"No parser: \"{parser}\".")
			exit(-1)

		return parser

	def __GetLegacyParserVersion(self, parser: str | None = None) -> str | None:
		"""
		Возвращает версию парсера из констант главного файла.
			parser – название парсера.
		"""

		Version = None
		try: Version = importlib.import_module(f"Parsers.{parser}.main").VERSION
		except AttributeError: pass

		return Version

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: "SystemObjects"):
		"""
		Менеджер парсеров.
			system_objects – коллекция системных объектов.
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__SystemObjects = system_objects

		self.__ExtensionSettings = None
		self.__ParserSettings = None
		self.__Extension = None
		self.__Parser = None

	def launch(self, parser: str | None = None) -> Any:
		"""
		Запускает парсер и возвращает его объект.
			parser – название парсера.
		"""

		parser = self.__CheckParser(parser)
		Module = importlib.import_module(f"Parsers.{parser}.main")
		Parser = Module.Parser(self.__SystemObjects)

		ParserName = TextStyler(parser).decorate.bold
		Text = f"Parser: {ParserName} (version {Module.VERSION})."
		self.__SystemObjects.logger.info(Text, stdout = True)

		return Parser

	def launch_extension(self, parser: str, extension: str) -> any:
		"""
		Запускает парсер и возвращает его объект.
			parser – название парсера.
		"""

		parser = self.__CheckParser(parser)
		Module = importlib.import_module(f"Parsers.{parser}.extensions.{extension}.main")
		Extension = Module.Extension(self.__SystemObjects)

		ParserName = TextStyler(parser).decorate.bold
		ExtensionName = TextStyler(extension).decorate.bold
		self.__SystemObjects.logger.info(f"Parser: {ParserName} (version {self.parser_version}).", stdout = True)
		self.__SystemObjects.logger.info(f"Running extension: {ExtensionName}...", stdout = True)

		return Extension

	def select_extension(self, extension: str):
		"""Задаёт имя используемого расширения."""

		self.__Extension = extension

	def select_parser(self, parser: str):
		"""Задаёт имя используемого парсера."""

		self.__Parser = parser

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ ПРОВЕРКИ ИМПЛЕМЕНТАЦИЙ ПАРСЕРОВ <<<<< #
	#==========================================================================================#

	def check_method_collect(self, parser: str | None = None) -> bool | None:
		"""
		Проверяет, доступна ли в парсере имплементация метода collect.
			parser – название парсера.
		"""
		
		parser = self.__CheckParser(parser)
		Module = importlib.import_module(f"Parsers.{parser}.main")
		Parser = Module.Parser
		IsImplemented = True

		try: Parser.collect
		except AttributeError: IsImplemented = False
		except: IsImplemented = None

		return IsImplemented

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ ПОЛУЧЕНИЯ ПАРАМЕТРОВ РАСШИРЕНИЙ <<<<< #
	#==========================================================================================#

	def get_extension_settings(self, parser: str | None = None, extension: str | None = None, cache: bool = False) -> dict | None:
		"""
		Возвращает словарь настроек расширения.
			parser – имя парсера;\n
			extension – имя расширения;\n
			cache – указывает, использовать ли кэшированные настройки.
		"""

		if not parser: parser = self.__Parser
		if not extension: extension = self.__Extension
		parser = self.__CheckParser(parser)

		if cache and self.__ExtensionSettings and parser == self.__SystemObjects.parser_name and extension == self.__SystemObjects.extension_name: return self.__ExtensionSettings

		if not self.__ExtensionSettings:
			try: self.__ExtensionSettings = ReadJSON(f"Configs/{parser}/extensions/{extension}.json")
			except FileNotFoundError: pass

			if not self.__ExtensionSettings:

				try: 
					self.__ExtensionSettings = ReadJSON(f"Parsers/{parser}/extensions/{extension}/settings.json")
					self.__SystemObjects.logger.warning("Using extension settings from repository.", stdout = True)

				except FileNotFoundError: pass

		return self.__ExtensionSettings

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ ПОЛУЧЕНИЯ ПАРАМЕТРОВ ПАРСЕРОВ <<<<< #
	#==========================================================================================#

	def get_parser_settings(self, parser: str | None = None, cache: bool = False) -> ParserSettings:
		"""
		Возвращает контейнер настроек парсера.
			parser – название парсера;\n
			cache – указывает, использовать ли кэшированные настройки.
		"""

		parser = self.__CheckParser(parser)
		if cache and self.__ParserSettings and parser == self.__SystemObjects.parser_name: return self.__ParserSettings
		self.__ParserSettings = ParserSettings(parser, self.__SystemObjects.logger)

		return self.__ParserSettings

	def get_parser_site(self, parser: str | None = None) -> str:
		"""
		Возвращает поддерживаемый парсером сайт.
			parser – название парсера.
		"""

		parser = self.__CheckParser(parser)
		Module = importlib.import_module(f"Parsers.{parser}.main")
		importlib.reload(Module)

		return Module.SITE

	def get_parser_type(self, parser: str | None = None) -> str:
		"""
		Возвращает тип контента парсера.
			parser – название парсера.
		"""

		parser = self.__CheckParser(parser)
		Module = importlib.import_module(f"Parsers.{parser}.main")

		return Module.TYPE
	
	def get_parser_type_name(self, parser: str | None = None) -> str:
		"""
		Возвращает название типа контента парсера.
			parser – название парсера.
		"""

		parser = self.__CheckParser(parser)
		Module = importlib.import_module(f"Parsers.{parser}.main")

		return Module.TYPE.__name__.lower()

	def get_parser_version(self, parser: str | None = None) -> str:
		"""
		Возвращает версию парсера.
			parser – название парсера.
		"""

		parser = self.__CheckParser(parser)
		Version = subprocess.getoutput(f"cd Parsers/{parser} && git describe --tags $(git rev-list --tags --max-count=1)")
		
		if Version.startswith("fatal"): Version = self.__GetLegacyParserVersion(parser)
		if Version.startswith("v"): Version = Version.lstrip("v")

		return Version