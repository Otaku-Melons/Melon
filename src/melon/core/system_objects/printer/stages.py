
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ....core.base.formats.base_format import BaseChapter, BaseTitle
	from . import Printer

class Stages:
	"""Сообщения этапов выполнения."""

	def __init__(self, printer: "Printer"):
		"""
		Сообщения этапов выполнения.

		:param printer: Оператор вывода.
		:type printer: Printer
		"""

		self.__Printer = printer

	def amending_end(self, amended_chapter_count: int):
		"""
		Шаблон сообщения: дополнение глав завершено.

		:param amended_chapter_count: Количество дополненных глав.
		:type amended_chapter_count: int
		"""

		Text = f"Amended chapters count: {amended_chapter_count}."
		self.__Printer.emit(Text)
	
	def chapter_amended(self, chapter: "BaseChapter", message: str | None = None):
		"""
		Шаблон сообщения: глава дополнена.

		:param chapter: Данные главы.
		:type chapter: BaseChapter
		:param message: Дополнительное необязательное сообщение о получении главы.
		:type message: str | None
		"""

		if message is None: message = ""
		if message: message = " " + message.strip()

		ChapterNote = "Paid chapter" if chapter.is_paid else "Chapter"
		Text = f"{ChapterNote} {chapter.id} amended.{message}"
		self.__Printer.emit(Text)

	def chapter_repaired(self, chapter: "BaseChapter"):
		"""
		Шаблон сообщения: глава восстановлена.

		:param chapter: Данные главы.
		:type chapter: BaseChapter
		"""

		ChapterNote = "Paid chapter" if chapter.is_paid else "Chapter"
		Text = f"{ChapterNote} {chapter.id} repaired."
		self.__Printer.emit(Text)

	def parsing_start(self, title: "BaseTitle", index: int, titles_count: int):
		"""
		Шаблон сообщения: парсинг начат.

		:param title: Данные тайтла.
		:type title: BaseTitle
		:param index: Индекс текущей операции парсинга.
		:type index: int
		:param titles_count: Количество тайтлов.
		:type titles_count: int
		"""

		NoteID = f" (ID: {title.id})" if title.id else ""

		if titles_count > 1:
			self.__Printer.templates.parsing_progress(index, titles_count)

		self.__Printer.emit(f"Parsing <b>{title.slug}</b>{NoteID}…")

	def titles_collected(self, count: int):
		"""
		Шаблон сообщения: коллекция собрана.

		:param count: Количество добавленных в коллекцию тайтлов.
		:type count: int
		"""

		self.__Printer.emit(f"Titles collected: {count}.")