from PyQt5.QtCore import QSettings, Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QFormLayout, QListWidget, QApplication, \
	QDialog, QComboBox, QSpinBox, QDialogButtonBox, QPushButton


class Settings(QDialog):
	"""
	Вікно для налаштувань шрифту
	Дає змогу налаштувати шрифт і кегль шрифту
	"""
	savePressed = pyqtSignal(QFont)

	def __init__(self, iniFile):
		""" Конструктор """
		super(Settings, self).__init__()

		self.ini = None
		self.fontSize = None
		self.fontName = None
		self.listWidget = QListWidget()

		self.setWindowTitle("Настройки")

		self.ini = QSettings(iniFile, QSettings.IniFormat)
		self.ini.setIniCodec("utf-8")

		self.readSetting()

		self.inputFont = QComboBox()
		self.inputFont.addItems([
			"MS Shell Dlg 2",
			"Consolas",
			"Times New Roman"
		])

		self.inputSize = QSpinBox()
		self.inputSize.setRange(5, 30)
		self.inputSize.setValue(int(self.fontSize))

		self.settingLayout = QFormLayout()
		self.settingLayout.addRow("Шрифт: ", self.inputFont)
		self.settingLayout.addRow("Розмір: ", self.inputSize)

		self.buttonBox = QDialogButtonBox(Qt.Horizontal)
		self.buttonBox.accepted.connect(self.reAccept)
		self.buttonBox.rejected.connect(self.reject)

		buttonSave = QPushButton("Зберегти")
		buttonSave.setDefault(True)
		buttonCancel = QPushButton("Відмінити")

		self.buttonBox.addButton(buttonSave, QDialogButtonBox.AcceptRole)
		self.buttonBox.addButton(buttonCancel, QDialogButtonBox.RejectRole)

		self.mainLayout = QVBoxLayout()
		self.mainLayout.addLayout(self.settingLayout)
		self.mainLayout.addWidget(self.buttonBox)

		self.setLayout(self.mainLayout)

	def reAccept(self):
		"""
		Метод, що викликається при підтвердженні зміни налаштувань шрифту
		Надсилає до головної програми новий об'єкт шрифту, після чого викликає
		надсилає сигнал про підтвердження операції.
		"""
		self.fontName = self.inputFont.currentText()
		self.fontSize = self.inputSize.value()
		font = QFont(self.fontName, self.fontSize)
		self.savePressed.emit(font)
		self.saveSetting()
		self.accept()

	def readSetting(self):
		"""
		Метод для читання збережених налаштувань при запуску програми
		:return: QFont, збережений шрифт
		"""
		self.ini.beginGroup("Font")
		self.fontName = self.ini.value("font", "MS Shell Dlg 2")
		self.fontSize = self.ini.value("size", "10")
		self.ini.endGroup()

		font = QFont(self.fontName, int(self.fontSize))
		return font

	def saveSetting(self):
		""" Метод для збереження налаштувань шрифту """
		self.ini.beginGroup("Font")
		self.ini.setValue("font", self.fontName)
		self.ini.setValue("size", self.fontSize)
		self.ini.endGroup()


if __name__ == "__main__":
	import sys
	app = QApplication(sys.argv)
	setting = Settings("setting.ini")
	# setting.exec()
	print(setting.exec())

	sys.exit(app.exec_())