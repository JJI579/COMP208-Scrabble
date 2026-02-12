import logging
import os

logsDir = os.path.join(os.path.dirname(__file__), 'logs')

class APILogger:
	def __init__(self, name: str = 'API', logFileName: str = 'api.log', formatString = "[API]"):
		os.makedirs(logsDir, exist_ok=True)
		self.logger = logging.getLogger(name)
		self.logger.setLevel(logging.INFO)
		self.logger.handlers.clear()
		logFormat = logging.Formatter(f'{formatString} (%(asctime)s) : %(message)s')
		consoleHandler = logging.StreamHandler()
		consoleHandler.setFormatter(logFormat)
		self.logger.addHandler(consoleHandler)
		logFilePath = os.path.join(logsDir, logFileName)
		fileHandler = logging.FileHandler(logFilePath)
		fileHandler.setFormatter(logFormat)
		self.logger.addHandler(fileHandler)
	
	def info(self, message: str):
		self.logger.info(message)
	
	def warning(self, message: str):
		self.logger.warning(message)
	
	def error(self, message: str):
		self.logger.error(message)
	
	def debug(self, message: str):
		self.logger.debug(message)

class WebsocketLogger(APILogger):

	def __init__(self, name: str = 'WebsocketLogger', logFileName: str = 'websocket.log', formatString="[WEBSOCKET]"):
		super().__init__(name, logFileName, formatString)
