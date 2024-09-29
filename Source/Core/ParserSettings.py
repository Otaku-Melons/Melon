from Source.Core.SystemObjects.Logger import Logger
from Source.Core.Exceptions import BadSettings

from dublib.Methods.Filesystem import NormalizePath
from dublib.Methods.JSON import ReadJSON
from dublib.Methods.Data import Zerotify

import os

#==========================================================================================#
# >>>>> КАТЕГОРИИ НАСТРОЕК <<<<< #
#==========================================================================================#

class Common:
	"""Базовые настройки."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def archives_directory(self) -> str:
		"""Директория читаемого контента."""

		return NormalizePath(self.__Settings["archives_directory"])
	
	@property
	def bad_image_stub(self) -> str | None:
		"""Путь к заглушке плохого изображения."""

		return NormalizePath(self.__Settings["bad_image_stub"]) if self.__Settings["bad_image_stub"] else None
	
	@property
	def covers_directory(self) -> str:
		"""Директория обложек."""

		return NormalizePath(self.__Settings["covers_directory"])
	
	@property
	def titles_directory(self) -> str:
		"""Директория описательных файлов."""

		return NormalizePath(self.__Settings["titles_directory"])
	
	@property
	def use_id_as_filename(self) -> bool:
		"""Указывает, нужно ли использовать ID в качестве имени описательного файла."""

		return self.__Settings["use_id_as_filename"]
	
	@property
	def sizing_images(self) -> bool:
		"""Указывает, нужно ли пытаться определить размер изображений."""

		return self.__Settings["sizing_images"]
	
	@property
	def legacy(self) -> bool:
		"""Указывает, нужно ли использовать устаревший формат для описания тайтла."""

		return self.__Settings["legacy"]
	
	@property
	def pretty(self) -> bool:
		"""Состояние: включено ли улучшение качества контента."""

		return self.__Settings["pretty"]
	
	@property
	def retries(self) -> int:
		"""Количество повторов запроса при неудачном выполнении."""

		return self.__Settings["retries"]
	
	@property
	def delay(self) -> float:
		"""Интервал ожидания между последовательными запросами."""

		return self.__Settings["delay"]

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __PutDefaultDirectories(self, parser_name: str):
		"""
		Подстанавливает стандартные директории на пустые места.
			parser_name – название парсера.
		"""

		# Если директория архивов не установлена.
		if not self.__Settings["archives_directory"]:
			# Установка директории.
			self.__Settings["archives_directory"] = f"Output/{parser_name}/archives"
			# Если директория не существует, создать её.
			if not os.path.exists(f"Output/{parser_name}/archives"): os.makedirs(f"Output/{parser_name}/archives")

		# Если директория обложек не установлена.
		if not self.__Settings["covers_directory"]:
			# Установка директории.
			self.__Settings["covers_directory"] = f"Output/{parser_name}/covers"
			# Если директория не существует, создать её.
			if not os.path.exists(f"Output/{parser_name}/covers"): os.makedirs(f"Output/{parser_name}/covers")

		# Если директория тайтлов не установлена.
		if not self.__Settings["titles_directory"]:
			# Установка директории.
			self.__Settings["titles_directory"] = f"Output/{parser_name}/titles"
			# Если директория не существует, создать её.
			if not os.path.exists(f"Output/{parser_name}/titles"): os.makedirs(f"Output/{parser_name}/titles")

	def __init__(self, parser_name: str, settings: dict, logger: Logger):
		"""
		Базовые настройки.
			parser_name – название парсера;\n
			settings – словарь настроек;\n
			logger – менеджер логов.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Настройки.
		self.__Settings = {
			"archives_directory": "",
			"covers_directory": "",
			"titles_directory": "",
			"bad_image_stub": None,
			"pretty": False,
			"use_id_as_filename": False,
			"sizing_images": False,
			"legacy": False,
			"retries": 0,
			"delay": 1.0
		}

		# Если общие настройки определены.
		if "common" in settings.keys():
			# Если определён интервал, конвертировать его в число с плавающей запятой.
			if "delay" in settings["common"].keys(): settings["common"]["delay"] = float(settings["common"]["delay"])
			
			# Для каждой настройки.
			for Key in self.__Settings.keys():
				# Если настройка определена, записать её.
				if Key in settings["common"].keys(): self.__Settings[Key] = settings["common"][Key]
				else: logger.warning(f"Setting \"{Key}\" has been reset to default.")

			if self.__Settings["bad_image_stub"]:
				BadImageStub = NormalizePath(self.__Settings["bad_image_stub"])
				if not os.path.exists(BadImageStub): self.__Settings["bad_image_stub"] = None
				else: self.__Settings["bad_image_stub"] = BadImageStub

			# Подстановка стандартных директорий.
			self.__PutDefaultDirectories(parser_name)

		else: raise BadSettings(parser_name)

class Proxy:
	"""Настройки прокси."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def enable(self) -> bool:
		"""Указывает, нужно ли использовать прокси."""

		return self.__Settings["enable"]
	
	@property
	def host(self) -> str:
		"""Хост."""

		return self.__Settings["host"]
	
	@property
	def port(self) -> int:
		"""Порт."""

		return self.__Settings["port"]
	
	@property
	def login(self) -> str | None:
		"""Логин для авторизации прокси."""

		return Zerotify(self.__Settings["login"])
	
	@property
	def password(self) -> str | None:
		"""Пароль для авторизации прокси."""

		return Zerotify(self.__Settings["password"])

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, settings: dict, logger: Logger):
		"""
		Настройки прокси.
			settings – словарь настроек;\n
			logger – менеджер логов.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Настройки.
		self.__Settings = {
			"enable": False,
			"host": "",
			"port": 0,
			"login": "",
			"password": ""
		}

		# Если настройки прокси определены.
		if "proxy" in settings.keys():
			# Если определён порт, конвертировать его в число.
			if "port" in settings["proxy"].keys(): settings["proxy"]["port"] = int(settings["proxy"]["port"]) if settings["proxy"]["port"] else 0

			# Для каждой настройки.
			for Key in self.__Settings.keys():
				# Если настройка определена и она нужного типа, записать её.
				if Key in settings["proxy"].keys() and type(self.__Settings[Key]) == type(settings["proxy"][Key]): self.__Settings[Key] = settings["proxy"][Key]
				else: logger.warning(f"Proxy setting \"{Key}\" has been reset to default.")

class Custom:
	"""Собственные настройки парсера."""

	def __init__(self, settings: dict, logger: Logger):
		"""
		Настройки прокси.
			settings – словарь настроек;\n
			logger – менеджер логов.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Настройки.
		self.__Settings = settings["custom"] if "custom" in settings.keys() else dict()
		# Менеджер логов.
		self.__Logger = logger

	def __getitem__(self, key: str) -> any:
		"""
		Возвращает значение настройки.
			key – ключ настройки.
		"""

		# Если ключ не найден, отправить в лог предупреждение.
		if key not in self.__Settings.keys(): self.__Logger.warning(f"No custom setting: \"{key}\".")
		
		return self.__Settings[key]

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class ParserSettings:
	"""Настройки парсера."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def common(self) -> Common:
		"""Базовые настройки."""

		return self.__Common
	
	@property
	def custom(self) -> Custom:
		"""Собственные настройки парсера."""

		return self.__Custom
	
	@property
	def proxy(self) -> Proxy:
		"""Данные прокси."""

		return self.__Proxy
	
	@property
	def type(self) -> str:
		"""Тип настроек."""

		return self.__Type

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, parser_name: str, logger: Logger):
		"""
		Настройки парсера.
			parser_name – название парсера.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Настройки.
		self.__Settings = ReadJSON(f"Parsers/{parser_name}/settings.json")
		# Менеджер логов.
		self.__Logger = logger
		# Тип настроек.
		self.__Type = self.__Settings["type"]
		# Контейнеры категорий настроек.
		self.__Common = Common(parser_name, self.__Settings, logger)
		self.__Proxy = Proxy(self.__Settings, logger)
		self.__Custom = Custom(self.__Settings, logger)

	def __getitem__(self, category: str) -> dict:
		"""
		Возвращает словарь категории настроек.
			category – название категории.
		"""

		# Если категория не найдена, отправить в лог предупреждение.
		if category not in self.__Settings.keys(): self.__Logger.warning(f"No settings category: \"{category}\".")
		
		return self.__Settings[category].copy()