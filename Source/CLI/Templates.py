from dublib.CLI.StyledPrinter import Styles, TextStyler
from prettytable import PLAIN_COLUMNS, PrettyTable

def ParsersTable(columns: dict[str, list], sort_by: str = "NAME"):
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