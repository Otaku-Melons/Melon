from dublib.StyledPrinter import StyledPrinter, Styles, TextStyler
from prettytable import PLAIN_COLUMNS, PrettyTable

def ParsersTable(columns: dict[str, list], sort_by: str = "NAME"):
	# Инициализация таблицы.
	TableObject = PrettyTable()
	TableObject.set_style(PLAIN_COLUMNS)
	# Колонки имплементаций.
	Implementations = ["collect", "get_updates", "repair"]
	# Строки подстановки статусов.
	ImplementationStatuses = {
		True: TextStyler("true", text_color = Styles.Colors.Green),
		False: TextStyler("false", text_color = Styles.Colors.Red)
	}

	# Для каждого сайта.
	for SiteIndex in range(len(columns["SITE"])):
		# Стилизация сайта курсивом.
		columns["SITE"][SiteIndex] = TextStyler(columns["SITE"][SiteIndex], decorations = [Styles.Decorations.Italic])

	# Для каждой колонки имплементации.
	for ColumnName in Implementations:

		# Для каждой имплементации.
		for StatusIndex in range(len(columns[ColumnName])):
			# Стилизация цветом.
			columns[ColumnName][StatusIndex] = ImplementationStatuses[columns[ColumnName][StatusIndex]]

	# Для каждого столбца.
	for ColumnName in columns.keys():
		# Буфер стилизации названия колонки.
		Buffer = TextStyler(ColumnName, decorations = [Styles.Decorations.Bold])
		# Парсинг столбца.
		TableObject.add_column(Buffer, columns[ColumnName])

	# Установка стилей таблицы.
	TableObject.align = "l"
	TableObject.sortby = TextStyler(sort_by, decorations = [Styles.Decorations.Bold])
	# Вывод таблицы.
	print(TableObject)