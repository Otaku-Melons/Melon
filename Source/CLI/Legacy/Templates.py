from dublib.CLI.TextStyler.FastStyler import FastStyler

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from dublib.Engine.Bus import ExecutionResult

def CachingSummary(result: "ExecutionResult"):
	"""
	Выводит в консоль результат кэширования пар ID-алиас тайтлов.

	:param result: Результат кэширования.
	:type result: ExecutionResult
	"""

	Total = result["total"]
	InCache = result["in_cache"]
	Cached = result["cached"]
	Errors: tuple[str] = result["errors"]

	print(f"Total: {Total}. Found in cache: {InCache} Cached: {Cached}.")

	if Errors:
		print(FastStyler("Errors:").decorate.bold)
		for Error in Errors: print(" - " + FastStyler(Error + ".json").colorize.red)



def ParsingProgress(index: int, count: int):
	"""
	Выводит прогресс обработки множества элементов.
		index – индекс обрабатываемого элемента;\n
		count – количество жлементов.
	"""

	Number = index + 1
	Progress = round(Number / count * 100, 2)
	Number = FastStyler(str(Number)).colorize.magenta
	if str(Progress).endswith(".0"): Progress = str(int(Progress))
	elif len(str(Progress).split(".")[-1]) == 1: Progress = str(Progress) + "0"
	else: Progress = str(Progress)
	Progress = FastStyler(Progress + "%").colorize.cyan
	print(f"[{Number} / {count} | {Progress}] ", end = "")

def ParsingSummary(parsed: int, not_found: int, errors: int):
	"""
	Выводит в консоль результат парсинга.
		parsed – количество успешно полученных тайтлов;\n
		not_found – количество не найденных в источнике тайтлов;\n
		errors – количество ошибок.
	"""

	print("===== SUMMARY =====")
	parsed = FastStyler(str(parsed)).colorize.green if parsed else FastStyler(str(parsed)).colorize.red
	not_found = FastStyler(str(not_found)).colorize.yellow if not_found else FastStyler(str(not_found)).colorize.green
	errors = FastStyler(str(errors)).colorize.red if errors else FastStyler(str(errors)).colorize.green
	print(f"Parsed: {parsed}. Not found: {not_found}. Errors: {errors}.")