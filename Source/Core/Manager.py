from dublib.Methods import ReadJSON

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
		Проверяет
			parser_name – название парсера.
		"""

	def __PutDefaultDirectories(self, settings: dict):
		"""
		Подстанавливает стандартные директории на пустые места.
			settings – словарь настроек.
		"""

		# Если директория архивов не установлена.
		if not settings["common"]["archives_directory"]:
			# Установка директории.
			settings["common"]["archives_directory"] = "Output/hentailib/archives"
			# Если директория не существует, создать её.
			if not os.path.exists("Output/hentailib/archives"): os.makedirs("Output/hentailib/archives")

		# Если директория обложек не установлена.
		if not settings["common"]["covers_directory"]:
			# Установка директории.
			settings["common"]["covers_directory"] = "Output/hentailib/covers"
			# Если директория не существует, создать её.
			if not os.path.exists("Output/hentailib/covers"): os.makedirs("Output/hentailib/covers")

		# Если директория тайтлов не установлена.
		if not settings["common"]["titles_directory"]:
			# Установка директории.
			settings["common"]["titles_directory"] = "Output/hentailib/titles"
			# Если директория не существует, создать её.
			if not os.path.exists("Output/hentailib/titles"): os.makedirs("Output/hentailib/titles")

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Менеджер парсеров."""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# 
		pass

	def get_parser_settings(self, parser_name: str) -> str:
		"""
		Возвращает словарь настроек парсера.
			parser_name – название парсера.
		"""

		# Чтение настроек.
		Settings = ReadJSON(f"Parsers/{parser_name}/settings.json")
		# Устанавливает стандартные директории.
		self.__PutDefaultDirectories(Settings)

		return Settings

	def get_parser_site(self, parser_name: str) -> str:
		"""
		Возвращает поддерживаемый парсером сайт.
			parser_name – название парсера.
		"""

		# Импорт парсера.
		Module = importlib.import_module(f"Parsers.{parser_name}.main")

		return Module.SITE

	def get_parser_struct(self, parser_name: str) -> str:
		"""
		Возвращает объектную структуру выходных данных парсера.
			parser_name – название парсера.
		"""

		# Импорт парсера.
		Module = importlib.import_module(f"Parsers.{parser_name}.main")

		return Module.STRUCT

	def get_parser_version(self, parser_name: str) -> str:
		"""
		Возвращает версию парсера.
			parser_name – название парсера.
		"""

		# Импорт парсера.
		Module = importlib.import_module(f"Parsers.{parser_name}.main")

		return Module.VERSION

	def launch(self, parser_name: str, system_objects: "Objects") -> any:
		"""
		Запускает парсер и возвращает его объект.
			parser_name – название парсера;
			system_objects – коллекция системных объектов.
		"""

		# Объект парсера.
		Parser = None

		# Если парсер существует.
		if parser_name in self.parsers_names:
			# Инициализация парсера.
			Module = importlib.import_module(f"Parsers.{parser_name}.main")
			Parser = Module.Parser(system_objects)
			# Запись в лог информации: название и версия парсера.
			system_objects.logger.info(f"Parser: \"{Module.NAME}\" (version {Module.VERSION}).")

		else:
			# Запись в лог критической ошибки: нет такого парсера.
			system_objects.logger.critical(f"No parser \"{parser_name}\".")
			# Выброс исключения.
			raise Exception(f"No parser \"{parser_name}\".")

		return Parser