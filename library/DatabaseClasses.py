import os

import peewee as pw

# from playhouse.sqlcipher_ext import SqlCipherDatabase
#
# localCipher = SqlCipherDatabase(None)

if not os.path.exists("databases"):
	os.makedirs("databases")

doctorsDB = pw.SqliteDatabase("databases/doctors.db")

localDB = pw.SqliteDatabase(None)
globalDB = pw.PostgresqlDatabase(
	"postgres",
	user="postgres",
	password="postgres",
	host="104.248.18.7",
	port=5432
)


def changeLocalDB(name):
	if name is None:
		localDB.init(None)
		return
	localDB.init(f"databases/Database{name}.db")
	localDB.create_tables([Patient, Treatment])


class _LocalTable(pw.Model):
	class Meta:
		database = localDB


class _GlobalTable(pw.Model):
	class Meta:
		database = globalDB


class Patient(_LocalTable):
	ids = pw.TextField(primary_key=True)
	surname = pw.TextField()
	name = pw.TextField()
	patronymic = pw.TextField()
	gender = pw.TextField()
	birthday = pw.TextField()
	telephone = pw.TextField()
	preferCat = pw.TextField()


class Treatment(_LocalTable):
	patientID = pw.ForeignKeyField(Patient)
	visiting = pw.TextField()
	kindOfConsult = pw.TextField()
	symptom = pw.TextField()
	diagnose = pw.TextField()
	direction = pw.TextField()
	data = pw.DateTimeField()


class DoctorLoginData(_GlobalTable):
	doctorID = pw.TextField(primary_key=True)
	doctorPassHash = pw.TextField()
	doctorPassword = pw.TextField()


class GlobalPatient(_GlobalTable):
	patientID = pw.TextField(primary_key=True)
	surname = pw.TextField()
	name = pw.TextField()
	patronymic = pw.TextField()
	gender = pw.TextField()
	birthday = pw.TextField()
	telephone = pw.TextField()
	preferCat = pw.TextField()


class Contract(_GlobalTable):
	contractID = pw.TextField(primary_key=True)
	doctorID = pw.ForeignKeyField(DoctorLoginData)
	patientID = pw.ForeignKeyField(GlobalPatient)


class GlobalTreatment(_GlobalTable):
	doctorID = pw.ForeignKeyField(DoctorLoginData)
	patientID = pw.ForeignKeyField(GlobalPatient)
	visiting = pw.TextField()
	kindOfConsult = pw.TextField()
	symptom = pw.TextField()
	diagnose = pw.TextField()
	direction = pw.TextField()
	data = pw.DateTimeField()


class LocalDoctor(pw.Model):
	doctorID = pw.TextField(primary_key=True)
	passwdHash = pw.TextField()

	class Meta:
		database = doctorsDB
