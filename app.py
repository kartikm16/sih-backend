from flask import Flask,jsonify,request
import pickle
import os
import numpy as np
import pandas as pd
import firebase_admin
from firebase_admin import credentials,db
from flask_cors import CORS 
import requests
app=Flask("__name__")

CORS(app, resources={r"/*": {"origins": r"http://localhost:3000+"}}, supports_credentials=True)


model=pickle.load(open("D:/SIH Hackathon Backend/backend/student_dropout_model_3levels.pkl","rb"))


base_dir=os.path.dirname(os.path.abspath(__file__))
cred_path=os.path.join(base_dir,"tech810servicekey.json")
cred=credentials.Certificate(cred_path)

firebase_admin.initialize_app(cred,{
    "databaseURL":"https://sih-tech810-default-rtdb.firebaseio.com/"
})
class Student:
    def __init__(self,key,value):
        self.attendance=value['attendance']
        self.fees_pending=value['fees_pending']
        self.family_income=value['family_income']
        self.kt=value['kt']
        self.key=key
        self.risk=""
        self.total_marks=0
        for mark in value['marks'].values():
            self.total_marks=self.total_marks+mark
        self.exam_score=self.total_marks/(len(value['marks'])*100) * 100
        print(self.exam_score)

    def predict_risk(self):
            student_data=pd.DataFrame([[self.attendance,self.exam_score , self.fees_pending, self.family_income, self.kt]],columns=['attendance', 'exam_score', 'fees_pending', 'family_income', 'backlogs'])
            self.risk=risk_labels[model.predict(student_data)[0]]
    def update_db(self):
            ref = db.reference(f'students/{self.key}')
            ref.update({
            "risk_status":self.risk,
        })




risk_labels = {0: 'Low Risk', 1: 'Medium Risk', 2: 'High Risk'}


@app.route('/')
def home():
    return "heo"

@app.route('/predict')
def predict():
    ref=db.reference('students')
    data=ref.get()
    if isinstance(data, dict):
        values = data.items()
    elif isinstance(data, list):
        values = [(i, item) for i, item in enumerate(data) if item is not None]
    else:
        values = []
    for key,value in values:
        s=Student(key,value)
        s.predict_risk()
        s.update_db()

    return jsonify(data)
@app.route('/uploadexcel', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        df = pd.read_excel(file)

        # Convert all column names to lower case to avoid KeyErrors
        df.columns = [col.lower() for col in df.columns]

        df = pd.read_excel(file)
        rows = [row.to_dict() for _, row in df.iterrows()]
        print(rows[0])
        id=-1
        for student in rows:
             id=id+1
             student_ref = db.reference(f'students/{id}')
             ref=db.reference(f'students/{id}')
             ref.update({
                  'name':student['name'],
                  'class':student['class'],
                  'kt':student['kt'],
                  'family_income':student['family_income'],
                  'fees_pending':student['fees_pending'],
                  'student_id':student['student_id'],
                  'attendance':student['attendance']
             })
             marks_ref = student_ref.child('marks')
             marks_ref.update({
                'Maths': student['maths'],
                'English': student['english'],
                'Chemistry': student['chemistry'],
                'Physics': student['physics']
             })
            

             
             
             
        # root_ref = db.reference('students')
        # # You can start id from current number of students
        # current_ids = root_ref.get() or {}
        # next_id = len(current_ids)

        # for student in rows:
        #     student_ref = root_ref.child(str(next_id))
        #     student_ref.update({
        #         "name": student.get('name', ''),
        #         "attendance": student.get('attendance', 0),
        #         "class": student.get('class', ''),
        #         "family_income": student.get('family_income', 0),
        #         "fees_pending": student.get('fees_pending', 0),
        #         "kt": student.get('kt', 0),
        #     })
        #     # Update nested marks safely
        #     marks_ref = student_ref.child('marks')
        #     marks_ref.update({
        #         "Maths": student.get('maths', 0),
        #         "English": student.get('english', 0),
        #         "Chemistry": student.get('chemistry', 0),
        #         "Physics": student.get('physics', 0)
        #     })

        #     next_id += 1

        return jsonify({"message": f"{len(rows)} students added/updated successfully"})

        
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
     
@app.route('/read')
def read():
     ref=db.reference('students')
     data=ref.get()
     return jsonify(data)
if __name__=='__main__':
    app.run(debug=True,port=5000)