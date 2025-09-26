from flask import Flask,jsonify
import pickle
import os
import numpy as np
import pandas as pd
import firebase_admin
from firebase_admin import credentials,db
app=Flask("__name__")

model=pickle.load(open("student_dropout_model_3levels.pkl","rb"))

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
        self.exam_score=self.total_marks/400 * 100

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
        print(s.risk)





    return jsonify(data)
if __name__=='__main__':
    app.run(debug=True)