from dublib.CLI.TextStyler import FastStyler

from typing import TYPE_CHECKING

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