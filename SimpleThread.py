import hashlib

from PyQt5.QtCore import QThread, pyqtSignal
from peewee import OperationalError

from library.DatabaseClasses import DoctorLoginData, LocalDoctor, \
	GlobalPatient, Contract, Patient, GlobalTreatment, Treatment


class AccountCheckThread(QThread):
	"""
	Клас для реалізації потоку для перевірки введених даних
	спочатку в локальній базі, потім на віддаленому сервері.
	"""
	# Сигнал успішної перевірки даних
	fullAccess = pyqtSignal()
	# Сигнал, що введено неправильний пароль
	partialAccess = pyqtSignal()
	# Сигнал, що введений аккаунт відсутній
	zeroAccess = pyqtSignal()
	log = pyqtSignal(str)

	def __init__(self, login=None, passwd=None):
		""" Конструктор. Зберігає передані логін і пароль. """
		QThread.__init__(self)
		self.login = login
		self.passwd = passwd

	def run(self):
		"""
		Метод спочатку перевіряє наявність збережених даних акаунтів в
		локальній базі. За наявності передає відповідний сигнал, інакше
		виконує запит до глобальної бази.
		"""
		bytesPasswdHash = bytes(self.passwd, encoding="utf-8")
		passwdHash = hashlib.md5(bytesPasswdHash).hexdigest()

		# Запит до локальної бази
		localDoctor = LocalDoctor.select().where(
			(LocalDoctor.doctorID == self.login) &
			(LocalDoctor.passwdHash == passwdHash))
		localDoctorPart = LocalDoctor.select().where(
			LocalDoctor.doctorID == self.login)

		try:
			if localDoctor:
				self.fullAccess.emit()
				return
			elif localDoctorPart:
				self.partialAccess.emit()
				return
		except OperationalError:
			self.log.emit("Відсутнє підключення до серверу")

		# Звернення до глобальної бази
		doctor = DoctorLoginData.select().where(
			(DoctorLoginData.doctorID == self.login) &
			(DoctorLoginData.doctorPassHash == passwdHash))
		try:
			if doctor:
				LocalDoctor.create(
					doctorID=self.login,
					passwdHash=passwdHash)
				self.fullAccess.emit()
				return
		except OperationalError:
			self.log.emit("Відсутнє підключення до серверу")
			return

		doctor = DoctorLoginData.select().where(
			DoctorLoginData.doctorID == self.login)
		try:
			if doctor:
				self.partialAccess.emit()
			else:
				self.zeroAccess.emit()
		except OperationalError:
			self.log.emit("Відсутнє підключення до серверу")


class DownloadDBThread(QThread):
	"""
	Клас для завантаження бази пацієнтів конкретного лікаря в окремому потоці.
	"""
	log = pyqtSignal(str)

	def __init__(self, login=None):
		""" Конструктор. Зберігає логін. """
		QThread.__init__(self)
		self.login = login

	def run(self):
		"""
		Метод, що завантажує базу пацієнтів.
		"""
		patients = GlobalPatient.select()\
			.join(Contract)\
			.join(DoctorLoginData)\
			.where(Contract.doctorID.doctorID == self.login)
		if not patients:
			self.log.emit("Не вдалося завантажити базу пацієнтів")
			return

		self.log.emit("Розпочато завантаження бази пацієнтів")
		for patient in patients:
			locpat = Patient.select().where(Patient.ids == patient.patientID)
			if locpat.exists():
				continue
			Patient.create(
				ids=patient.patientID,
				surname=patient.surname,
				name=patient.name,
				patronymic=patient.patronymic,
				gender=patient.gender,
				birthday=patient.birthday,
				telephone=patient.telephone,
				preferCat=patient.preferCat)
		self.log.emit("Успішно завантажено базу пацієнтів")


class UploadDBThread(QThread):
	"""
	Клас для вивантаження бази звернень в глобальну базу в окремому потоці
	"""
	log = pyqtSignal(str)

	def __init__(self, doctorID):
		""" Конструктор. Зберігає переданий ID лікаря """
		QThread.__init__(self)
		self.doctorID = doctorID

	def run(self):
		""" Метод для вивантаження бази """
		self.log.emit("Спроба вивантажити базу звернень", 5000)
		treatments = Treatment.select()
		for treatment in treatments:
			GlobalTreatment.create(
				doctorID=self.doctorID,
				patientID=treatment.patientID,
				visiting=treatment.visiting,
				kindOfConsult=treatment.kindOfConsult,
				symptom=treatment.symptom,
				diagnose=treatment.diagnose,
				direction=treatment.direction,
				data=treatment.data)
		self.log.emit("Базу звернень вивантажено", 5000)
