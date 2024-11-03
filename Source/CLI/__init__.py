from dublib.CLI.StyledPrinter import Styles, TextStyler
from prettytable import PLAIN_COLUMNS, PrettyTable

class Templates:
	"""Набор шаблонов ввода-вывода."""

	#==========================================================================================#
	# >>>>> СТИЛИЗАТОРЫ <<<<< #
	#==========================================================================================#

	def bold(text: str) -> str:
		"""
		Возвращает стилизованный текст: полужирный.
			text – текст.
		"""

		return TextStyler(text, decorations = [Styles.Decorations.Bold])

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

		status = TextStyler("enabled", text_color = Styles.Colors.Green) if status else TextStyler("disabled", text_color = Styles.Colors.Red)
		print(f"{text}: {status}")

	def parsers_table(columns: dict[str, list], sort_by: str = "NAME"):
		"""
		Выводит в консоль форматированную таблицу установленных парсеров.
			columns – данные для вывода;\n
			sort_by – название колонки для сортировки.
		"""

		TableObject = PrettyTable()
		TableObject.set_style(PLAIN_COLUMNS)
		Implementations = ["collect", "image"]
		ImplementationStatuses = {
			True: TextStyler("true", text_color = Styles.Colors.Green),
			False: TextStyler("false", text_color = Styles.Colors.Yellow),
			None: TextStyler("error", text_color = Styles.Colors.Red),
		}

		for SiteIndex in range(len(columns["SITE"])):
			columns["SITE"][SiteIndex] = TextStyler(columns["SITE"][SiteIndex], decorations = [Styles.Decorations.Italic])

		for ColumnName in Implementations:

			for StatusIndex in range(len(columns[ColumnName])):
				columns[ColumnName][StatusIndex] = ImplementationStatuses[columns[ColumnName][StatusIndex]]

		for ColumnName in columns.keys():
			Buffer = TextStyler(ColumnName, decorations = [Styles.Decorations.Bold])
			TableObject.add_column(Buffer, columns[ColumnName])

		TableObject.align = "l"
		TableObject.sortby = TextStyler(sort_by, decorations = [Styles.Decorations.Bold])
		TableObject = str(TableObject).strip()
		Link = TextStyler("https://github.com/Otaku-Melons", decorations = [Styles.Decorations.Underlined])
		print(TableObject if TableObject else f"Parsers not installed. See {Link} for more info.")

	def parsing_summary(parsed: int, not_found: int, errors: int):
		"""
		Выводит в консоль результат парсинга.
			parsed – количество успешно полученных тайтлов;\n
			not_found – количество не найденных в источнике тайтлов;\n
			errors – количество ошибок.
		"""

		Templates.header("SUMMARY")
		parsed = TextStyler(str(parsed), text_color = Styles.Colors.Green) if parsed else TextStyler(str(parsed), text_color = Styles.Colors.Red)
		not_found = TextStyler(str(not_found), text_color = Styles.Colors.Yellow) if not_found else TextStyler(str(not_found), text_color = Styles.Colors.Green)
		errors = TextStyler(str(errors), text_color = Styles.Colors.Red) if errors else TextStyler(str(errors), text_color = Styles.Colors.Green)
		print(f"Parsed: {parsed}. Not found: {not_found}. Errors: {errors}.")

	def title(version: str):
		"""
		Выводит в консоль заголовок ПО.
			version – версия Melon.
		"""

		Templates.header(f"Melon v{version}")
		