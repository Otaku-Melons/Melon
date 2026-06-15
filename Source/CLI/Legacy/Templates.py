from dublib.CLI.TextStyler.FastStyler import FastStyler

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from dublib.Engine.Bus import ExecutionResult







def ParsingSummary(parsed: int, not_found: int, errors: int):
	"""
	Выводит в терминал результат парсинга.
		parsed – количество успешно полученных тайтлов;\n
		not_found – количество не найденных в источнике тайтлов;\n
		errors – количество ошибок.
	"""

	print("===== SUMMARY =====")
	parsed = FastStyler(str(parsed)).colorize.green if parsed else FastStyler(str(parsed)).colorize.red
	not_found = FastStyler(str(not_found)).colorize.yellow if not_found else FastStyler(str(not_found)).colorize.green
	errors = FastStyler(str(errors)).colorize.red if errors else FastStyler(str(errors)).colorize.green
	print(f"Parsed: {parsed}. Not found: {not_found}. Errors: {errors}.")