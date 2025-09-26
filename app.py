from flask import Flask,jsonify
import pickle
import os
import numpy as np
import pandas as pd
import firebase_admin
from firebase_admin import credentials,db
app=Flask("__name__")

sampledata=pd.DataFrame([[30, 40 , 1000, 200000, 5]],columns=['attendance', 'exam_score', 'fees_pending', 'family_income', 'backlogs'])
model=pickle.load(open("student_dropout_model_3levels.pkl","rb"))
# data = np.array([70, 80, 1000, 200000, 2])
# data = data.reshape(1, -1)  # 1 sample, 5 features
base_dir=os.path.dirname(os.path.abspath(__file__))
cred_path=os.path.join(base_dir,"tech810servicekey.json")
cred=credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred,{
    "databaseURL":"https://sih-tech810-default-rtdb.firebaseio.com/"
})


# new_predictions=model.predict(sampledata)
risk_labels = {0: 'Low Risk', 1: 'Medium Risk', 2: 'High Risk'}
predicted_class = model.predict(sampledata)[0]
print(risk_labels[predicted_class])

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
        values = data.values()
    elif isinstance(data, list):
        values = [item for item in data if item is not None]
    else:
        values = []
    for value in values:
        total_marks=0
        for mark in value['marks'].values():
            total_marks=total_marks+mark
        print("total marks:",total_marks)


    return jsonify(data)
if __name__=='__main__':
    app.run(debug=True)