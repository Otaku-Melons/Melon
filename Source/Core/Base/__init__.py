import subprocess

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ <<<<< #
#==========================================================================================#

def GetLatestGitTag(parser: str) -> str:
	"""
	Возвращает самый свежий тега Git.
		parser – название парсера.
	"""

	return subprocess.getoutput(f"cd Parsers/{parser} && git describe --tags $(git rev-list --tags --max-count=1)")