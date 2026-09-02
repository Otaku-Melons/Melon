from pathlib import Path
from typing import TYPE_CHECKING

from dublib.functions.filesystem import json

if TYPE_CHECKING:
	from .shared_data import SharedData

class Journal:
	"""Журнал кэша пар ID-алиас тайтлов."""

	def __init__(self, shared_data: "SharedData"):
		"""
		Журнал кэша пар ID-алиас тайтлов

		:param shared_data: Разделяемые в контексте одного парсера данные.
		:type shared_data: SharedData
		"""

		self.__SharedData = shared_data

		self.__JournalPath = Path(f"{self.__SharedData.path}/journal.json")
		self.__Data: dict[int, str] = {}

	def get_id_by_slug(self, slug: str) -> int | None:
		"""
		Ищет ID тайтла по его алиасу.

		Отключается переменной среды `MELON_USE_CACHE`.

		:param slug: Алиас тайтла.
		:type slug: str
		"""

		if not self.__SharedData.temper.system_obejcts.options.USE_CACHE:
			return None

		for ID, Slug in self.__Data.items():
			if slug == Slug:
				return ID

		return None

	def get_slug_by_id(self, title_id: int) -> str | None:
		"""
		Ищет алиас тайтла по его ID.

		Отключается переменной среды `MELON_USE_CACHE`.

		:param title_id: ID тайтла.
		:type title_id: int
		"""

		if not self.__SharedData.temper.system_obejcts.options.USE_CACHE:
			return None

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
			self.__Data = {int(Key): Value for Key, Value in json.read(self.__JournalPath).items()}
		else:
			self.__Data = {}

	def save(self):
		"""Сохраняет журнал."""

		self.__Data = dict(sorted(self.__Data.items()))
		json.write(self.__JournalPath, self.__Data)

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

