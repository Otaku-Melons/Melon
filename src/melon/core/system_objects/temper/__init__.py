import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Sequence

from dublib.functions.filesystem import RemoveDirectoryContent

from .shared_data import SharedData

if TYPE_CHECKING:
	from ....core.system_objects import SystemObjects

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

	def clear_parser_temp(self, parser_name: str, whitelist: Sequence[str] | None = ("collections", "shared")):
		"""
		Очищает временный каталог парсера. По умолчанию не удаляет файлы и каталоги из белого списка.

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

	def get_extension_temp_directory(self, parser_name: str, extension_name: str) -> Path:
		"""
		Возвращает путь ко временной директории расширения и автоматически создаёт её.

		:param parser_name: Имя парсера.
		:type parser_name: str
		:param extension_name: Имя расширения.
		:type extension_name: str
		:return: Путь ко временной директории расширения.
		:rtype: Path
		"""

		ParserTemp: Path = self.get_parser_temp_directory(parser_name)
		ExtensionsTemp: Path = ParserTemp / "extensions"
		ExtensionsTemp.mkdir(exist_ok = True)
		ExtensionTemp: Path = ExtensionsTemp / extension_name
		ExtensionTemp.mkdir(exist_ok = True)

		return ExtensionTemp

	def get_parser_collections_directory(self, parser_name: str) -> Path:
		"""
		Возвращает путь к каталогу коллекций парсера и автоматически создаёт его.

		:param parser_name: Имя парсера.
		:type parser_name: str
		:return: Путь к каталогу коллекций парсера.
		:rtype: Path
		"""

		ParserCollectionDirectory = self.get_parser_temp_directory(parser_name) / "collections"
		ParserCollectionDirectory.mkdir(exist_ok = True)

		return ParserCollectionDirectory

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