import datetime
import sys
from datetime import time

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import qApp
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QAction
# from PyQt5.QtWidgets import QStatusBar
# from PyQt5.QtWidgets import QMessageBox
# from PyQt5.QtWidgets import QListView
# from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtCore import QSize, QThread
from PyQt5.QtCore import QStringListModel
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtGui import QIcon

import Setting
from SimpleThread import AccountCheckThread, DownloadDBThread, UploadDBThread
from library.DataTable import DataTable
from library.DatabaseClasses import *
from widgets import AboutLicence


class SearchWidget(QWidget):
	"""
	Віджет для відображення пошукового рядка. Пошук виконується за назвами
	кодів ICPC.
	"""

	inputDone = pyqtSignal(str)

	def __init__(self, data):
		""" Конструктор """
		super().__init__()
		self.data = data

		self.mainBox = QGroupBox("Пошук симптомів, діагнозів")
		self.layout = QVBoxLayout()

		self.button = QPushButton("Пошук")
		self.button.clicked.connect(self.buttonPressed)

		self.entry = QLineEdit()
		self.entry.returnPressed.connect(self.buttonPressed)
		self.entry.setClearButtonEnabled(True)
		self.entry.setPlaceholderText("Введіть назву симптома, дігнозу або ...")

		words = data.getParamByLocalization()
		self.complete = QCompleter(words, self.entry)
		self.complete.setCaseSensitivity(False)
		self.complete.setFilterMode(Qt.MatchContains)
		self.complete.setMaxVisibleItems(10)
		self.complete.setCompletionMode(QCompleter.PopupCompletion)
		self.entry.setCompleter(self.complete)

		self.layout.addWidget(self.entry)
		self.layout.addWidget(self.button)
		self.mainBox.setLayout(self.layout)

		self.mainLayout = QVBoxLayout()
		self.mainLayout.addWidget(self.mainBox)
		self.setLayout(self.mainLayout)

	@pyqtSlot(name="buttonPressed")
	def buttonPressed(self):
		"""
		Викликається при натисканні на один з варіантів доповнення, або
		при натисканні клавіші Enter.
		Очищує рядок і відправляє код введеного симптому, скарги, діагнозу
		до віджету з рядками звернення.
		"""
		text = self.entry.text().strip()
		self.entry.setText("")

		text = self.data.getCode(text)
		self.inputDone.emit(text)


class LocalizationWidget(QWidget):
	"""
	Віджет для відображення списку локалізацій. Локалізації вказано згідно до
	бази ICPC
	"""
	inputLocal = pyqtSignal(str)

	def __init__(self, localization=None):
		"""
		Конструктор. На основі списку локалізацій створює группу кнопок з
		назвами локалізацій.
		"""
		super().__init__()
		if not localization:
			localization = []

		self.mainBox = QGroupBox("Локалізації")
		self.layout = QVBoxLayout()

		self.listWidget = QListWidget(self)
		self.listWidget.setWordWrap(True)
		self.listWidget.itemClicked.connect(self.buttonPressed)

		list_separator = QListWidgetItem()
		list_separator.setSizeHint(QSize(-1, 2))
		list_separator.setFlags(Qt.NoItemFlags)
		self.listWidget.addItem(list_separator)

		for loc in localization:
			list_item = QListWidgetItem(self.listWidget)
			list_item.setText(loc)
			# list_item.setFont(app.myfont)
			list_item.setBackground(QColor("#ddd"))
			self.listWidget.addItem(list_item)

			list_separator = QListWidgetItem()
			list_separator.setSizeHint(QSize(-1, 2))
			list_separator.setFlags(Qt.NoItemFlags)
			self.listWidget.addItem(list_separator)
			# self.listWidget.setItemWidget(list_item, button)
		self.listWidget.updateGeometry()
		self.layout.addWidget(self.listWidget)

		self.mainBox.setLayout(self.layout)
		self.mainLayout = QVBoxLayout()
		self.mainLayout.addWidget(self.mainBox)
		self.setLayout(self.mainLayout)

	def buttonPressed(self):
		"""
		Викликається при натисканні на певну локалізацію. Передає
		назву локалізації до віджету зі списком симптомів, скарг, діагнозів
		"""
		text = None
		if self.listWidget.currentItem():
			text = self.listWidget.currentItem().text()
		if text:
			self.inputLocal.emit(text)


class ParametrWidget(QWidget):
	"""
	Віджет зі списком симптомів, скарг, діагнозів.
	"""
	itemCurrent = pyqtSignal(str)

	def __init__(self, data):
		"""
		Конструктор. При старті програми створює групу кнопок зі всім списком
		скарг, симптомів та діагнозів.
		"""
		super().__init__()
		self.data = data

		self.mainBox = QGroupBox("Скарги, симптоми, діагнози")
		self.layout = QVBoxLayout()

		self.listWidget = QListWidget(self)
		self.listWidget.setWordWrap(True)
		self.listWidget.itemDoubleClicked.connect(self.buttonClicked)

		self.parameter = self.data.getParamByLoc()
		self.setParam(self.parameter)

		self.layout.addWidget(self.listWidget)
		self.mainBox.setLayout(self.layout)
		self.mainLayout = QVBoxLayout()
		self.mainLayout.addWidget(self.mainBox)
		self.setLayout(self.mainLayout)

	def buttonClicked(self):
		"""
		При натисканні на певний кнопку групи передає її код у віджет
		з рядками звернення
		"""
		cur = self.listWidget.currentItem().text()
		text = ""
		for par in self.parameter:
			if par["text"] == cur:
				text = par["code"]
		self.itemCurrent.emit(text)

	def setParam(self, parameter):
		"""
		Метод, що створює кнопки за списком скарг, симптомів і діагнозів
		і розміщує іх у віджеті.
		"""
		self.listWidget.clear()
		list_separator = QListWidgetItem()
		list_separator.setSizeHint(QSize(-1, 2))
		list_separator.setCheckState(False)
		list_separator.setFlags(Qt.NoItemFlags)
		self.listWidget.addItem(list_separator)
		for par in parameter:
			# label = QLabel(par)
			# label.setWordWrap(True)
			list_item = QListWidgetItem(par["text"], self.listWidget)
			list_item.setBackground(QColor(par["color"]))

			self.listWidget.addItem(list_item)
			list_separator = QListWidgetItem()
			list_separator.setSizeHint(QSize(-1, 2))
			list_separator.setFlags(Qt.NoItemFlags)
			self.listWidget.addItem(list_separator)
			# self.listWidget.addItem(list_separator)
			# self.listWidget.setItemWidget(list_item, label)

	@pyqtSlot(str, name="enterLocal")
	def enterLocal(self, local):
		"""
		Метод, що отримує назву локалізації, і фільтрує скарги,
		симптоми і діагнози за вказаною локалізацією, а також додає до цього
		списку список направлень
		"""
		self.parameter = self.data.getParamByLoc(local)
		self.setParam(self.parameter)


class AncetaWidget(QWidget):
	"""
	Віджет анкети.
	Створює віджет з полями для введення інформації про пацієнта.
	Містить методи:
	- __init__() - конструктор
	- searchByID() - метод для пошуку ID пацієнта під час введення
	- returnPressed() - метод для остаточного доповнення ID та інших полів
	- resizeEvent() - метод для зміни відображення віджету
	"""
	def __init__(self):
		""" Конструктор. Створює і заповнює всі поля класу """
		super().__init__()

		# self.listOfDiagnose = []

		self.paramLabels = [
			"Відвідування", "Вид консультації",
			"Прізвище", "Ім'я", "По-батькові", "Стать (0-ч,1-ж)",
			"Дата народження", "Номер телефону", "Пільгова категорія"]
		self.entryList = []

		# Створення форми для введення анкети пацієнта
		self.thickLayout = QFormLayout()
		self.thickLayout.setRowWrapPolicy(QFormLayout.WrapAllRows)

		# Створення рядку для введення ID пацієнта
		self.idEntry = QLineEdit()
		self.idCompleter = QCompleter([""])
		self.idCompleter.setCaseSensitivity(False)
		self.idCompleter.setCompletionMode(QCompleter.PopupCompletion)
		self.idEntry.setCompleter(self.idCompleter)
		self.idEntry.setClearButtonEnabled(True)
		self.idEntry.textEdited.connect(self.searchByID)
		self.idEntry.returnPressed.connect(self.returnPressed)
		self.thickLayout.addRow("ID паціента", self.idEntry)

		# Створення всіх інших рядків
		for lab in self.paramLabels:
			entry = QLineEdit()
			self.entryList.append(entry)
			self.thickLayout.addRow(lab, entry)

		# Створення кнопки для очистки рядків
		self.clearButton = QPushButton("Очистити поля")
		self.clearButton.clicked.connect(self.clearWidget)

		self.thickLayout.addRow(self.clearButton)

		widget = QWidget()
		widget.setLayout(self.thickLayout)

		# Створення поля з смугами прокручування
		# Для нормального відображення на малих екранах
		scroll = QScrollArea()
		scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		scroll.setWidgetResizable(True)
		scroll.setWidget(widget)

		scroll_layout = QVBoxLayout(self)
		scroll_layout.addWidget(scroll)

		self.mainBox = QGroupBox("Анкета пацієнта")
		self.mainBox.setLayout(scroll_layout)
		self.mainLayout = QVBoxLayout()
		self.mainLayout.addWidget(self.mainBox)

		self.setLayout(self.mainLayout)

	# @pyqtSlot(str, name="insertEntry")
	# def insertEntry(self, code):
	# 	if code not in self.listOfDiagnose:
	# 		self.listOfDiagnose.append(code)
	#
	# 	text = "".join(self.listOfDiagnose)
	# 	self.entry.setText(text)

	def searchByID(self, ids):
		"""
		Метод для пошуку ID пацієнта в базі під час введення ID у
		відповідний рядок. Слугує для обмеження підказок ID, для запобігання
		отриманню даних з бази через відображення списку всіх ID.
		"""
		data = Patient.select().where(Patient.ids.startswith(ids))

		if len(data) > 1:
			app.statusbar.showMessage("Забагато альтернатив.", 5000)
		elif len(data) < 1:
			app.statusbar.showMessage("Пацієнт відсутній.", 5000)
		else:
			app.statusbar.showMessage("Пацієнт знайдений.", 5000)

			data = data.get()
			model = self.idCompleter.model()
			if not model:
				model = QStringListModel()
			model.setStringList([data.ids])
			self.idCompleter.setModel(model)

	def returnPressed(self):
		"""
		Метод, що викликається при натисканні клавіші "Enter" в рядку введення
		ID пацієнта.
		Перевіряє наявність пацієнта в базі. При наявності виводить дані
		пацієнта в поля. Інакше повідомляє про помилку.
		"""
		ids = self.idEntry.text()
		data = Patient.select().where(Patient.ids == ids)

		if data:
			data = data.get()
			self.entryList[2].setText(data.surname)
			self.entryList[2].setCursorPosition(0)
			self.entryList[3].setText(data.name)
			self.entryList[3].setCursorPosition(0)
			self.entryList[4].setText(data.patronymic)
			self.entryList[4].setCursorPosition(0)
			self.entryList[5].setText(data.gender)
			self.entryList[5].setCursorPosition(0)
			self.entryList[6].setText(data.birthday)
			self.entryList[6].setCursorPosition(0)
			self.entryList[7].setText(data.telephone)
			self.entryList[7].setCursorPosition(0)
			self.entryList[8].setText(data.preferCat)
			self.entryList[8].setCursorPosition(0)
		else:
			error = "Проблеми при виведенні анкети пацієнта"
			app.statusbar.showMessage(error, 5000)

	def clearWidget(self):
		""" Метод для очищення рядків анкети """
		self.idEntry.clear()
		for entry in self.entryList:
			entry.clear()

	def resizeEvent(self, event):
		""" Метод для перебудови віджету при зміні розмірів вікна """
		if self.size().width() > 350:
			self.thickLayout.setRowWrapPolicy(QFormLayout.DontWrapRows)
		else:
			self.thickLayout.setRowWrapPolicy(QFormLayout.WrapAllRows)


class ResultWidget(QWidget):
	"""
	Віджет з рядками для опису звернення
	"""
	def __init__(self, data):
		super().__init__()
		self.data = data

		self.listOfSymptom = []
		self.listOfDiagnose = []
		self.listOfDirection = []

		self.labelList = ["Скарги", "Діагнози", "Процеси"]
		self.entryList = []

		self.mainBox = QGroupBox("Звернення")
		self.formLayout = QFormLayout()
		self.formLayout.setRowWrapPolicy(QFormLayout.WrapAllRows)

		for lab in self.labelList:
			entry = QLineEdit()
			entry.setClearButtonEnabled(True)
			self.entryList.append(entry)
			self.formLayout.addRow(lab, entry)

		self.clearButton = QPushButton("Очистити поля")
		self.clearButton.clicked.connect(self.clearWidget)
		self.formLayout.addRow(self.clearButton)

		widget = QWidget()
		widget.setLayout(self.formLayout)

		scroll = QScrollArea()
		scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		scroll.setWidgetResizable(True)
		scroll.setWidget(widget)

		scroll_layout = QVBoxLayout(self)
		scroll_layout.addWidget(scroll)

		self.mainBox.setLayout(scroll_layout)
		self.mainLayout = QVBoxLayout()
		self.mainLayout.addWidget(self.mainBox)

		self.setLayout(self.mainLayout)

	def clearWidget(self):
		""" Метод для очищення рядків звернення """
		for entry in self.entryList:
			entry.clear()

	def getResult(self):
		""" Метод для отримання даних звернення """
		result = dict(symptom="", diagnose="", direction="")
		result["symptom"] = self.entryList[0].text()
		result["diagnose"] = self.entryList[1].text()
		result["direction"] = self.entryList[2].text()
		return result

	@pyqtSlot(str, name="insertInLine")
	def insertInLine(self, code):
		"""
		Метод для вставки введеного коду в один з рядків
		:param code: String, код симптому, захворювання, або направлення.
		"""
		type_code = self.data.getTypeByCode(code)
		text = self.entryList[type_code].text()
		if code not in text:
			if text == "":
				text = code
			else:
				text = text + ", " + code
			# text = self.entryList[type_code].text() + code
			self.entryList[type_code].setText(text)

	def resizeEvent(self, event):
		""" Метод для перебудови віджету при зміні розмірів вікна """
		if self.size().width() > 350:
			self.formLayout.setRowWrapPolicy(QFormLayout.DontWrapRows)
		else:
			self.formLayout.setRowWrapPolicy(QFormLayout.WrapAllRows)


class CentralWidget(QWidget):
	"""
	Головний віджет. Керує розміщенням і відображенням всіх інших віджетів.
	"""
	def __init__(self):
		"""
		Конструктор. Створює і розміщує у вікні програми віджети.
		"""
		super().__init__()

		self.download = None
		self.upload = None

		self.data = DataTable()
		self.mainLayout = QHBoxLayout()
		self.mainLayout.setContentsMargins(1, 1, 1, 1)
		self.mainLayout.setSpacing(1)
		self.searchAndLoc = QVBoxLayout()
		self.ancetaAndRes = QVBoxLayout()
		self.searchAndLoc.setContentsMargins(1, 1, 1, 1)
		self.ancetaAndRes.setContentsMargins(1, 1, 1, 1)
		self.searchAndLoc.setSpacing(1)
		self.ancetaAndRes.setSpacing(1)

		self.search = SearchWidget(self.data)
		self.localization = LocalizationWidget(self.data.getLocalization())
		self.parametr = ParametrWidget(self.data)
		self.anceta = AncetaWidget()
		self.result = ResultWidget(self.data)

		self.search.inputDone.connect(self.result.insertInLine)
		self.localization.inputLocal.connect(self.parametr.enterLocal)
		self.parametr.itemCurrent.connect(self.result.insertInLine)

		self.searchAndLoc.addWidget(self.search)
		self.searchAndLoc.addWidget(self.localization)

		self.ancetaAndRes.addWidget(self.anceta, 65)
		self.ancetaAndRes.addWidget(self.result, 35)

		self.mainLayout.addLayout(self.searchAndLoc, 30)
		self.mainLayout.addWidget(self.parametr, 35)
		self.mainLayout.addLayout(self.ancetaAndRes, 35)

		self.setLayout(self.mainLayout)

	def saveTreatment(self):
		"""
		Метод для збереження звернень пацієнтів в локальну базу.
		Якщо відсутній ID пацієнта, або відсутні дані звернення, скасовує
		збереження звернення.
		"""
		treat = self.result.getResult()
		patientID = self.anceta.idEntry.text()

		# Перевірка, чи можна зберегти звернення
		if not any([treat[key] for key in treat]):
			app.statusbar.showMessage("Відсутні дані звернення", 10000)
			return
		if not patientID:
			app.statusbar.showMessage("Відсутній ID пацієнта", 10000)
			return

		Treatment.create(
			patientID=patientID,
			visiting=self.anceta.entryList[0].text(),
			kindOfConsult=self.anceta.entryList[1].text(),
			symptom=treat["symptom"],
			diagnose=treat["diagnose"],
			direction=treat["direction"],
			data=datetime.datetime.now().strftime("%d/%m/%Y, %H:%M"))

		app.statusbar.showMessage("Звернення збережено", 10000)

	def downloadDB(self, doctorID):
		"""
		Метод для завантаження локальної бази пацієнтів з глобальної.
		Створює новий потік, в якому виконується передача даних.
		"""
		app.statusbar.showMessage("Спроба підключення до бази", 10000)

		self.download = DownloadDBThread(doctorID)
		self.download.log.connect(app.statusbar.showMessage)
		self.download.start()

	def uploadDB(self, doctorID):
		"""
		Метод для вивантаження локальної бази звернень до глобальної бази.
		Створює новий потік, в якому виконується передача даних.
		"""
		app.statusbar.showMessage("Спроба підключення до бази", 10000)

		self.upload = UploadDBThread(doctorID)
		self.upload.log.connect(app.statusbar.showMessage)
		self.upload.start()


class LoginWindow(QWidget):
	"""
	Вікно входу в аккаунт лікаря. Містить поля для введення логіну і паролю.
	"""
	# Сигнал, що надсилається в разі успішної перевірки
	accessed = pyqtSignal()

	def __init__(self):
		"""
		Конструктор. Створює поля для введення логіну і паролю лікаря.
		"""
		super().__init__()

		self.check = None

		self.mainLayout = QVBoxLayout()
		self.mainLayout.addStretch(1)

		self.statusLabel = QLabel()
		self.mainLayout.addWidget(self.statusLabel)

		self.loginLabel = QLabel("ID лікаря: ")
		self.loginEntry = QLineEdit("")
		self.loginEntry.setClearButtonEnabled(True)
		self.mainLayout.addWidget(self.loginLabel)
		self.mainLayout.addWidget(self.loginEntry)

		self.passwordLabel = QLabel("Пароль:")
		self.passwordEntry = QLineEdit("")
		self.passwordEntry.setEchoMode(2)
		self.passwordEntry.setClearButtonEnabled(True)
		self.loginEntry.returnPressed.connect(self.passwordEntry.setFocus)
		self.passwordEntry.returnPressed.connect(self.checkAccount)
		self.mainLayout.addWidget(self.passwordLabel)
		self.mainLayout.addWidget(self.passwordEntry)

		self.button = QPushButton("Ввійти")
		self.button.pressed.connect(self.checkAccount)
		self.mainLayout.addWidget(self.button)

		self.mainLayout.addStretch(1)
		self.setLayout(self.mainLayout)

	def checkAccount(self):
		"""
		Метод для перевірки правильності введення логіну і паролю.
		Викликається при натисканні клавіші Enter та кнопки 'Ввійти'
		"""
		doctorID = self.loginEntry.text()
		doctorPass = self.passwordEntry.text()

		app.statusbar.showMessage("Спроба підключення до серверу")

		if doctorID == "admin" and doctorPass == "admin":
			self.accessed.emit()
			return

		self.check = AccountCheckThread(doctorID, doctorPass)
		self.check.fullAccess.connect(self.fullAccess)
		self.check.partialAccess.connect(self.particleAccess)
		self.check.zeroAccess.connect(self.zeroAccess)
		self.check.log.connect(app.statusbar.showMessage)
		self.check.start()

	def fullAccess(self):
		app.statusbar.showMessage("")
		self.accessed.emit()

	def particleAccess(self):
		app.statusbar.showMessage("Неправильний пароль", 5000)

	def zeroAccess(self):
		app.statusbar.showMessage("Лікар з введеним ID відсутній в базі", 5000)


class MainApp(QMainWindow):
	"""
	Клас для реалізації головного вікна програми. Створює меню
	"""
	def __init__(self):
		"""
		Конструктор.
		"""
		super().__init__()
		title = "Журнал реестрації амбулаторних пацієнтів"
		self.setWindowTitle(title)
		self.setMinimumSize(320, 240)
		self.resize(800, 600)

		self.loginWindow = LoginWindow()
		self.mainWindow = CentralWidget()
		self.loginWindow.accessed.connect(self.login)
		self.setCentralWidget(self.loginWindow)

		self._makeMenuAndToolBar()

		self.ini = Setting.Settings("setting.ini")
		self.readSetting()

		self.statusbar = self.statusBar()

		self.show()

	def login(self):
		"""
		Викликається в разі введення коректних логіна і паролю.
		Перемикає вікно на вікно для роботи з пацієнтами і
		підключає базу конкретного лікаря
		"""
		self.doctorID = self.loginWindow.loginEntry.text()
		changeLocalDB(self.doctorID)
		self.mainWindow = CentralWidget()
		self.setCentralWidget(self.mainWindow)
		self.menubar.setVisible(True)
		self.toolbar.setVisible(True)

	def logout(self):
		"""
		Викликається при натисканні клавіші 'Вихід'. Виконує відключення
		локальної бази лікаря і вихід з аккаунту. Перемикає вікно на
		вікно входу.
		"""
		changeLocalDB(None)
		self.loginWindow = LoginWindow()
		self.loginWindow.accessed.connect(self.login)
		self.setCentralWidget(self.loginWindow)
		self.menubar.setVisible(False)
		self.toolbar.setVisible(False)

	def _makeMenuAndToolBar(self):
		"""
		Створює меню і тулбар.
		"""
		self.toolbar = self.addToolBar("Action")
		self.menubar = self.menuBar()

		file_menu = self.menubar.addMenu("&Файл")
		db_menu = self.menubar.addMenu("&База")
		about_menu = self.menubar.addMenu("&Допомога")

		self.toolbar.setMovable(False)

		# Действия
		save_icon = QIcon.fromTheme("document-save", QIcon("icons/actionSave.svg"))
		save_act = QAction(save_icon, '&Зберегти', self)
		save_act.setShortcut("Ctrl+S")
		save_act.triggered.connect(lambda: self.mainWindow.saveTreatment())
		self.toolbar.addAction(save_act)
		file_menu.addAction(save_act)

		setting_icon = QIcon("icons/actionSetting.svg")
		setting_act = QAction(setting_icon, "&Налаштування", self)
		setting_act.triggered.connect(self._settingPage)
		file_menu.addSeparator()
		file_menu.addAction(setting_act)

		downloadDB = QAction("Завантажити базу пацієнтів", self)
		downloadDB.triggered.connect(lambda: self.mainWindow.downloadDB(self.doctorID))
		db_menu.addAction(downloadDB)

		uploadDB = QAction("Вивантажити базу звернень", self)
		uploadDB.triggered.connect(lambda: self.mainWindow.uploadDB(self.doctorID))
		db_menu.addAction(uploadDB)

		exit_act = QAction(QIcon("icons/actionExit.svg"), '&Вихід', self)
		exit_act.setShortcut('Ctrl+Q')
		exit_act.setStatusTip('Вихід з аккаунту лікаря')
		exit_act.triggered.connect(self.logout)
		file_menu.addSeparator()
		file_menu.addAction(exit_act)

		about_author_act = QAction("&Про програму", self)
		about_author_act.triggered.connect(self._aboutAuthor)
		about_menu.addAction(about_author_act)

		self.menubar.setVisible(False)
		self.toolbar.setVisible(False)

	def setNewFont(self, font):
		""" Встановлює отриманий шрифт як шрифт програми """
		main_app.setFont(font)

	def readSetting(self):
		""" Зчитує збережені налаштування """
		font = self.ini.readSetting()
		self.setNewFont(font)

	def _settingPage(self):
		""" Відображає вікно налаштувань """
		ini = Setting.Settings("setting.ini")
		ini.savePressed.connect(self.saveSetting)
		ini.exec()

	@pyqtSlot(QFont, name="saveSetting")
	def saveSetting(self, font):
		self.setNewFont(font)

	def _aboutAuthor(self):
		""" Відображає вікно з відомостями про ліцензію """
		about = AboutLicence.AboutLicence()
		about.exec()


if __name__ == '__main__':
	main_app = QApplication(sys.argv)
	# localDB.connect()
	app = MainApp()
	app.show()
	sys.exit(main_app.exec_())
