from backend.libs.database import db

class TimeTable(db.Model):
    __tablename__ = 't_timetable'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    lesson = db.Column(db.Text)
    teacher = db.Column(db.Text)
    day_num = db.Column(db.Integer)
    begin_hour = db.Column(db.Integer)
    begin_minute = db.Column(db.Integer)
    end_hour = db.Column(db.Integer)
    end_minute = db.Column(db.Integer)

    @property
    def json(self):
        json = {
            'uid': self.uid,
            'user_id': self.user_id,
            'lesson': self.lesson,
            'teacher': self.teacher,
            'day_num': self.day_num,
            'begin_hour': self.begin_hour,
            'begin_minute': self.begin_minute,
            'end_hour': self.end_hour,
            'end_minute': self.end_minute,
        }
        return json
    # required parameters on request
    add_timetable1 = ['content']
    add_timetable = ['lesson', 'day_num', 'begin_hour', 'begin_minute', 'end_hour', 'end_minute']
    update_timetable = ['lesson', 'day_num', 'begin_hour', 'begin_minute', 'end_hour', 'end_minute']
    def update_column(self, column, value):
        setattr(self, column, value)


