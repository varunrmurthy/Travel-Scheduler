from flask import Flask, render_template, request, jsonify
app = Flask(__name__)
app.config['input'] = {}
app.config['input']['place'] = []
@app.route('/')
def places():
    return render_template('places.html', places=app.config['input']['place'])
@app.route('/places', methods=['POST'])
def show():
    addr = request.form.get('place', '', type=str)
    print(addr)
    app.config['input']['place'].append(addr);
    return jsonify(addr)
