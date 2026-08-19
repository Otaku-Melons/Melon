from dublib.cli.terminalyzer import ValidableTypes

from ..base_processor import PARAMS, BaseCommandProcessor

class CommandProcessorTemplate(BaseCommandProcessor[PARAMS]):
	"""Контейнер шаблонов генерации команд."""
	
	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ ГЕНЕРАЦИИ КОМАНДЫ <<<<< #
	#==========================================================================================#

	def _AddMirrorKey(self):
		"""Добавляет ключ подключения зеркала."""

		self._Command.base.add_key("--mirror", type = ValidableTypes.Domain, description = "Source mirror to requests.")

	def _AddParserPosition(self, multiple: bool = False):
		"""
		Добавляет позицию для имени парсера(ов).

		:param multiple: Указывает, должна ли позиция поддерживать множественное указание парсеров.
		:type multiple: bool
		"""

		if multiple:
			ComPos = self._Command.create_position("PARSERS", "One or more parsers names separated by comma. By default all.")
			ComPos.add_key("--use")

		else:
			ComPos = self._Command.create_position("PARSER", "Name of parser.", important = True)
			ComPos.add_key("--use")
	