from dublib.Methods import Cls

def PrintAmendingProgress(message: str, current_state: int, max_state: int):
	"""Выводит в консоль прогресс дополнения."""

	# Очистка консоли.
	Cls()
	# Вывод в консоль: прогресс.
	print(f"{message}Amending: {current_state} / {max_state}")