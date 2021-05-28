from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget

class CustomListView(QWidget):
	def __init__(self):
		super().__init__()

		

if __name__ == '__main__':
	import sys

	app = QApplication(sys.argv)

	sys.exit(app.exec_())