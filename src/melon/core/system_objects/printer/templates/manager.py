from prettytable import PLAIN_COLUMNS, PrettyTable

from dublib.cli.text_styler import FastStyler

from ....system_objects.manager.parsers import ExportResults
from ._base import _BaseTemplatesSection

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

