from Source.Core.ParserSettings import ParserSettings

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
	def parser_settings(self) -> ParserSettings:
		"""Настройки используемого парсера."""

		return self.get()

	@property
	def parser_settings(self) -> ParserSettings:
		"""Настройки используемого парсера."""

		return self.get_parser_settings()

	@property
	def parser_version(self) -> str:
		"""Версия используемого парсера."""

		return self.get_parser_version()

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CheckParser(self, parser_name: str | None) -> str:
		"""
		Проверяет наличие парсера.
			parser_name – название парсера.
		"""

		if not parser_name: parser_name = self.__ParserName

		if parser_name != None and parser_name not in self.all_parsers_names:
			self.__SystemObjects.logger.critical(f"No parser \"{parser_name}\".")
			print(f"No parser: \"{parser_name}\".")
			exit(-1)

		return parser_name

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: "SystemObjects"):
		"""
		Менеджер парсеров.
			system_objects – коллекция системных объектов.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__SystemObjects = system_objects
		self.__ParserSettings = None
		self.__ParserName = None

	def launch(self, parser_name: str | None = None) -> any:
		"""
		Запускает парсер и возвращает его объект.
			parser_name – название парсера.
		"""

		parser_name = self.__CheckParser(parser_name)
		Module = importlib.import_module(f"Parsers.{parser_name}.main")
		Parser = Module.Parser(self.__SystemObjects)

		Text = f"Parser: \"{Module.NAME}\" (version {Module.VERSION})."
		self.__SystemObjects.logger.info(Text)
		# print(Text)

		return Parser

	def select_parser(self, parser_name: str):
		"""Задаёт имя используемого парсера."""

		self.__ParserName = parser_name

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ ПРОВЕРКИ ИМПЛЕМЕНТАЦИЙ ПАРСЕРОВ <<<<< #
	#==========================================================================================#

	def check_method_collect(self, parser_name: str | None = None) -> bool | None:
		"""
		Проверяет, доступна ли в парсере имплементация метода collect.
			parser_name – название парсера.
		"""
		
		parser_name = self.__CheckParser(parser_name)
		Module = importlib.import_module(f"Parsers.{parser_name}.main")
		Parser = Module.Parser(self.__SystemObjects, self.get_parser_settings(parser_name))
		IsImplemented = True

		try: Parser.collect
		except AttributeError: IsImplemented = False
		except: IsImplemented = None

		return IsImplemented

	def check_method_image(self, parser_name: str | None = None) -> bool:
		"""
		Проверяет, доступна ли в парсере имплементация метода image.
			parser_name – название парсера.
		"""

		parser_name = self.__CheckParser(parser_name)
		Module = importlib.import_module(f"Parsers.{parser_name}.main")
		Parser = Module.Parser(self.__SystemObjects, self.get_parser_settings(parser_name))
		IsImplemented = True

		try: Parser.image
		except AttributeError: IsImplemented = False
		except: IsImplemented = None

		return IsImplemented
	
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ ПОЛУЧЕНИЯ ПАРАМЕТРОВ ПАРСЕРОВ <<<<< #
	#==========================================================================================#

	def get_parser_settings(self, parser_name: str | None = None) -> ParserSettings:
		"""
		Возвращает контейнер настроек парсера.
			parser_name – название парсера.
		"""

		parser_name = self.__CheckParser(parser_name)
		if not self.__ParserSettings: self.__ParserSettings = ParserSettings(parser_name, self.__SystemObjects.logger)

		return self.__ParserSettings

	def get_parser_site(self, parser_name: str | None = None) -> str:
		"""
		Возвращает поддерживаемый парсером сайт.
			parser_name – название парсера.
		"""

		parser_name = self.__CheckParser(parser_name)
		Module = importlib.import_module(f"Parsers.{parser_name}.main")
		importlib.reload(Module)

		return Module.SITE

	def get_parser_type(self, parser_name: str | None = None) -> str:
		"""
		Возвращает тип контента парсера.
			parser_name – название парсера.
		"""

		parser_name = self.__CheckParser(parser_name)
		Module = importlib.import_module(f"Parsers.{parser_name}.main")

		return Module.TYPE
	
	def get_parser_type_name(self, parser_name: str | None = None) -> str:
		"""
		Возвращает название типа контента парсера.
			parser_name – название парсера.
		"""

		parser_name = self.__CheckParser(parser_name)
		Module = importlib.import_module(f"Parsers.{parser_name}.main")

		return Module.TYPE.__name__.lower()

	def get_parser_version(self, parser_name: str | None = None) -> str:
		"""
		Возвращает версию парсера.
			parser_name – название парсера.
		"""

		parser_name = self.__CheckParser(parser_name)
		Module = importlib.import_module(f"Parsers.{parser_name}.main")

		return Module.VERSION