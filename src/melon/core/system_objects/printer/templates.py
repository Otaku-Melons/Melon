from typing import TYPE_CHECKING

from prettytable import PLAIN_COLUMNS, PrettyTable

from dublib.cli.text_styler import FastStyler
from dublib.functions.data import StringifyFloat

from ...system_objects.parsers_manager import ConfigInstallationResult

if TYPE_CHECKING:
	from ....core.base.parsers.components.images_downloader import (
		ImageDownloadingResult,
	)
	from ....utils.cacher import CachingResult
	from ....utils.classificator import ClassificationResult
	from . import Printer

class Templates:
	"""Расширенные шаблоны вывода."""

	def __init__(self, printer: "Printer"):
		"""
		Расширенные шаблоны вывода.

		:param printer: Оператор вывода.
		:type printer: Printer
		"""

		self.__Printer = printer

	def caching_summary(self, result: "CachingResult"):
		"""
		Шаблон вывода: результат кэширования пар ID-алиас тайтлов.

		:param result: Результат кэширования.
		:type result: CachingResult
		"""

		self.__Printer.emit(f"Total: {result.total_files}. Found in cache: {result.found_in_cache}. Cached: {result.cached}. Updated: {result.updated}.")

		if result.errors:
			self.__Printer.emit(FastStyler("Errors:").decorate.bold)
			for Error in result.errors:
				self.__Printer.emit(" - " + FastStyler(Error + ".json").colorize.red)

	def classification_result(self, result: "ClassificationResult"):
		"""
		Шаблон вывода: результат обработки классификатора.

		:param result: Контейнер результата классификации.
		:type result: ClassificationResult
		"""

		ResultDict = result.to_dict()

		for Key in ResultDict:

			if Key == "is_procedure_found":
				if result.is_procedure_found:
					self.__Printer.emit(FastStyler("is_procedure_found: ").decorate.bold, end_line = False)
					self.__Printer.emit(FastStyler("True").colorize.green)
					continue
				else:
					self.__Printer.emit(FastStyler("is_procedure_found:").decorate.bold, end_line = False)
					self.__Printer.emit(FastStyler("False").colorize.red)
					return
			
			self.__Printer.emit(FastStyler(f"{Key}:").decorate.bold, ResultDict[Key])

	def config_installation_result(self, result: ConfigInstallationResult):
		"""
		Шаблон сообщения: результат установки конфигурации.

		:param result: Результат установки конфигурации.
		:type result: ConfigInstallationResult
		"""

		match result:
			case ConfigInstallationResult.Missing: self.__Printer.emit("Preset missing. Skipped.")
			case ConfigInstallationResult.Installed: self.__Printer.emit("Config installed.")
			case ConfigInstallationResult.AlreadyExists: self.__Printer.emit("Config already exists. Skipped.")
			case ConfigInstallationResult.Overwtitten: self.__Printer.emit("Config overwritten.")
			case ConfigInstallationResult.Merged: self.__Printer.emit("Config merged with preset.")

	def header(self, header: str):
		"""
		Шаблон сообщения: заголовок.

		:param header: Текст заголовка.
		:type header: str
		"""

		header = header.upper()
		header = f"===== {header} ====="
		self.__Printer.emit(header)

	def image_downloading_result(self, result: "ImageDownloadingResult", show_path: bool = True):
		"""
		Шаблон вывода: результат скачивания изображения.

		:param result: Результат скачивания изображения.
		:type result: ImageDownloadingResult
		:param show_path: Указывает, выводить ли путь к изображению.
		:type show_path: bool
		"""

		if result.error_message: self.__Printer.error(result.error_message)
		elif result.is_already_exists and not result.is_downloaded: self.__Printer.emit("Image already exists.")
		elif result.is_already_exists and result.is_downloaded: self.__Printer.emit("Image overwritten.")
		else: self.__Printer.emit("Done.")
		
		if show_path and result.path: self.__Printer.emit(f"Image path: \"{result.path}\".")

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
		self.__Printer.emit(TableString if TableString else "Parsers not installed.")

	def parsing_progress(self, index: int, count: int):
		"""
		Шаблон вывода: прогресс парсинга тайтлов.

		:param index: Индекс обрабатываемого тайтла.
		:type index: int
		:param count: Количество тайтлов.
		:type count: int
		"""

		Number = index + 1
		Progress = round(index / count * 100, 2)
		NumberString = FastStyler(str(Number)).colorize.magenta
		ProgressString = StringifyFloat(Progress)
		ProgressString = FastStyler(ProgressString + "%").colorize.cyan

		self.__Printer.progress_indicator.set_progress(Progress)
		self.__Printer.emit(f"[{NumberString} / {count} | {ProgressString}] ", end_line = False, flush = True)

	def parsing_summary(self, parsed: int, not_found: int, errors: int):
		"""
		Шаблон вывода: результат парсинга.

		:param parsed: Количество успешно собранных тайтлов.
		:type parsed: int
		:param not_found: Количество не найденных в источнике тайтлов.
		:type not_found: int
		:param errors: Количество ошибок.
		:type errors: int
		"""

		self.header("SUMMARY")
		Parsed = FastStyler(str(parsed)).colorize.green if parsed else FastStyler(str(parsed)).colorize.red
		NotFound = FastStyler(str(not_found)).colorize.yellow if not_found else FastStyler(str(not_found)).colorize.green
		Errors = FastStyler(str(errors)).colorize.red if errors else FastStyler(str(errors)).colorize.green

		self.__Printer.progress_indicator.end()
		self.__Printer.emit(f"Parsed: {Parsed}. Not found: {NotFound}. Errors: {Errors}.")