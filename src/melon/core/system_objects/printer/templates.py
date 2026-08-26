from typing import TYPE_CHECKING, Literal

from prettytable import PLAIN_COLUMNS, PrettyTable

from dublib.cli.text_styler import FastStyler
from dublib.functions.data import StringifyFloat

from ...system_objects.manager.parsers import ExportResults

if TYPE_CHECKING:
	from ....core.base.formats.base_format import BaseChapter, BaseTitle
	from ....core.base.parsers.components.images_downloader import (
		ImageDownloadingResult,
	)
	from ....utils.cacher import CachingResult
	from ....utils.classificator import ClassificationResult
	from . import Printer

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class _BaseTemplatesSection:
	"""Базовая секция шаблонов."""

	@property
	def printer(self) -> "Printer":
		"""Оператор вывода."""

		return self._Printer

	def __init__(self, printer: "Printer"):
		"""
		Базовая секция шаблонов.

		:param printer: Оператор вывода.
		:type printer: Printer
		"""

		self._Printer = printer

class CacherTemplates(_BaseTemplatesSection):
	"""Расширенные шаблоны вывода: оператор кэширования пар ID-алиас."""

	def result(self, result: "CachingResult"):
		"""
		Шаблон вывода: оператор кэширования пар ID-алиас.

		:param result: Результат кэширования.
		:type result: CachingResult
		"""

		self.printer.emit(f"Total: {result.total_files}. Found in cache: {result.found_in_cache}. Cached: {result.cached}. Updated: {result.updated}.")

		if result.errors:
			self.printer.emit(FastStyler("Errors:").decorate.bold)
			for Error in result.errors:
				self.printer.emit(" - " + FastStyler(Error + ".json").colorize.red)

class ClassificatorTemplates(_BaseTemplatesSection):
	"""Расширенные шаблоны вывода: оператор обработки классификаторов."""

	def result(self, result: "ClassificationResult"):
		"""
		Шаблон вывода: оператор обработки классификаторов.

		:param result: Результат обработки классификатора.
		:type result: ClassificationResult
		"""

		ResultDict = result.to_dict()

		for Key in ResultDict:

			if Key == "is_procedure_found":
				if result.is_procedure_found:
					self.printer.emit(FastStyler("is_procedure_found: ").decorate.bold, end_line = False)
					self.printer.emit(FastStyler("True").colorize.green)
					continue
				else:
					self.printer.emit(FastStyler("is_procedure_found:").decorate.bold, end_line = False)
					self.printer.emit(FastStyler("False").colorize.red)
					return
			
			self.printer.emit(FastStyler(f"{Key}:").decorate.bold, ResultDict[Key])

class CollectorTemplates(_BaseTemplatesSection):
	"""Расширенные шаблоны вывода: сборщик алиасов."""

	def collected(self, count: int):
		"""
		Шаблон сообщения: коллекция собрана.

		:param count: Количество добавленных в коллекцию тайтлов.
		:type count: int
		"""

		self.printer.emit(f"Slugs collected: {count}.")

	def start(self):
		"""Шаблон вывода: начато сканирование локальных тайтлов."""

		self.printer.emit("Collecting titles… ", flush = True)

class ImagesTemplates(_BaseTemplatesSection):
	"""Расширенные шаблоны вывода: обработка изображений."""

	def downloaded(self, result: "ImageDownloadingResult", show_path: bool = True):
		"""
		Шаблон вывода: результат скачивания изображения.

		:param result: Результат скачивания изображения.
		:type result: ImageDownloadingResult
		:param show_path: Указывает, выводить ли путь к изображению.
		:type show_path: bool
		"""

		if result.error_message: self.printer.error(result.error_message)
		elif result.is_already_exists and not result.is_downloaded: self.printer.emit("Image already exists.")
		elif result.is_already_exists and result.is_downloaded: self.printer.emit("Image overwritten.")
		else: self.printer.emit("Done.")
		
		if show_path and result.path: self.printer.emit(f"Image path: \"{result.path}\".")

	def start_downloading(self, filename: str, image_type: Literal["cover", "person", "slide"] | None = None, end_line: bool = False):
		"""
		Шаблон вывода: скачивание изображения начато.

		:param filename: Имя файла.
		:type filename: str
		:param image_type: Тип изображения.
		:type image_type: Literal["cover", "person", "slide"] | None
		:param end_line: bool
		:type end_line: Указывает, нужно ли добавить в конец строки символ новой строки.
		"""

		ImageType: str = "" if image_type is None else f" {image_type}"
		self.printer.emit(f"Downloading{ImageType} \"{filename}\"… ", end_line = end_line)

class ManagerTemplates(_BaseTemplatesSection):
	"""Расширенные шаблоны вывода: системный менеджер."""

	def exported(self, result: ExportResults):
		"""
		Шаблон вывода: результат экспорта настроек.

		:param result: Результат экспорта настроек.
		:type result: ExportResults
		"""

		match result:
			case ExportResults.Missing: self.printer.emit("Preset missing. Skipped.")
			case ExportResults.Installed: self.printer.emit("Config installed.")
			case ExportResults.AlreadyExists: self.printer.emit("Config already exists. Skipped.")
			case ExportResults.Overwtitten: self.printer.emit("Config overwritten.")
			case ExportResults.Merged: self.printer.emit("Config merged with preset.")

	def parsers_table(self, columns: dict[str, list[str]]):
		"""
		Шаблон вывода: таблица парсеров.

		:param columns: Словарь данных для вывода.
		:type columns: dict[str, list[str]]
		"""

		TableObject = PrettyTable()
		TableObject.set_style(PLAIN_COLUMNS)
		Implementations = ("collect",)
		ImplementationStatuses = {
			"True": FastStyler("true").colorize.green,
			"False": FastStyler("false").colorize.yellow,
			"None": FastStyler("error").colorize.red,
		}

		for DomainIndex in range(len(columns["DOMAIN"])):
			columns["DOMAIN"][DomainIndex] = FastStyler(columns["DOMAIN"][DomainIndex]).decorate.italic

		for ColumnName in Implementations:

			for StatusIndex in range(len(columns[ColumnName])):
				columns[ColumnName][StatusIndex] = ImplementationStatuses[columns[ColumnName][StatusIndex]]

		for ColumnName in columns.keys():
			Buffer = FastStyler(ColumnName).decorate.bold
			TableObject.add_column(Buffer, columns[ColumnName])

		TableObject.align = "l"
		TableObject.sortby = FastStyler("NAME").decorate.bold
		TableString = str(TableObject).strip()
		self.printer.emit(TableString if TableString else "Parsers not installed.")

class ParsingTemplates(_BaseTemplatesSection):
	"""Расширенные шаблоны вывода: процесс парсинга."""

	def amending_end(self, amended_chapter_count: int):
		"""
		Шаблон сообщения: дополнение глав завершено.

		:param amended_chapter_count: Количество дополненных глав.
		:type amended_chapter_count: int
		"""

		Text = f"Amended chapters count: {amended_chapter_count}."
		self.printer.emit(Text)
	
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
		self.printer.emit(Text)

	def chapter_repaired(self, chapter: "BaseChapter"):
		"""
		Шаблон сообщения: глава восстановлена.

		:param chapter: Данные главы.
		:type chapter: BaseChapter
		"""

		ChapterNote = "Paid chapter" if chapter.is_paid else "Chapter"
		Text = f"{ChapterNote} {chapter.id} repaired."
		self.printer.emit(Text)

	def progress(self, index: int, count: int):
		"""
		Шаблон вывода: прогресс парсинга тайтлов.

		:param index: Индекс обрабатываемого тайтла.
		:type index: int
		:param count: Количество тайтлов.
		:type count: int
		"""

		Number = index + 1
		Progress = round(Number / count * 100, 2)
		NumberString = FastStyler(str(Number)).colorize.magenta
		ProgressString = StringifyFloat(Progress)
		ProgressString = FastStyler(ProgressString + "%").colorize.cyan

		self.printer.progress_indicator.set_progress(Progress)
		self.printer.emit(f"[{NumberString} / {count} | {ProgressString}] ", end_line = False, flush = True)

	def start(self, title: "BaseTitle", index: int, titles_count: int):
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
			self.progress(index, titles_count)

		self.printer.emit(f"Parsing <b>{title.slug}</b>{NoteID}…")

	def summary(self, parsed: int, not_found: int, errors: int):
		"""
		Шаблон вывода: результат парсинга.

		:param parsed: Количество успешно собранных тайтлов.
		:type parsed: int
		:param not_found: Количество не найденных в источнике тайтлов.
		:type not_found: int
		:param errors: Количество ошибок.
		:type errors: int
		"""

		self.printer.emit("===== SUMMARY =====")
		Parsed = FastStyler(str(parsed)).colorize.green if parsed else FastStyler(str(parsed)).colorize.red
		NotFound = FastStyler(str(not_found)).colorize.yellow if not_found else FastStyler(str(not_found)).colorize.green
		Errors = FastStyler(str(errors)).colorize.red if errors else FastStyler(str(errors)).colorize.green

		self.printer.progress_indicator.end()
		self.printer.emit(f"Parsed: {Parsed}. Not found: {NotFound}. Errors: {Errors}.")

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Templates:
	"""Расширенные шаблоны вывода."""
	
	@property
	def cacher(self) -> CacherTemplates:
		"""Расширенные шаблоны вывода: оператор кэширования пар ID-алиас."""

		return self.__Cacher

	@property
	def classificator(self) -> ClassificatorTemplates:
		"""Расширенные шаблоны вывода: оператор обработки классификаторов."""

		return self.__Classificator

	@property
	def collector(self) -> CollectorTemplates:
		"""Расширенные шаблоны вывода: сборщик алиасов."""

		return self.__Collector

	@property
	def images(self) -> ImagesTemplates:
		"""Расширенные шаблоны вывода: обработка изображений."""

		return self.__Images
	
	@property
	def manager(self) -> ManagerTemplates:
		"""Расширенные шаблоны вывода: системный менеджер."""

		return self.__Manager
	
	@property
	def parsing(self) -> ParsingTemplates:
		"""Расширенные шаблоны вывода: процесс парсинга."""

		return self.__Parsing

	def __init__(self, printer: "Printer"):
		"""
		Расширенные шаблоны вывода.

		:param printer: Оператор вывода.
		:type printer: Printer
		"""

		self.__Printer = printer

		self.__Cacher = CacherTemplates(self.__Printer)
		self.__Classificator = ClassificatorTemplates(self.__Printer)
		self.__Collector = CollectorTemplates(self.__Printer)
		self.__Images = ImagesTemplates(self.__Printer)
		self.__Manager = ManagerTemplates(self.__Printer)
		self.__Parsing = ParsingTemplates(self.__Printer)
