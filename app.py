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



risk_labels = {0: 'Low Risk', 1: 'Medium Risk', 2: 'High Risk'}


@app.route('/')
def home():
    return "heo"
@app.route('/add')
def add():
    ref=db.reference('students')
    new_student_ref = ref.push({
    'name': 'Kartik',
    'attendance': 75,
    'kt': 1
   })
    return "Data inserted"
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
        total_marks=0
        for mark in value['marks'].values():
            total_marks=total_marks+mark
        exam_score=total_marks/400 * 100
        attendance=value['attendance']
        family_income=value['family_income']
        fees_pending=value['fees_pending']
        kt=value['kt']
        student_data=pd.DataFrame([[attendance, exam_score , fees_pending, family_income, kt]],columns=['attendance', 'exam_score', 'fees_pending', 'family_income', 'backlogs'])
        risk=risk_labels[model.predict(student_data)[0]]
        ref = db.reference(f'students/{key}')  # replace with actual student key
        ref.update({
        "risk_status":risk,
        "risk":None
       })




    return jsonify(data)
if __name__=='__main__':
    app.run(debug=True)