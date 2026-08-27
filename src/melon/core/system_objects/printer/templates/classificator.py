from typing import TYPE_CHECKING

from dublib.cli.text_styler import FastStyler

from ._base import _BaseTemplatesSection

if TYPE_CHECKING:
	from .....utils.classificator import ClassificationResult

class ClassificatorTemplates(_BaseTemplatesSection):
	"""Расширенные шаблоны вывода: оператор обработки классификаторов."""

	def result(self, result: "ClassificationResult"):
		"""
		Шаблон вывода: оператор обработки классификаторов.

		:param result: Результат обработки классификатора.
		:type result: ClassificationResult
		"""

		ResultDict = result.to_dict()

		for Key in ResultDict:

			if Key == "is_procedure_found":
				if result.is_procedure_found:
					self.printer.emit(FastStyler("is_procedure_found: ").decorate.bold, end_line = False)
					self.printer.emit(FastStyler("True").colorize.green)
					continue
				else:
					self.printer.emit(FastStyler("is_procedure_found:").decorate.bold, end_line = False)
					self.printer.emit(FastStyler("False").colorize.red)
					return
			
			self.printer.emit(FastStyler(f"{Key}:").decorate.bold, ResultDict[Key])

