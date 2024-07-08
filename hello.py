from flask import Flask, render_template, jsonify

app = Flask(__name__)

# INDEX
@app.route('/')
def index():
    return render_template('index.html')

# INSERT
@app.route('/insert')
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


# DB SAP EXAMPLE
@app.route("/db-sap")
def db_sap():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DB SAP</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            h1 {
                color: #333;
            }
            .button {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                font-size: 16px;
                cursor: pointer;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: background-color 0.3s, box-shadow 0.3s;
                margin: 5px;
            }
            .button:hover {
                background-color: #45a049;
                box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
            }
            .button:active {
                background-color: #3e8e41;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                transform: translateY(2px);
            }
        </style>
    </head>

    <body>
        <h1>Hello from Database SAP!</h1>
        <h2>View data</h2>
        <button id="runPythonButton1" class="button">Run Python Code 1</button>
        <h2>Insert data</h2>
        <button id="runPythonButton2" class="button">Run Python Code 2</button>

        <script>
        document.getElementById("runPythonButton1").addEventListener("click", function() {
            fetch('/run-python-code-1', {
                method: 'POST',
            })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                alert(data.message);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        });

        document.getElementById("runPythonButton2").addEventListener("click", function() {
            fetch('/run-python-code-2', {
                method: 'POST',
            })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                alert(data.message);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        });
        </script>

    </body>

    </html>
    """
    return html_content

@app.route('/run-python-code-1', methods=['POST'])
def run_python_code_1():
    message = "Python code 1 executed successfully!"
    return jsonify({'message': message})

@app.route('/run-python-code-2', methods=['POST'])
def run_python_code_2():
    message = "Python code 2 executed successfully!"
    return jsonify({'message': message})



if __name__ == "__main__":
    app.run(debug=True)