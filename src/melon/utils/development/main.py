from typing import Sequence

from dublib.web_requestor import WebRequestor

from ...core.base.parsers.components.images_downloader import ImageDownloadingResult
from ...core.base.source_operator import BaseSourceOperator

class SourceOperator(BaseSourceOperator):
	"""Оператор источника."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def _CollectSlugs(self, period: int | None = None, filters: str | None = None, pages: int | None = None) -> Sequence[str]:
		"""
		Собирает список алиасов тайтлов по заданным параметрам.

		:param period: Количество часов до текущего момента, составляющее период получения данных.
		:type period: int | None
		:param filters: Строка, описывающая параметры фильтрации.
		:type filters: str | None
		:param pages: Количество запрашиваемых страниц каталога.
		:type pages: int | None
		:return: Набор собранных алиасов.
		:rtype: Sequence[str]
		"""

		return super()._CollectSlugs(period, filters, pages)

	def _InitializeRequestor(self) -> WebRequestor:
		"""
		Инициализирует модуль WEB-запросов.

		:return: Оператор запросов.
		:rtype: WebRequestor
		"""

		return super()._InitializeRequestor()

	def _IsTitleExists(self, slug: str) -> bool | None:
		"""
		Проверяет, существует ли тайтл на сервере.

		:param slug: Алиас тайтла.
		:type slug: str
		:return: Возвращает статус существования файла на сервере или `None` при невозможности проверки.
		:rtype: bool | None
		"""

		return None

	def _ParseSlugFromString(self, string: str) -> str | None:
		"""
		Парсит алиас тайтла из переданной строки. Может использоваться для обработки тайтлов по ссылкам.

		:param string: Строка, из которой требуется получить алиас.
		:type string: str
		:return: Алиас или `None` в случае неудачи или отсутствия имплементации.
		:rtype: str | None
		"""

		return super()._ParseSlugFromString(string)

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	def _PostMirrorChanging(self, mirror: str | None):
			"""
			Выполняется после изменения зеркала.
	
			:param mirror: Домен зеркала.
			:type mirror: str | None
			"""
	
			pass

	def _TempImage(self, url: str, force_mode: bool = False) -> ImageDownloadingResult:
		"""
		Скачивает изображение по ссылке и сохраняет во временный каталог парсера.

		:param url: Ссылка на изображение.
		:type url: str
		:param force_mode: Переключает режим перезаписи существующих изображений.
		:type force_mode: bool
		:return: Результат скачивания изображения.
		:rtype: ImageDownloadingResult
		"""

		return super()._TempImage(url, force_mode)