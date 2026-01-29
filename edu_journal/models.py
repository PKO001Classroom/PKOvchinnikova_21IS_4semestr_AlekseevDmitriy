class User:
    def __init__(self, user_id, username, password, role, full_name, specialty=None, group_name=None):
        self.id = user_id
        self.username = username
        self.password = password
        self.role = role
        self.full_name = full_name
        self.specialty = specialty
        self.group_name = group_name


class Subject:
    def __init__(self, subject_id, name, code, specialty):
        self.id = subject_id
        self.name = name
        self.code = code
        self.specialty = specialty


class Grade:
    def __init__(self, grade_id, student_id, teacher_id, subject_id, grade_value, comment, date):
        self.id = grade_id
        self.student_id = student_id
        self.teacher_id = teacher_id
        self.subject_id = subject_id
        self.grade_value = grade_value
        self.comment = comment
        self.date = date