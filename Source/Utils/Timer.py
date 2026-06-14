import time

class Timer:
	"""Таймер времени исполнения."""

	def __init__(self, start: bool = False):
		"""
		Таймер времени исполнения.

		:param start: Указывает, нужно ли запустить таймер при инициализации.
		:type start: bool
		"""
		
		self.__StartTime: float | None = None

		if start: self.start()

	def end(self) -> float:
		"""
		Завершает отсчёт интервала. Возвращает количество прошедших секунд.

		:return: Время исполнения в секундах.
		:rtype: float
		:raises RuntimeError: Таймер не запущен.
		"""

		if not self.__StartTime: raise RuntimeError("Timer not started.")

		Delay = time.time() - self.__StartTime
		self.__StartTime = None

		return Delay
	
	def ends(self) -> str:
		"""
		Завершает отсчёт интервала и возвращает форматированную строку времени.

		:return: Строковое представление времени исполнения.
		:rtype: str
		"""

		OriginalDelay = self.end()
		Delay = round(OriginalDelay, 2)
		Minutes, Seconds = divmod(Delay, 60)
		Minutes = int(Minutes)
		Seconds = int(Seconds)
		
		StrMinutes = ""
		if Minutes: StrMinutes = f"{Minutes} minutes " 
		else: Seconds = Delay if Delay else round(OriginalDelay, 4)
		StrTime = f"{StrMinutes}{Seconds} seconds"

		return StrTime

	def start(self):
		"""Начинает отсчёт интервала времени."""

		self.__StartTime = time.time()