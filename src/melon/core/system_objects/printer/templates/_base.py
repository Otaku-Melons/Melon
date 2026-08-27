from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ...printer import Printer

class _BaseTemplatesSection:
	"""Базовая секция шаблонов."""

	@property
	def printer(self) -> "Printer":
		"""Оператор вывода."""

		return self._Printer

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		pass

	def __init__(self, printer: "Printer"):
		"""
		Базовая секция шаблонов.

		:param printer: Оператор вывода.
		:type printer: Printer
		"""

		self._Printer = printer

		self._PostInitMethod()
