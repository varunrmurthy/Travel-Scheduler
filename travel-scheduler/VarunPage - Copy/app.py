from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template('plain.html')

@app.route('/data', methods=['POST'])
def my_form_post():
    text = request.form['address']
    processed_text = text.upper()
    return processed_text
