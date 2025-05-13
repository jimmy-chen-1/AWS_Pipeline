#!/bin/bash

# === ✅ Step 0: ===
exec > /home/ec2-user/user_data.log 2>&1
set -e


yum update -y
yum groupinstall "Development Tools" -y
yum install gcc zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel xz xz-devel libffi-devel wget -y

# === ✅ Step 1: Python 3.10 ===
cd /usr/src
wget https://www.python.org/ftp/python/3.10.14/Python-3.10.14.tgz
tar xvf Python-3.10.14.tgz
cd Python-3.10.14
./configure --enable-optimizations
make altinstall

# === ✅ Step 2: Python  ===
cd /home/ec2-user
/usr/local/bin/python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install numpy==1.23.5
pip install flask boto3 joblib pandas scikit-learn==1.2.1

# === ✅ Step 3 ===
mkdir -p /home/ec2-user/ml_webapp/templates
cd /home/ec2-user/ml_webapp

cat <<EOF > download_model.py
import boto3
s3 = boto3.client("s3")
s3.download_file("ml-model-sc171", "ml_model.pkl", "ml_model.pkl")
print("✅ Model downloaded from S3")
EOF

source /home/ec2-user/venv/bin/activate
python download_model.py

# === ✅ Step 4:app.py ===
cat <<EOF > app.py
from flask import Flask, request, render_template
import joblib
import pandas as pd

app = Flask(__name__)
model = joblib.load("ml_model.pkl")

feature_names = [
    'city', 'accommodates', 'room_type', 'bathrooms', 'bedrooms',
    'is_superhost', 'has_wifi', 'has_ac', 'has_kitchen', 'has_heating',
    'has_washer', 'has_dryer', 'has_tv', 'has_shampoo', 'has_essentials',
    'has_hair_dryer', 'has_elevator', 'has_gym'
]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            form_data = {feature: request.form[feature] for feature in feature_names}
            for k in form_data:
                if form_data[k] in ['True', 'False']:
                    form_data[k] = form_data[k] == 'True'
                elif k not in ['city', 'room_type']:
                    form_data[k] = float(form_data[k])
            df = pd.DataFrame([form_data])
            prediction = model.predict(df)[0]
            return render_template('index.html', result=prediction)
        except Exception as e:
            return render_template('index.html', result=f"Error: {e}")
    return render_template('index.html', result=None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
EOF

# === ✅ Step 5 ===
cat <<'EOF' > templates/index.html
<!DOCTYPE html>
<html>
<head>
    <title>ML Prediction App</title>
</head>
<body>
    <h2>Enter Prediction Parameters:</h2>
    <form method="post">
        City: <input type="text" name="city"><br><br>
        Accommodates: <input type="number" name="accommodates" step="1"><br><br>
        Room Type: <input type="text" name="room_type"><br><br>
        Bathrooms: <input type="number" name="bathrooms" step="0.5"><br><br>
        Bedrooms: <input type="number" name="bedrooms" step="1"><br><br>

        Is Superhost: <select name="is_superhost">
            <option value="True">Yes</option><option value="False">No</option></select><br><br>

        Has Wifi: <select name="has_wifi">
            <option value="True">Yes</option><option value="False">No</option></select><br><br>

        Has AC: <select name="has_ac">
            <option value="True">Yes</option><option value="False">No</option></select><br><br>

        Has Kitchen: <select name="has_kitchen">
            <option value="True">Yes</option><option value="False">No</option></select><br><br>

        Has Heating: <select name="has_heating">
            <option value="True">Yes</option><option value="False">No</option></select><br><br>

        Has Washer: <select name="has_washer">
            <option value="True">Yes</option><option value="False">No</option></select><br><br>

        Has Dryer: <select name="has_dryer">
            <option value="True">Yes</option><option value="False">No</option></select><br><br>

        Has TV: <select name="has_tv">
            <option value="True">Yes</option><option value="False">No</option></select><br><br>

        Has Shampoo: <select name="has_shampoo">
            <option value="True">Yes</option><option value="False">No</option></select><br><br>

        Has Essentials: <select name="has_essentials">
            <option value="True">Yes</option><option value="False">No</option></select><br><br>

        Has Hair Dryer: <select name="has_hair_dryer">
            <option value="True">Yes</option><option value="False">No</option></select><br><br>

        Has Elevator: <select name="has_elevator">
            <option value="True">Yes</option><option value="False">No</option></select><br><br>

        Has Gym: <select name="has_gym">
            <option value="True">Yes</option><option value="False">No</option></select><br><br>

        <input type="submit" value="Predict">
    </form>

    {% if result is not none %}
        <h3>Prediction Result: {{ result }}</h3>
    {% endif %}
</body>
</html>
EOF

# === ✅ Step 6:Flask ===
cd /home/ec2-user/ml_webapp
nohup /home/ec2-user/venv/bin/python app.py > flask.log 2>&1 &
