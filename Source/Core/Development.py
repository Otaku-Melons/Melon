from Source.Core.SystemObjects import SystemObjects
from Source.Core.Base.Parsers.Components.Settings import Settings
from Source.Core.Base.Formats.Components.Structs import ContentTypes
from Source.Core.Timer import Timer

from dublib.Methods.Filesystem import WriteJSON
from dublib.CLI.TextStyler import TextStyler
from dublib.Engine.Patcher import Patch

import shutil
import os

class DevelopmeptAssistant:
	"""Помощник разработчика."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CheckExtensionName(self, name: str) -> bool:
		"""
		Проверяет валидность имени расширения.
			name – имя расширения.
		"""

		if name.count(".") != 1:
			self.__Logger.error("Extension name must have a format \"{PARSER}.{EXTENSION}\".", stdout = True)
			return False
		
		Parser, Extension = name.split(".")

		if not os.path.exists(f"Parsers/{Parser}"):
			self.__Logger.error(f"Parser \"{Parser}\" not found.", stdout = True)
			return False
		
		if os.path.exists(f"Parsers/{Parser}/extensions/{name}"):
			self.__Logger.error(f"Extension \"{name}\" already exists.", stdout = True)
			return False
		
		return True

	def __InitGit(self, path: str):
		"""
		Инициализирует репозиторий Git.
			path – путь к репозиторию.
		"""

		ExitCode = os.system(f"cd {path} && git init -q")
		if ExitCode == 0: self.__Logger.info("Git repository initialized.", stdout = True)
		else: self.__Logger.error("Unable initialize Git repository.", stdout = True)

	def __InsertModuleName(self, path: str, files: str | tuple[str], module: str):
		"""
		Заполняет определение имени парсера.
			path – путь к домашнему каталогу парсера;\n
			files – кортеж файлов для замены;\n
			module – название парсера.
		"""

		if type(files) == str: files = [files]

		for File in files:
			File = Patch(f"{path}/{File}")
			File.replace("NAME = None", f"NAME = \"{module}\"")
			File.replace("{NAME}", module)
			File.save()

	def __IntallFiles(self, files: dict, path: str):
		"""
		Заполняет определение имени парсера.
			files – словарь устанавливаемых файлов;\n
			path – путь установки.
		"""

		for File in files.keys():
			OriginalPath = f"Templates/{File}" 
			Filename = files[File] if files[File] else File
			Path = f"{path}/{Filename}"
			shutil.copy(OriginalPath, Path)
			print("File " + TextStyler(Filename).decorate.italic + " installed.")

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: SystemObjects):
		"""
		Помощник разработчика.
			system_objects – коллекция системных объектов.
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__SystemObjects = system_objects

		self.__Logger = self.__SystemObjects.logger

	def init_extension(self, name: str) -> bool:
		"""
		Инициализирует новый репозиторий расширения.
			name – название расширения.
		"""


		TimerObject = Timer(start = True)
		if not self.__CheckExtensionName(name): return 
		Parser = name.split(".")[0]

		Path = f"Parsers/{Parser}/extensions/{name}"
		BoldName = TextStyler(name).decorate.bold
		self.__Logger.info(f"Initializing extension {BoldName}...", stdout = True)
		os.makedirs(Path)
		
		try:
			self.__InitGit(Path)
			Files = {
				".gitignore": None,
				"EXTENSION.md": "README.md",
				"extension.py": "main.py"
			}
			self.__IntallFiles(Files, Path)
			WriteJSON(f"{Path}/settings.json", dict())
			print("File " + TextStyler("settings.json").decorate.italic + " installed.")
			self.__InsertModuleName(Path, "README.md", name)

		except Exception as ExceptionData: 
			shutil.rmtree(Path)
			self.__Logger.error(str(ExceptionData), stdout = True)

		else: TimerObject.done()

	def init_parser(self, name: str, type: ContentTypes):
		"""
		Инициализирует новый репозиторий парсера.
			name – название парсера;\n
			type – тип контента.
		"""

		TimerObject = Timer(start = True)
		Path = f"Parsers/{name}"
		BoldName = TextStyler(name).decorate.bold
		self.__Logger.info(f"Initializing parser {BoldName}...", stdout = True)

		if os.path.exists(Path):
			self.__Logger.error("Parser with this name already exists.", stdout = True)
			return
		
		else: os.makedirs(Path)
		
		try:
			self.__InitGit(Path)
			Files = {
				".gitignore": None,
				"PARSER.md": "README.md",
				f"{type.value}.py": "main.py"
			}
			self.__IntallFiles(Files, Path)
			WriteJSON(f"{Path}/settings.json", Settings)
			print("File " + TextStyler("settings.json").decorate.italic + " installed.")
			self.__InsertModuleName(Path, ("main.py", "README.md"), name)

		except Exception as ExceptionData: 
			shutil.rmtree(Path)
			self.__Logger.error(str(ExceptionData), stdout = True)

		else: TimerObject.done()