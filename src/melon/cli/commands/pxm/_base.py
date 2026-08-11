from ..base_processor import _PARAMS, BaseCommandProcessor

class CommandProcessorTemplate(BaseCommandProcessor[_PARAMS]):
	"""Контейнер шаблонов генерации команд."""
	
	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ ГЕНЕРАЦИИ КОМАНДЫ <<<<< #
	#==========================================================================================#

	def _AddParserPosition(self):
		"""Добавляет позицию имени парсера, используюмую **pxm**."""

		ComPos = self._Command.create_position("PARSER", "Parser name.", important = True)
		ComPos.set_argument()
	