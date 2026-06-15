from dublib.CLI.TextStyler import FastStyler

from typing import TYPE_CHECKING

from prettytable import PLAIN_COLUMNS, PrettyTable

if TYPE_CHECKING:
	from Source.Utils.Classificator import ClassificationResult

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

def PrintOptionStatus(option: str, status: bool, inverse: bool = False):
	"""
	Выводит в консоль стилизованный статус активации опции.

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
	Выводит в консоль форматированную таблицу парсеров.

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
	TableObject = str(TableObject).strip()
	Link = FastStyler("https://github.com/Otaku-Melons").decorate.underlined
	print(TableObject if TableObject else f"Parsers not installed. See {Link} for more info.")