from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from dublib.functions.filesystem import json

from ...base.parsers.components.images_downloader import FilteredBy

if TYPE_CHECKING:
	from .shared_data import SharedData

class FilteredImages:
	"""Кэш отфильтрованных изображений."""

	def __reason_to_section_name(self, filtered_by: FilteredBy) -> str:
		"""
		Преобразовывает причину фильтрации в имя секции.

		:param filtered_by: Причина фильтрации.
		:type filtered_by: FilteredBy
		:return: Имя секции.
		:rtype: str
		"""

		return "by_" + filtered_by.name.lower()

	def __init__(self, shared_data: "SharedData"):
		"""
		Кэш отфильтрованных изображений.

		:param shared_data: Разделяемые в контексте одного парсера данные.
		:type shared_data: SharedData
		"""

		self.__shared_data = shared_data

		self.__cache_path = Path(f"{self.__shared_data.path}/filtered_images.json")
		self.__data: dict[str, list[str]] = {self.__reason_to_section_name(reason): [] for reason in FilteredBy}

	def add(self, link: str, filtered_by: FilteredBy) -> bool:
		"""
		Помещает ссылку на изображение в кэш. Не дублирует записи.

		:param link: Ссылка.
		:type link: str
		:param filtered_by: Причина фильтрации.
		:type filtered_by: FilteredBy
		:return: Возвращает `True`, если ссылка добавлена в кэш.
		:rtype: bool
		"""

		link = urlparse(link).path
		section: str = "by_" + filtered_by.name.lower()
		
		if link not in self.__data[section]:
			self.__data[section].append(link)
			self.save()
			return True

		return False

	def check(self, link: str) -> FilteredBy | None:
		"""
		Проверяет, содержится ли ссылка в кэше.

		Отключается переменной среды `MELON_USE_CACHE`.

		:param link: Ссылка.
		:type link: str
		:return: Причина фильтрации или `None`, если ссылка не найдена.
		:rtype: FilteredBy | None
		"""

		if not self.__shared_data.temper.system_obejcts.options.USE_CACHE:
			return None

		link = urlparse(link).path

		for reason in FilteredBy:
			if link in self.get_section(reason):
				return reason

		return None

	def drop(self):
		"""Сбрасывает журнал."""

		for reason in FilteredBy:
			section: str = self.__reason_to_section_name(reason)
			self.__data[section].clear()

		self.save()

	def get_section(self, filtered_by: FilteredBy) -> tuple[str, ...]:
		"""
		Получает содержимое секции кэша.

		Отключается переменной среды `MELON_USE_CACHE`.

		:param filtered_by: Причина фильтрации.
		:type filtered_by: FilteredBy
		:return: Содержимое секции.
		:rtype: tuple[str, ...]
		"""

		if not self.__shared_data.temper.system_obejcts.options.USE_CACHE:
			return ()

		section: str = self.__reason_to_section_name(filtered_by)

		return tuple(self.__data[section])

	def load(self):
		"""Загружает кэш."""

		if self.__cache_path.exists():
			self.__data = self.__data | json.read(self.__cache_path)

	def save(self):
		"""Сохраняет кэш."""

		json.write(self.__cache_path, self.__data)
