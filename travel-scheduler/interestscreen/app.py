from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

selected={}

@app.route('/')
def index():
    return render_template('template.html')

@app.route('/change', methods=['POST'])
def change():
    current = request.form.lists()[0][1][0]
    if not current in selected:
        selected[current] = True
    else:
        selected[current] = not selected[current]

    if selected[current]:
        return jsonify(result='t'+current)
    else:
        return jsonify(result='f'+current)
