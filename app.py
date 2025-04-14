from flask import Flask, render_template_string, url_for
import mysql.connector

app = Flask(__name__)

# mysql connection info/credentials 
db_config = {
    'host': 'sql.freedb.tech',
    'user': 'freedb_group3',
    'password': 'nXz9Kv6bcmbVQs%',
    'database': 'freedb_airbnb_clone'
}

# home page
@app.route('/')
def home():
    home_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AirBnB Clone</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            .btn {
                display: inline-block;
                padding: 10px 20px;
                font-size: 16px;
                text-align: center;
                cursor: pointer;
                color: #fff;
                background-color: #007BFF;
                border: none;
                border-radius: 5px;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <h1>AirBnB Clone</h1>
        <p>Welcome to the AirBnB Clone home page!</p>
        <a href="{{ url_for('admin_panel') }}" class="btn">Go to Database Admin Panel</a>
    </body>
    </html>
    """
    return render_template_string(home_template)

# "admin" panel with db info
@app.route('/admin')
def admin_panel():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]

    cursor.close()
    connection.close()

    admin_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Database Admin Panel</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            ul { list-style-type: none; padding: 0; }
            li { background: #f4f4f4; margin: 5px 0; padding: 10px; border: 1px solid #ddd; }
            .btn {
                display: inline-block;
                padding: 10px 20px;
                font-size: 16px;
                text-align: center;
                cursor: pointer;
                color: #fff;
                background-color: #007BFF;
                border: none;
                border-radius: 5px;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <h1>Database Admin Panel</h1>
        <ul>
            {% for table in tables %}
            <li>{{ table }}</li>
            {% endfor %}
        </ul>
        <a href="{{ url_for('home') }}" class="btn">Back to Home</a>
    </body>
    </html>
    """
    return render_template_string(admin_template, tables=table_names)

if __name__ == '__main__':
    app.run(debug=True)

