from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('app/home.html')


@app.route('/dashboard')
def dashboard():
    return render_template('app/dashboard.html')


@app.route('/import-file', methods=['POST'])
def importFile(request):
    file = request.file('file')
    
    return render_template('app/dashboard.html')


if __name__ == "__main__":
    app.run(port=5000, debug=True)