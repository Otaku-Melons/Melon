from dublib.Methods import Cls

def PrintAmendingProgress(message: str, current_state: int, max_state: int):
	"""
	Выводит в консоль прогресс дополнение глав информацией о содержимом.
		message – сообщение из внешнего обработчика;
		current_state – индекс текущей дополняемой главы;
		max_state – количество глав, которые необходимо дополнить.
	"""

	# Очистка консоли.
	Cls()
	# Вывод в консоль: прогресс.
	print(f"{message}\nAmending: {current_state} / {max_state}")