from flask import Flask, render_template
# from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# INDEX
@app.route('/')
def index():
    return render_template('index.html')

# INSERT
@app.route('/insert', methods=['GET', 'POST'])
def insert():
    return render_template('insert.html')

# LOGISTICS
@app.route('/logistics')
def logistics():
    return render_template('logistics.html')

# MODIFY
@app.route('/modify')
def modify():
    return render_template('modify.html')

# SEARCH
@app.route('/search')
def search():
    return render_template('search.html')


if __name__ == "__main__":
    app.run(debug=True)