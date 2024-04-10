import json
from pathlib import Path
class Student: #Введение учеников в программу
    name: str #Каждый ученик имеет имя и фамилию
    surname: str

    def __init__(self, name, surname):
        self.name = name
        self.surname = surname


class Department: #Введение факультативов в программу
    name: str #Каждый факультатив имеет имя, учителя и список учеников
    teacher: str
    students: list[Student]

    def __init__(self, name, teacher, students=[]):
        self.name = name
        self.teacher = teacher
        self.students = students

    def isMember(self, name, surname) -> bool: #Функция поиска студентов по факультативам
        for student in self.students:
            if student.name == name and student.surname == surname:
                return True
        return False

    def removeStudent(self, name, surname): #Функция удаления студентов в факультативе
        for student in self.students:
            if student.name == name and student.surname == surname:
                self.students.remove(student)

    def isExist(self, dep: []): #Функция поиска факультативов по их общему списку
        for department in dep:
            if department.name == self.name:
                return True
        return False

    def removeDepartment(self, dep: []): #Функция удаления факультативов из их общего списка
        for department in dep:
            if department.name == self.name:
                dep.remove(department)

class DataBase: #Введение класса "Вывода данных"
    def __init__(self):
        self.path = Path(__file__).parent / "database.json"

    def read(self): #Функция чтения данных "Вывода" из файла
        departments = []
        with open(self.path, 'r') as file:
            data = json.load(file)
        for dep in data["departments"]:
            departments.append(Department(dep["name"],
                                          dep["teacher"],
                                          [Student(student["name"],student["surname"]) for student in dep["students"]]
                                          )
                               )
        return departments

    def write(self, departments): #Функция записи данных "Вывода" в файл
        data = []
        for dep in departments:
            data.append({"name": dep.name ,
                         "teacher":dep.teacher,
                         "students":[{"name":x.name, "surname":x.surname} for x in dep.students]}
            )
        with open(self.path, 'w') as file:
            json.dump({"departments":data}, file, indent=4)

def main(): #Функция основного кода
    database = DataBase()
    dep = database.read()

    with open(Path(__file__).parent / "command.json",'r') as file: #Открытие файла "Ввода"
        data = json.load(file)

    command = data["command"]
    content = data["content"]
    match command:
        case "get": #Функция вывода информации из файла
            match content["type"]:
                case "student": #Проверка наличия определенного студента по имени-фамилии в определенном факультативе
                    name = content["instance"]["name"]
                    surname = content["instance"]["surname"]
                    for department in dep:
                        if department.isMember(name, surname):
                            print(f"Студент: {name} {surname} присутствует в департаменте: {department.name}")
                case "department": #Вывод списка студентов в определенном факультативе
                    department_name = content["instance"]["name"]
                    for department in dep:
                        if department.name == department_name:
                            print(f"Следующие студенты учатся в департаменте {department_name}")
                            for student in department.students:
                                print(student.name, student.surname)
                case "departments": #Вывод списка факультативов из общего списка факультативов
                    print(f"Следующие департаменты присутствуют в базе данных:")
                    for department in dep: #Вывод общей информации по определенному факультативу, название/учитель/количество студентов
                        print(f"Название: {department.name}, преподаватель: {department.teacher}, количество студентов: {len(department.students)}")
                case _:
                    raise
        case "post": #Функция ввода/удаления информации в/из файла
            match content["type"]:
                case "department":
                    match content["action"]["command"]:
                        case "addStudent": #Добавление студента по имени-фамилии в определенный факультатив
                            department_name = content["instance"]["name"]
                            student_list = content["action"]["instance"]
                            for department in dep:
                                if department.name == department_name:
                                    for student in student_list:
                                        student_name = student["name"]
                                        student_surname = student["surname"]
                                        if not department.isMember(student_name, student_surname):
                                            department.students.append(Student(name=student_name, surname=student_surname))
                                        else: #Проверка студента на наличие в определенном факультативе
                                            print(f"Студент {student_name} {student_surname} уже был в департаменте {department.name}")
                        case "deleteStudent": #Удаление студента по имени-фамилии из определенного факультатива
                            department_name = content["instance"]["name"]
                            student_name = content["action"]["instance"]["name"]
                            student_surname = content["action"]["instance"]["surname"]
                            for department in dep:
                                if department.name == department_name:
                                    if department.isMember(student_name, student_surname):
                                        department.removeStudent(student_name, student_surname)
                                    else: #Проверка студента на наличие в определенном факультативе
                                        print(f"Студента {student_name} {student_surname} в департаменте {department.name} не обнаружено.")
                        case "addDepartment": #Добавление факультатива по имени-учителю
                            name = content["instance"]["name"]
                            teacher = content["instance"]["teacher"]
                            department = Department(name=name, teacher=teacher)
                            if not department.isExist(dep):
                                dep.append(department)
                            else: #Проверка факультатива на наличие в списке факультативов
                                print(f"Департамент {name} с учителем {teacher} уже был добавлен, игнорируем команду")
                        case "deleteDepartment": #Удаление факультатива по имени-учителю
                            name = content["instance"]["name"]
                            teacher = content["instance"]["teacher"]
                            department = Department(name=name, teacher=teacher)
                            if department.isExist(dep):
                                department.removeDepartment(dep)
                            else:  #Проверка факультатива на наличие в списке факультативов
                                print(
                                    f"Департамент {name} с учителем {teacher} ещё не был добавлен, игнорируем команду")

                case _:
                    raise
        case _:
            raise
    database.write(dep)

main()