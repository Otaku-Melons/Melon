import time

class Timer:
	"""Таймер времени исполнения."""

	def __init__(self):
		"""Таймер времени исполнения."""
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__StartTime = None

	def end(self) -> float:
		"""Завершает отсчёт интервала. Возвращает количество прошедших секунд."""

		Delay = time.time() - self.__StartTime
		self.__StartTime = None

		return Delay
	
	def ends(self) -> str:
		"""Завершает отсчёт интервала и возвращает форматированную строку времени."""

		Delay = self.end()
		Delay = round(Delay, 2)
		Minutes, Seconds = divmod(Delay, 60)
		Minutes = int(Minutes)
		Seconds = int(Seconds)
		
		StrMinutes = ""
		if Minutes: StrMinutes = f"{Minutes} minutes " 
		else: Seconds = Delay
		StrTime = f"{StrMinutes}{Seconds} seconds"

		return StrTime

	def start(self):
		"""Начинает отсчёт интервала времени."""

		self.__StartTime = time.time()