from typing import TYPE_CHECKING

from dublib.web_requestor import WebResponse

from ....core import exceptions

if TYPE_CHECKING:
	from ....core.base.formats.base_format import BaseChapter, BaseTitle
	from . import Printer

class Portals:
	"""Порталы вывода парсера."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def printer(self) -> "Printer":
		"""Оператор вывода."""

		return self.__Printer

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, printer: "Printer", parser_name: str):
		"""
		Порталы вывода парсера.

		:param printer: Оператор вывода.
		:type printer: Printer
		:param parser_name: Имя парсера.
		:type parser_name: str
		"""

		self.__Printer = printer
		self.__ParserName = parser_name

	#==========================================================================================#
	# >>>>> ШАБЛОНЫ ОШИБОК <<<<< #
	#==========================================================================================#

	def authorization_required(self, text: str | None = None, exception: bool = True):
		"""
		Портал ошибки: требуется авторизация.

		:param text: Описание ошибки. Следует указать краткую инструкцию по авторизации, если таковая поддерживается.
		:type text: str | None
		:param exception: Указывает, выбрасывать ли исключение.
		:type exception: bool
		:raises ParsingError: Активирована опция выброса исключения.
		"""

		if not text:
			text = "Should use authorization method for selected parser."

		self.__Printer.critical(text)

		if exception:
			raise exceptions.parsers.AuthorizationRequired(text)

	def request_error(self, response: WebResponse, text: str | None = None, exception: bool = True):
		"""
		Портал ошибки: неудачный запрос.

		:param response: Контейнер ответа.
		:type response: WebResponse
		:param text: Описание ошибки.
		:type text: str | None
		:param exception: Указывает, выбрасывать ли исключение.
		:type exception: bool
		:raises ParsingError: Выбрасывается при активации соответствующего аргумента.
		"""

		if not text:
			text = "Request error."

		Text = f"{text} Response code: {response.status_code}."

		self.__Printer.error(Text)

		if exception:
			raise exceptions.parsers.ParsingError(text)

	def unsupported_format(self, format: str | None = None, exception: bool = True):
		"""
		Шаблон предупреждения: неподдерживаемый формат JSON.

		:param format: Имя формата.
		:type format: str | Non
		:param exception: Указывает, следует ли выбросить исключение.
		:type exception: bool
		:raises UnsupportedFormat: Выбрасывается при активации соответствующего аргумента.
		"""

		Format = f": \"{format}\"" if format else ""
		Text = f"Unsupported JSON format{Format}."

		self.__Printer.error(Text)

		if exception:
			raise exceptions.parsers.UnsupportedFormat(Text)

	#==========================================================================================#
	# >>>>> ШАБЛОНЫ ПРЕДУПРЕЖДЕНИЙ <<<<< #
	#==========================================================================================#

	def chapter_not_found(self, chapter: "BaseChapter", exception: bool = True):
		"""
		Портал предупреждения: глава не найдена.

		:param chapter: Данные главы.
		:type chapter: BaseChapter
		:param exception: Указывает, выбрасывать ли исключение.
		:type exception: bool
		:raise ChapterNotFound: Выбрасывается в качестве исключения портала.
		"""

		Text = f"Chapter {chapter.id} not found."
		self.__Printer.error(Text)

		if exception:
			raise exceptions.parsers.ChapterNotFound(id = chapter.id, slug = chapter.slug)

	def title_not_found(self, title: "BaseTitle", exception: bool = True):
		"""
		Портал предупреждения: тайтл не найден.

		:param title: Данные тайтла.
		:type title: BaseTitle
		:param exception: Указывает, следует ли выбросить исключение.
		:type exception: bool
		:raises TitleNotFound: Выбрасывается в качестве исключения портала.
		"""

		NoteID = f" (ID: {title.id})" if title.id else ""
		Text = f"Title: \"{title.slug}\"{NoteID}. Not found."

		self.__Printer.warning(Text)

		if exception:
			raise exceptions.parsers.TitleNotFound(title)

	#==========================================================================================#
	# >>>>> ШАБЛОНЫ СООБЩЕНИЙ <<<<< #
	#==========================================================================================#

	def chapter_skipped(self, chapter: "BaseChapter", comment: str | None = None):
		"""
		Портал сообщения: дополнение главы пропущено.

		:param chapter: Данные главы.
		:type chapter: BaseChapter
		:param comment: Комментарий о причине пропуска.
		:type comment: str | None
		"""

		ChapterType = "Paid chapter " if chapter.is_paid else "Chapter "
		ChapterIdentificator = ""

		if chapter.id:
			ChapterIdentificator = str(chapter.id)
		elif chapter.slug:
			ChapterIdentificator = f"\"{chapter.slug}\""

		comment = f" {comment}" if comment else ""
		Text = f"{ChapterType}{ChapterIdentificator} skipped.{comment}"

		self.__Printer.emit(Text)

	def collect_progress_by_page(self, page: int):
		"""
		Портал сообщения: индикация прогресса сбора коллекции.

		:param page: Номер страницы каталога, с которого собраны данные.
		:type page: int
		"""

		self.__Printer.emit(f"Titles on page {page} collected.")

	def covers_unstubbed(self):
		"""Портал сообщения: обложки отфильтрованы, так как являются заглушками."""

		self.__Printer.emit("Stubs detected. Covers downloading skipped.")