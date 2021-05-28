from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QDialogButtonBox, \
	QPushButton, QDialog, QVBoxLayout


class AboutLicence(QDialog):
	"""
	Клас для створення вікна з інформацією про ліцензійне використання
	"""
	def __init__(self):
		super().__init__()

		self.mainLayout = QVBoxLayout()

		text = "«INTERNATIONAL CLASSIFICATION OF PRIMARY CARE (ICPC-2-E)»\n" + \
				"«Copyright © WONCA [2016]»\n" + \
				"«World Organization of National Colleges, Academies and " + \
				"Academic Associations" + \
				"of General Practitioners/Family Physicians»,"
		self.mainLabel = QLabel(text)
		self.mainLabel.setAlignment(Qt.AlignCenter)
		self.mainLayout.addWidget(self.mainLabel)

		self.buttonBox = QDialogButtonBox(Qt.Horizontal)
		self.buttonBox.accepted.connect(self.accept)

		self.buttonOk = QPushButton("Зрозуміло")
		self.buttonBox.addButton(self.buttonOk, QDialogButtonBox.AcceptRole)
		self.mainLayout.addWidget(self.buttonBox)

		self.setLayout(self.mainLayout)
