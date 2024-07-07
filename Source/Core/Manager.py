from dublib.Methods.JSON import ReadJSON

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
			# Выброс исключения.
			raise Exception(f"No parser \"{parser_name}\".")

	def __PutDefaultDirectories(self, settings: dict, parser_name: str):
		"""
		Подстанавливает стандартные директории на пустые места.
			settings – словарь настроек;
			parser_name – название парсера.
		"""

		# Если директория архивов не установлена.
		if not settings["common"]["archives_directory"]:
			# Установка директории.
			settings["common"]["archives_directory"] = f"Output/{parser_name}/archives"
			# Если директория не существует, создать её.
			if not os.path.exists(f"Output/{parser_name}/archives"): os.makedirs(f"Output/{parser_name}/archives")

		# Если директория обложек не установлена.
		if not settings["common"]["covers_directory"]:
			# Установка директории.
			settings["common"]["covers_directory"] = f"Output/{parser_name}/covers"
			# Если директория не существует, создать её.
			if not os.path.exists(f"Output/{parser_name}/covers"): os.makedirs(f"Output/{parser_name}/covers")

		# Если директория тайтлов не установлена.
		if not settings["common"]["titles_directory"]:
			# Установка директории.
			settings["common"]["titles_directory"] = f"Output/{parser_name}/titles"
			# Если директория не существует, создать её.
			if not os.path.exists(f"Output/{parser_name}/titles"): os.makedirs(f"Output/{parser_name}/titles")

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
		Parser = Module.Parser(self.__SystemObjects)
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
		Parser = Module.Parser(self.__SystemObjects)
		# Состояние: доступен ли метод.
		IsImplemented = True

		try:
			# Проверка существования метода.
			Parser.collect

		except AttributeError:
			# Переключение состояния.
			IsImplemented = False

		return IsImplemented

	def check_method_get_updates(self, parser_name: str) -> bool:
		"""
		Проверяет, доступна ли в парсере имплементация метода get_updates.
			parser_name – название парсера.
		"""

		# Проверка наличия парсера.
		self.__CheckParser(parser_name)
		# Инициализация парсера.
		Module = importlib.import_module(f"Parsers.{parser_name}.main")
		Parser = Module.Parser(self.__SystemObjects)
		# Состояние: доступен ли метод.
		IsImplemented = True

		try:
			# Проверка существования метода.
			Parser.get_updates

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
		Parser = Module.Parser(self.__SystemObjects)
		# Состояние: доступен ли метод.
		IsImplemented = True

		try:
			# Проверка существования метода.
			Parser.repair

		except AttributeError:
			# Переключение состояния.
			IsImplemented = False

		return IsImplemented

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ ПОЛУЧЕНИЯ ПАРАМЕТРОВ ПАРСЕРОВ <<<<< #
	#==========================================================================================#

	def get_parser_settings(self, parser_name: str) -> str:
		"""
		Возвращает словарь настроек парсера.
			parser_name – название парсера.
		"""

		# Проверка наличия парсера.
		self.__CheckParser(parser_name)
		# Чтение настроек.
		Settings = ReadJSON(f"Parsers/{parser_name}/settings.json")
		# Устанавливает стандартные директории.
		self.__PutDefaultDirectories(Settings, parser_name)

		return Settings

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