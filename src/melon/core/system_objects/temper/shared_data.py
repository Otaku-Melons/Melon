from pathlib import Path
from typing import TYPE_CHECKING

from dublib.functions.filesystem import json

from .filtered_images import FilteredImages
from .journal import Journal

if TYPE_CHECKING:
	from ..temper import Temper

class SharedData:
	"""Разделяемые в контексте сессий одного парсера данные."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def filtered_images(self) -> FilteredImages:
		"""Кэш отфильтрованных изображений."""

		return self.__filtered_images

	@property
	def journal(self) -> Journal:
		"""Журнал кэша пар ID-алиас тайтлов."""

		return self.__journal

	@property
	def last_parsed_slug(self) -> str | None:
		"""
		Алиас последнего тайтла, обработанного парсером.

		Отключается переменной среды `MELON_USE_CACHE`.
		"""

		if not self.__temper.system_obejcts.options.USE_CACHE:
			return None

		return self.__data.get("last_parsed_slug")

	@property
	def path(self) -> Path:
		"""Путь к каталогу разделяемых данных."""

		return self.__shared_data_directory

	@property
	def temper(self) -> "Temper":
		"""Дескриптор временных каталогов и объектов."""
		
		return self.__temper

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

		self.__temper = temper
		self.__parser_name = parser_name

		self.__shared_data_directory = Path(self.__temper.get_parser_temp_directory(self.__parser_name) / "shared")
		self.__shared_data_directory.mkdir(exist_ok = True)

		self.__shared_data_file = Path(f"{self.__shared_data_directory}/shared.json")

		self.__data: dict = {
			"last_parsed_slug": None
		}

		self.__filtered_images = FilteredImages(self)
		self.__journal = Journal(self)

		self.load()

	def load(self):
		"""Загружает разделяемые данные."""

		if self.__shared_data_file.exists():
			self.__data = self.__data | json.read(self.__shared_data_file)

		self.__filtered_images.load()
		self.__journal.load()

	def set_last_parsed_slug(self, slug: str):
		"""
		Задаёт алиас последнего обработанного парсером тайтла.

		:param slug: Алиас.
		:type slug: str
		"""

		self.__data["last_parsed_slug"] = slug
		self.save()
		
	def save(self):
		"""Сохраняет разделяемые данные."""

		json.write(self.__shared_data_file, self.__data)
