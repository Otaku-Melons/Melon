from prettytable import PLAIN_COLUMNS, PrettyTable
from dublib.CLI.TextStyler import TextStyler

class Templates:
	"""Набор шаблонов ввода-вывода."""

	#==========================================================================================#
	# >>>>> БАЗОВЫЕ ШАБЛОНЫ <<<<< #
	#==========================================================================================#

	def header(text: str):
		"""
		Выводит в консоль заголовок.
			text – заголовок.
		"""

		print(f"=== {text} ===")

	#==========================================================================================#
	# >>>>> ЧАСТНЫЕ ШАБЛОНЫ <<<<< #
	#==========================================================================================#

	def option_status(text: str, status: bool):
		"""
		Выводит в консоль форматированный статус опции.
			text – название опции;\n
			status – статус.
		"""

		status = TextStyler("enabled").colorize.green if status else TextStyler("disabled").colorize.red
		print(f"{text}: {status}")

	def parsers_table(columns: dict[str, list], sort_by: str = "NAME"):
		"""
		Выводит в консоль форматированную таблицу установленных парсеров.
			columns – данные для вывода;\n
			sort_by – название колонки для сортировки.
		"""

		TableObject = PrettyTable()
		TableObject.set_style(PLAIN_COLUMNS)
		Implementations = ["collect"]
		ImplementationStatuses = {
			True: TextStyler("true").colorize.green,
			False: TextStyler("false").colorize.yellow,
			None: TextStyler("error").colorize.red,
		}

		for SiteIndex in range(len(columns["SITE"])):
			columns["SITE"][SiteIndex] = TextStyler(columns["SITE"][SiteIndex]).decorate.italic

		for ColumnName in Implementations:

			for StatusIndex in range(len(columns[ColumnName])):
				columns[ColumnName][StatusIndex] = ImplementationStatuses[columns[ColumnName][StatusIndex]]

		for ColumnName in columns.keys():
			Buffer = TextStyler(ColumnName).decorate.bold
			TableObject.add_column(Buffer, columns[ColumnName])

		TableObject.align = "l"
		TableObject.sortby = TextStyler(sort_by).decorate.bold
		TableObject = str(TableObject).strip()
		Link = TextStyler("https://github.com/Otaku-Melons").decorate.underlined
		print(TableObject if TableObject else f"Parsers not installed. See {Link} for more info.")

	def parsing_progress(index: int, count: int):
		"""
		Выводит прогресс обработки множества элементов.
			index – индекс обрабатываемого элемента;\n
			count – количество жлементов.
		"""

		Number = index + 1
		Progress = round(Number / count * 100, 2)
		Number = TextStyler(str(Number)).colorize.magenta
		if str(Progress).endswith(".0"): Progress = str(int(Progress))
		elif len(str(Progress).split(".")[-1]) == 1: Progress = str(Progress) + "0"
		else: Progress = str(Progress)
		Progress = TextStyler(Progress + "%").colorize.cyan
		print(f"[{Number} / {count} | {Progress}] ", end = "")

	def parsing_summary(parsed: int, not_found: int, errors: int):
		"""
		Выводит в консоль результат парсинга.
			parsed – количество успешно полученных тайтлов;\n
			not_found – количество не найденных в источнике тайтлов;\n
			errors – количество ошибок.
		"""

		Templates.header("SUMMARY")
		parsed = TextStyler(str(parsed)).colorize.green if parsed else TextStyler(str(parsed)).colorize.red
		not_found = TextStyler(str(not_found)).colorize.yellow if not_found else TextStyler(str(not_found)).colorize.green
		errors = TextStyler(str(errors)).colorize.red if errors else TextStyler(str(errors)).colorize.green
		print(f"Parsed: {parsed}. Not found: {not_found}. Errors: {errors}.")

	def title(version: str):
		"""
		Выводит в консоль заголовок ПО.
			version – версия Melon.
		"""

		Templates.header(f"Melon v{version}")