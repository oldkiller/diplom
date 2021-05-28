import hashlib
import mimesis
import random

from mimesis.builtins import UkraineSpecProvider

from library.DatabaseClasses import localDB, Patient, Treatment, globalDB, \
	DoctorLoginData, Contract, GlobalTreatment, GlobalPatient

localDB.init("databases/database.db")

localDB.create_tables([Patient, Treatment])
globalDB.create_tables([GlobalPatient, Contract, DoctorLoginData, GlobalTreatment])

pers = mimesis.Person("uk")
ua = UkraineSpecProvider()
code = mimesis.Code()
date = mimesis.Datetime()

makeMD5 = lambda passwd: hashlib.md5(bytes(passwd, encoding="utf8")).hexdigest()

for i in range(10):
	print(f"Start doctor: {i}")
	passwd = pers.password(16)
	doctor = DoctorLoginData.create(
		doctorID=pers.identifier("@@@####-####"),
		doctorPassHash=makeMD5(passwd),
		doctorPassword=passwd)
	for j in range(200):
		gender = pers.gender()
		if gender == "Чол.":
			g = mimesis.enums.Gender.MALE
		else:
			g = mimesis.enums.Gender.FEMALE
		patient = GlobalPatient.create(
			patientID=pers.identifier("@@####-####-####"),
			surname=pers.surname(g),
			name=pers.name(g),
			patronymic=ua.patronymic(g),
			gender=pers.gender(g),
			birthday=str(date.date()),
			telephone=pers.telephone(),
			preferCat=random.randint(0, 3))
		Contract.create(
			contractID=pers.identifier("#####.#####.#####"),
			doctorID=doctor,
			patientID=patient)


# for _ in range():
# 	Contract.create(
# 		contractID=pers.identifier("@@-###/###")
# 	)




# try:
# 	globalDB.connect()
# 	pers = mimesis.Person("uk")
# 	for _ in range(2):
# 		DoctorLoginData.create(
# 			doctorID=pers.identifier("@@####-####"),
# 			doctorPassword=pers.password(length=16)
# 		)
# 	globalDB.close()
# except pw.OperationalError as e:
# 	print("Нет связи")

# Treatment.create(
# 	patientID="1",
# 	symptom="11Dasda",
# 	diagnose="13123",
# 	direction="13123123",
# 	data=datetime.datetime.now().strftime("%d/%m/%Y, %H:%M")
# )

# db.create_tables([Patient, Treatment])
# pers = mimesis.Person("uk")
# ua = UkraineSpecProvider()
# code = mimesis.Code()
# date = mimesis.Datetime("uk")
#
# for _ in range(1000):
#     gender = pers.gender()
#     if gender == "Чол.":
#         g = mimesis.enums.Gender.MALE
#     else:
#         g = mimesis.enums.Gender.FEMALE
#     patient = Patient(
#         ids=pers.identifier("####-###.##-#####"),
#         surname=pers.surname(g),
#         name=pers.name(g),
#         patronymic=ua.patronymic(g),
#         gender=gender,
#         birthday=str(date.date()),
#         telephone=pers.telephone(),
#         preferCat=random.randint(1, 3))
#     patient.save()
#
# print(f"pass {time.time() - start} sec")

localDB.close()
