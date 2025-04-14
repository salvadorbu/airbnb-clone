from flask import Flask, request, redirect, render_template_string, url_for
import mysql.connector
import random

app = Flask(__name__)

# MySQL connection info
db_config = {
    'host': 'sql.freedb.tech',
    'user': 'freedb_group3',
    'password': 'nXz9Kv6bcmbVQs%',
    'database': 'freedb_airbnb_clone'
}

STYLE = """
<style>
    body {
        font-family: 'Helvetica Neue', sans-serif;
        background-color: #f7f7f7;
        margin: 0;
        padding: 0;
    }
    header {
        background: #ff5a5f;
        padding: 20px;
        color: white;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
    }
    .container {
        padding: 30px;
        max-width: 800px;
        margin: auto;
        background: white;
        box-shadow: 0px 0px 15px rgba(0,0,0,0.1);
        border-radius: 8px;
    }
    h2 {
        color: #484848;
    }
    ul {
        list-style-type: none;
        padding: 0;
    }
    li {
        background: #fafafa;
        border: 1px solid #ddd;
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 5px;
    }
    input, textarea {
        width: 100%;
        padding: 10px;
        margin: 5px 0 15px 0;
        border: 1px solid #ccc;
        border-radius: 5px;
    }
    .btn {
        background-color: #ff5a5f;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
    }
    .btn:hover {
        background-color: #e04848;
    }
    a {
        color: #0077cc;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
</style>
"""

@app.route('/')
def home():
    return STYLE + """
    <header>Airbnb</header>
    <div class='container' style='text-align: center;'>
        <h2>Welcome to Airbnb</h2>
        <a href='/listings' class='btn' style='margin: 10px;'>Manage Listings (Host)</a>
        <a href='/browse' class='btn' style='margin: 10px;'>Browse Listings (Guest)</a>
    </div>
    """

# ------------------- Host Side -------------------
@app.route('/listings')
def listings():
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM listing")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return STYLE + render_template_string("""
    <header>Manage Listings</header>
    <div class='container'>
        <a href='/' class='btn'>Home</a> <a href='/add' class='btn'>Add Listing</a>
        <ul>
        {% for row in rows %}
            <li>
                <b>{{ row.host_username }}</b><br>
                {{ row.description }}<br>
                ${{ row.price }} per night<br>
                <a href='/edit/{{ row.listing_id }}'>Edit</a> | <a href='/delete/{{ row.listing_id }}'>Delete</a>
            </li>
        {% endfor %}
        </ul>
    </div>
    """, rows=rows)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        host_username = request.form['host_username']
        description = request.form['description']
        price = request.form['price']
        contact_info = request.form['contact_info']
        location_id = random.randint(10000, 99999) # random location ID

        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor()
        cur.execute("INSERT INTO listing (host_username, description, price, contact_info, location_id) VALUES (%s, %s, %s, %s, %s)",
                    (host_username, description, price, contact_info, location_id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('listings'))

    return STYLE + """
    <div class='container'>
    <h2>Add Listing</h2>
    <form method='post'>
        Host Username: <input name='host_username'><br>
        Description: <textarea name='description'></textarea><br>
        Price per night: <input name='price'><br>
        Contact Info: <input name='contact_info'><br>
        <input type='submit' class='btn'>
    </form>
    <a href='/'>Home</a>
    </div>
    """

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor(dictionary=True)
    if request.method == 'POST':
        username = request.form['host_username']
        description = request.form['description']
        price = request.form['price']
        contact_info = request.form['contact_info']
        cur.execute("UPDATE listing SET host_username=%s, description=%s, price=%s, contact_info=%s WHERE listing_id=%s",
                    (username, description, price, contact_info, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('listings'))

    cur.execute("SELECT * FROM listing WHERE listing_id=%s", (id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return STYLE + render_template_string("""
    <div class='container'>
    <h2>Edit Listing</h2>
    <form method='post'>
        Host Username: <input name='host_username' value='{{ row.host_username }}'><br>
        Description: <textarea name='description'>{{ row.description }}</textarea><br>
        Price per night: <input name='price' value='{{ row.price }}'><br>
        Contact Info: <input name='contact_info' value='{{ row.contact_info }}'><br>
        <input type='submit' class='btn'>
    </form>
    <a href='/'>Home</a>
    </div>
    """, row=row)

@app.route('/delete/<int:id>')
def delete(id):
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor()

    try:
       #  Get location_id for the listing
        cur.execute("SELECT location_id FROM listing WHERE listing_id = %s", (id,))
        result = cur.fetchone()
        location_id = result[0] if result else None

        # Delete related rows
        cur.execute("DELETE FROM booking WHERE f_listing_id = %s", (id,))
        cur.execute("DELETE FROM availability WHERE f_listing_id = %s", (id,))
        cur.execute("DELETE FROM review WHERE f_listing_id = %s", (id,))
        cur.execute("DELETE FROM saved_listings WHERE listings = %s", (id,))

        if location_id:
            cur.execute("DELETE FROM photos WHERE f_location_id = %s", (location_id,))

        # Delete the listing
        cur.execute("DELETE FROM listing WHERE listing_id = %s", (id,))


        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        return f"<h2>Error:</h2><pre>{err}</pre>"
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('listings'))


# ------------------- Guest Side -------------------
@app.route('/browse')
def browse():
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM listing")
    listings = cur.fetchall()
    cur.close()
    conn.close()
    return STYLE + render_template_string("""
    <h2>Browse Listings</h2>
    <a href='/'>Home</a>
    <ul>
    {% for row in listings %}
        <li>
            <b>{{ row.title }}</b><br>
            {{ row.description }}<br>
            ${{ row.price }} per night<br>
            <form method='post' action='/book'>
                <input type='hidden' name='listing_id' value='{{ row.id }}'>
                Check-in: <input type='date' name='check_in'><br>
                Check-out: <input type='date' name='check_out'><br>
                <input type='submit' value='Book'>
            </form>
        </li>
    {% endfor %}
    </ul>
    """, listings=listings)

@app.route('/book', methods=['POST'])
def book():
    listing_id = request.form['listing_id']
    check_in = request.form['check_in']
    check_out = request.form['check_out']
    guest_id = 1  # Hardcoded for demo

    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor()
    cur.execute("INSERT INTO booking (f_listing_id, check_in_date, check_out_date, f_guest_id, status) VALUES (%s, %s, %s, %s, %s)",
                (listing_id, check_in, check_out, guest_id, 'pending'))
    conn.commit()
    cur.close()
    conn.close()
    return STYLE + redirect(url_for('browse'))

@app.route('/host-bookings')
def host_bookings():
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT b.*, l.title FROM booking b
        JOIN listing l ON b.f_listing_id = l.id
        WHERE l.f_host_id = %s
    """, (1,))  # Hardcoded host ID
    bookings = cur.fetchall()
    cur.close()
    conn.close()
    return STYLE + render_template_string("""
    <h2>Host Bookings</h2>
    <a href='/'>Home</a>
    <ul>
    {% for b in bookings %}
        <li>
            Listing: {{ b.title }}<br>
            {{ b.check_in_date }} → {{ b.check_out_date }}<br>
            Status: {{ b.status }}<br>
            <a href='/approve/{{ b.f_listing_id }}/{{ b.check_in_date }}/{{ b.check_out_date }}'>Approve</a> |
            <a href='/reject/{{ b.f_listing_id }}/{{ b.check_in_date }}/{{ b.check_out_date }}'>Reject</a>
        </li>
    {% endfor %}
    </ul>
    """, bookings=bookings)

if __name__ == '__main__':
    app.run(debug=True)