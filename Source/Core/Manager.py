from Source.Core.ParserSettings import ParserSettings

import importlib
import os

class Manager:
	"""Менеджер парсеров."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТОЛЬКО ДЛЯ ЧТЕНИЯ <<<<< #
	#==========================================================================================#

	@property
	def parsers_names(self) -> list[str]:
		"""Список названий доступных парсеров."""

		# Получение списка каталогов в директории парсеров.
		Parsers = os.listdir("Parsers")
		# Удаление директории шаблонов.
		if "Templates" in Parsers: Parsers.remove("Templates")

		return Parsers

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CheckParser(self, parser_name: str):
		"""
		Проверяет наличие парсера.
			parser_name – название парсера.
		"""

		# Если парсер не существует.
		if parser_name not in self.parsers_names:
			# Запись в лог критической ошибки: нет такого парсера.
			self.__SystemObjects.logger.critical(f"No parser \"{parser_name}\".")
			# Вывод в консоль: парсер не найден.
			print(f"No parser: \"{parser_name}\".")
			# Завершение работы.
			exit(-1)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: "Objects"):
		"""
		Менеджер парсеров.
			system_objects – коллекция системных объектов.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Коллекция системных объектов.
		self.__SystemObjects = system_objects
		# Настройки парсера.
		self.__ParserSettings = None

	def launch(self, parser_name: str) -> any:
		"""
		Запускает парсер и возвращает его объект.
			parser_name – название парсера.
		"""

		# Проверка наличия парсера.
		self.__CheckParser(parser_name)
		# Очистка временных файлов парсера.
		self.__SystemObjects.temper.clear_parser_temp(parser_name)
		# Инициализация парсера.
		Module = importlib.import_module(f"Parsers.{parser_name}.main")
		Parser = Module.Parser(self.__SystemObjects, self.get_parser_settings(parser_name))
		# Запись в лог информации: название и версия парсера.
		self.__SystemObjects.logger.info(f"Parser: \"{Module.NAME}\" (version {Module.VERSION}).")

		return Parser

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ ПРОВЕРКИ ИМПЛЕМЕНТАЦИЙ ПАРСЕРОВ <<<<< #
	#==========================================================================================#

	def check_method_collect(self, parser_name: str) -> bool:
		"""
		Проверяет, доступна ли в парсере имплементация метода collect.
			parser_name – название парсера.
		"""

		# Проверка наличия парсера.
		self.__CheckParser(parser_name)
		# Инициализация парсера.
		Module = importlib.import_module(f"Parsers.{parser_name}.main")
		Parser = Module.Parser(self.__SystemObjects, self.get_parser_settings(parser_name))
		# Состояние: доступен ли метод.
		IsImplemented = True

		try:
			# Проверка существования метода.
			Parser.collect

		except AttributeError:
			# Переключение состояния.
			IsImplemented = False

		return IsImplemented

	def check_method_image(self, parser_name: str) -> bool:
		"""
		Проверяет, доступна ли в парсере имплементация метода image.
			parser_name – название парсера.
		"""

		# Проверка наличия парсера.
		self.__CheckParser(parser_name)
		# Инициализация парсера.
		Module = importlib.import_module(f"Parsers.{parser_name}.main")
		Parser = Module.Parser(self.__SystemObjects, self.get_parser_settings(parser_name))
		# Состояние: доступен ли метод.
		IsImplemented = True

		try:
			# Проверка существования метода.
			Parser.image

		except AttributeError:
			# Переключение состояния.
			IsImplemented = False

		return IsImplemented

	def check_method_repair(self, parser_name: str) -> bool:
		"""
		Проверяет, доступна ли в парсере имплементация метода repair.
			parser_name – название парсера.
		"""

		# Проверка наличия парсера.
		self.__CheckParser(parser_name)
		# Инициализация парсера.
		Module = importlib.import_module(f"Parsers.{parser_name}.main")
		Parser = Module.Parser(self.__SystemObjects, self.get_parser_settings(parser_name))
		# Состояние: доступен ли метод.
		IsImplemented = True

		try:
			# Проверка существования метода.
			Parser.repair

		except AttributeError:
			# Переключение состояния.
			IsImplemented = False

		return IsImplemented

	def check_method_updates(self, parser_name: str) -> bool:
		"""
		Проверяет, доступна ли в парсере имплементация метода updates.
			parser_name – название парсера.
		"""

		# Проверка наличия парсера.
		self.__CheckParser(parser_name)
		# Инициализация парсера.
		Module = importlib.import_module(f"Parsers.{parser_name}.main")
		Parser = Module.Parser(self.__SystemObjects, self.get_parser_settings(parser_name))
		# Состояние: доступен ли метод.
		IsImplemented = True

		try:
			# Проверка существования метода.
			Parser.updates

		except AttributeError:
			# Переключение состояния.
			IsImplemented = False

		return IsImplemented
	
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ ПОЛУЧЕНИЯ ПАРАМЕТРОВ ПАРСЕРОВ <<<<< #
	#==========================================================================================#

	def get_parser_settings(self, parser_name: str) -> ParserSettings:
		"""
		Возвращает контейнер настроек парсера.
			parser_name – название парсера.
		"""

		# Проверка наличия парсера.
		self.__CheckParser(parser_name)
		# Если настройки не прочитаны, прочитать.
		if not self.__ParserSettings: self.__ParserSettings = ParserSettings(parser_name, self.__SystemObjects.logger)

		return self.__ParserSettings

	def get_parser_site(self, parser_name: str) -> str:
		"""
		Возвращает поддерживаемый парсером сайт.
			parser_name – название парсера.
		"""

		# Проверка наличия парсера.
		self.__CheckParser(parser_name)
		# Импорт парсера.
		Module = importlib.import_module(f"Parsers.{parser_name}.main")
		# Перезагрузка модуля (сбрасывает переопределённые переменные).
		importlib.reload(Module)

		return Module.SITE

	def get_parser_struct(self, parser_name: str) -> str:
		"""
		Возвращает объектную структуру выходных данных парсера.
			parser_name – название парсера.
		"""

		# Проверка наличия парсера.
		self.__CheckParser(parser_name)
		# Импорт парсера.
		Module = importlib.import_module(f"Parsers.{parser_name}.main")

		return Module.STRUCT

	def get_parser_version(self, parser_name: str) -> str:
		"""
		Возвращает версию парсера.
			parser_name – название парсера.
		"""

		# Проверка наличия парсера.
		self.__CheckParser(parser_name)
		# Импорт парсера.
		Module = importlib.import_module(f"Parsers.{parser_name}.main")

		return Module.VERSION