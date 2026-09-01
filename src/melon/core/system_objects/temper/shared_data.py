from pathlib import Path
from typing import TYPE_CHECKING

from dublib.functions.filesystem import ReadJSON, WriteJSON

from .journal import Journal

if TYPE_CHECKING:
	from ..temper import Temper

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
