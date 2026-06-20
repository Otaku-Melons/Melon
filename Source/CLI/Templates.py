from dublib.Methods.Data import StringifyFloat
from dublib.CLI.TextStyler import FastStyler

from typing import TYPE_CHECKING

from prettytable import PLAIN_COLUMNS, PrettyTable

if TYPE_CHECKING:
	from Source.Utils.Classificator import ClassificationResult
	from Source.Utils.Cacher import CachingResult

def PrintCachingSummary(result: "CachingResult"):
	"""
	Выводит в терминал результат кэширования пар ID-алиас тайтлов.

	:param result: Результат кэширования.
	:type result: CachingResult
	"""

	print(f"Total: {result.total_files}. Found in cache: {result.found_in_cache}. Cached: {result.cached_files}.")

	if result.errors:
		print(FastStyler("Errors:").decorate.bold)
		for Error in result.errors:
			print(" - " + FastStyler(Error + ".json").colorize.red)

def PrintClassificationResult(result: "ClassificationResult", input_value: str):
	"""
	Выводит в терминал стилизованный результат классификации.

	:param result: Контейнер результата классификации.
	:type result: ClassificationResult
	:param input_value: Искомое значение.
	:type input_value: str
	"""

	ResultDict = result.to_dict()

	for Key in ResultDict:

		if Key == "is_procedure_found":
			if result.is_procedure_found:
				print(FastStyler("is_procedure_found:").decorate.bold, FastStyler("True").colorize.green)
				continue
			else:
				print(FastStyler("is_procedure_found:").decorate.bold, FastStyler("False").colorize.red)
				return
		
		print(FastStyler(f"{Key}:").decorate.bold, ResultDict[Key])

def PrintHeader(header: str):
	"""
	Выводит в терминал заголовок.

	:param header: Заголовок.
	:type header: str
	"""

	print(f"===== {header.upper()} =====")

def PrintOptionStatus(option: str, status: bool, inverse: bool = False):
	"""
	Выводит в терминал стилизованный статус активации опции.

	:param option: Имя опции.
	:type option: str
	:param status: Состояние активации опции.
	:type status: bool
	:param inverse: Указывает, нужно ли инвертировать цвета статусов.
	:type inverse: bool
	"""

	ColoredStatus = FastStyler("enabled").colorize.green if status else FastStyler("disabled").colorize.red
	if inverse: ColoredStatus = FastStyler("enabled").colorize.red if status else FastStyler("disabled").colorize.green

	print(f"{option}: {ColoredStatus}")

def PrintParsersTable(columns: dict[str, list[str]]):
	"""
	Выводит в терминал форматированную таблицу парсеров.

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

	for SiteIndex in range(len(columns["SITE"])):
		columns["SITE"][SiteIndex] = FastStyler(columns["SITE"][SiteIndex]).decorate.italic

	for ColumnName in Implementations:

		for StatusIndex in range(len(columns[ColumnName])):
			columns[ColumnName][StatusIndex] = ImplementationStatuses[columns[ColumnName][StatusIndex]]

	for ColumnName in columns.keys():
		Buffer = FastStyler(ColumnName).decorate.bold
		TableObject.add_column(Buffer, columns[ColumnName])

	TableObject.align = "l"
	TableObject.sortby = FastStyler("NAME").decorate.bold
	TableString = str(TableObject).strip()
	Link = FastStyler("https://github.com/Otaku-Melons").decorate.underlined
	print(TableString if TableString else f"Parsers not installed. See {Link} for more info.")

def PrintParsingProgress(index: int, count: int):
	"""
	Выводит прогресс парсинга тайтлов.

	:param index: Индекс обрабатываемого тайтла.
	:type index: int
	:param count: Количество тайтлов.
	:type count: int
	"""

	Number = index
	Progress = round(Number / count * 100, 2)
	NumberString = FastStyler(str(Number)).colorize.magenta
	ProgressString = StringifyFloat(Progress)
	ProgressString = FastStyler(ProgressString + "%").colorize.cyan
	print(f"[{NumberString} / {count} | {ProgressString}] ", end = "", flush = True)

def PrintParsingSummary(parsed: int, not_found: int, errors: int):
	"""
	Выводит результат парсинга.

	:param parsed: Количество успешно собранных тайтлов.
	:type parsed: int
	:param not_found: Количество не найденных в источнике тайтлов.
	:type not_found: int
	:param errors: Количество ошибок.
	:type errors: int
	"""

	PrintHeader("SUMMARY")
	Parsed = FastStyler(str(parsed)).colorize.green if parsed else FastStyler(str(parsed)).colorize.red
	NotFound = FastStyler(str(not_found)).colorize.yellow if not_found else FastStyler(str(not_found)).colorize.green
	Errors = FastStyler(str(errors)).colorize.red if errors else FastStyler(str(errors)).colorize.green
	print(f"Parsed: {Parsed}. Not found: {NotFound}. Errors: {Errors}.")