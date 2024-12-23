import time

class Timer:
	"""Таймер времени исполнения."""

	def __init__(self, start: bool = False):
		"""
		Таймер времени исполнения.
			start – автоматический запуск таймера сразу после инициализации.
		"""
		
		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__StartTime = None

		if start: self.start()

	def end(self) -> float:
		"""Завершает отсчёт интервала. Возвращает количество прошедших секунд."""

		Delay = time.time() - self.__StartTime
		self.__StartTime = None

		return Delay
	
	def ends(self) -> str:
		"""Завершает отсчёт интервала и возвращает форматированную строку времени."""

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
	
	def done(self):
		"""Останавливает таймер и выводит в консоль время исполнения."""

		print("Done in " + self.ends() + ".")

	def start(self):
		"""Начинает отсчёт интервала времени."""

		self.__StartTime = time.time()