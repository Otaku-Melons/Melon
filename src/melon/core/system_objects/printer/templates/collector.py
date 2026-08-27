from ._base import _BaseTemplatesSection

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

