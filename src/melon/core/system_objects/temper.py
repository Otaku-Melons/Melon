import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Sequence

from dublib.functions.filesystem import ReadJSON, RemoveDirectoryContent, WriteJSON

if TYPE_CHECKING:
	from ...core.system_objects import SystemObjects

#==========================================================================================#
# >>>>> СТРУКТУРЫ РАЗДЕЛЯЕМЫХ ДАННЫХ <<<<< #
#==========================================================================================#

class Journal:
	"""Журнал кэша пар ID-алиас тайтлов."""

	def __init__(self, shared_data: "SharedData"):
		"""
		Журнал хранения пар ID-алиас тайтлов.

		:param shared_data: Разделяемые в контексте одного парсера данные.
		:type shared_data: SharedData
		"""

		self.__SharedData = shared_data

		self.__JournalPath = Path(f"{self.__SharedData.path}/journal.json")
		self.__Data: dict[int, str] = {}

	def get_id_by_slug(self, slug: str) -> int | None:
		"""
		Ищет ID тайтла по его алиасу.

		:param slug: Алиас тайтла.
		:type slug: str
		"""

		for ID, Slug in self.__Data.items():
			if slug == Slug:
				return ID

		return None

	def get_slug_by_id(self, title_id: int) -> str | None:
		"""
		Ищет алиас тайтла по его ID.

		:param title_id: ID тайтла.
		:type title_id: int
		"""

		try:
			return self.__Data[title_id]
		except KeyError:
			return None

	def drop(self):
		"""Сбрасывает журнал."""

		self.__Data = {}
		self.save()

	def load(self):
		"""Загружает журнал."""

		if self.__JournalPath.exists():
			self.__Data = {int(Key): Value for Key, Value in ReadJSON(self.__JournalPath).items()}
		else:
			self.__Data = {}

	def save(self):
		"""Сохраняет журнал."""

		self.__Data = dict(sorted(self.__Data.items()))
		WriteJSON(self.__JournalPath, self.__Data)

	def update(self, title_id: int, slug: str):
		"""
		Обновляет запись об алиасе тайтла.

		:param title_id: ID тайтла.
		:type title_id: int
		:param slug: Алиас тайтла.
		:type slug: str
		:raise TypeError: Выбрасывается при неверном типе переданных данных.
		"""

		if type(title_id) is not int: raise TypeError("Title ID must be integer.")
		if type(slug) is not str: raise TypeError("Title slug must be string.")
		self.__Data[title_id] = slug
		self.save()

class SharedData:
	"""Разделяемые в контексте сессий одного парсера данные."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def journal(self) -> Journal:
		"""Журнал кэша пар ID-алиас тайтлов."""

		return self.__Journal

	@property
	def last_parsed_slug(self) -> str | None:
		"""Алиас последнего тайтла, обработанного парсером."""

		return self.__Data.get("last_parsed_slug")

	@property
	def path(self) -> Path:
		"""Путь к каталогу разделяемых данных."""

		return self.__SharedDataDirectoryPath

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	def __init__(self, temper: "Temper", parser_name: str):
		"""
		Разделяемые в контексте сессий одного парсера данные.

		:param temper: Дескриптор временных каталогов и объектов.
		:type temper: Temper
		:param parser_name: Имя парсера.
		:type parser_name: str
		"""

		self.__Temper = temper
		self.__ParserName = parser_name

		self.__SharedDataDirectoryPath = Path(self.__Temper.get_parser_temp_directory(self.__ParserName) / "shared")
		self.__SharedDataDirectoryPath.mkdir(exist_ok = True)

		self.__SharedDataPath = Path(f"{self.__SharedDataDirectoryPath}/shared.json")

		self.__Data: dict = {
			"last_parsed_slug": None
		}

		self.__Journal = Journal(self)

		self.load()

	def load(self):
		"""Загружает разделяемые данные."""

		if self.__SharedDataPath.exists():
			self.__Data = self.__Data | ReadJSON(self.__SharedDataPath)

		self.__Journal.load()

	def set_last_parsed_slug(self, slug: str):
		"""
		Задаёт алиас последнего обработанного парсером тайтла.

		:param slug: Алиас.
		:type slug: str
		"""

		self.__Data["last_parsed_slug"] = slug
		self.save()
		
	def save(self):
		"""Сохраняет разделяемые данные."""

		WriteJSON(self.__SharedDataPath, self.__Data)

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Temper:
	"""Дескриптор временных каталогов и объектов."""

	def __init__(self, system_objects: "SystemObjects"):
		"""
		Оператор временных каталогов и объектов.
		
		:param system_objects: Коллекция системных объектов.
		:type system_objects: SystemObjects
		"""

		self.__SystemObjects: "SystemObjects" = system_objects

		self.__TempDirectory = self.__SystemObjects.options.TEMP_DIR.value
		self.__TempDirectory.mkdir(exist_ok = True)

	def clear_parser_temp(self, parser_name: str, whitelist: Sequence[str] | None = ("Collection.txt", "shared")):
		"""
		Очищает временный каталог парсера. По умолчанию не трогает файлы и каталоги из белого списка.

		:param parser_name: Имя парсера.
		:type parser_name: str
		:param whitelist: Последовательность не удаляемых файлов и папок во временном каталоге. При `None` происходит полная очистка.
		:type whitelist: bool
		"""

		ParserTempDirectory = self.get_parser_temp_directory(parser_name)

		if not whitelist: 
			RemoveDirectoryContent(ParserTempDirectory)
			return

		for Descriptor in os.scandir(ParserTempDirectory):
			if Descriptor.name in whitelist:
				continue

			if Descriptor.is_file():
				os.remove(Descriptor.path)
			elif Descriptor.is_dir():
				shutil.rmtree(Descriptor.path)

	def get_parser_temp_directory(self, parser_name: str) -> Path:
		"""
		Возвращает путь ко временной директории парсера и автоматически создаёт её.

		:param parser_name: Имя парсера.
		:type parser_name: str
		:return: Путь ко временной директории парсера.
		:rtype: Path
		"""

		ParserTempDirectory = self.__TempDirectory / parser_name
		ParserTempDirectory.mkdir(exist_ok = True)

		return ParserTempDirectory

	def load_parser_shared_data(self, parser_name: str) -> SharedData:
		"""
		Загружает разделяемые в контексте сессий одного парсера данные.

		:param parser_name: Имя парсера.
		:type parser_name: str
		:return: Разделяемые в контексте сессий одного парсера данные.
		:rtype: SharedData
		"""

		return SharedData(self, parser_name)