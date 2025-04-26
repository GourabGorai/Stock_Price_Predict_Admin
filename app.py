from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import psycopg2
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

API_KEY = 'FVOEWU64HKN1C9U2'
STOCK_BASE_URL = 'https://www.alphavantage.co/query'
HOLIDAY_API_KEY = '49339829-1b08-49a6-b341-72f937bb885f'
HOLIDAY_API_URL = 'https://holidayapi.com/v1/holidays'


# Database connection function
def get_db_connection():
    conn = psycopg2.connect(
        "postgres://avnadmin:AVNS_HjYF1YDB0ilME5gCWBC@pg-2ff69ed5-gourabg30march-ae98.l.aivencloud.com:28031/defaultdb?sslmode=require"
    )
    return conn


# Root route with authentication
@app.route('/')
def home():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))


# Dashboard to view tables with search functionality
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    # Initialize variables
    userdata2 = []
    stockhistory = []
    search_email_user = ''
    search_email_stock = ''

    # Handle user search by email
    if request.method == 'POST' and 'search_email_user' in request.form:
        search_email_user = request.form['search_email_user'].strip()
        if search_email_user:
            cur.execute('SELECT * FROM userdata2 WHERE email ILIKE %s', (f'%{search_email_user}%',))
            userdata2 = cur.fetchall()
        else:
            cur.execute('SELECT * FROM userdata2')
            userdata2 = cur.fetchall()
    else:
        cur.execute('SELECT * FROM userdata2')
        userdata2 = cur.fetchall()

    # Handle stock history search by email
    if request.method == 'POST' and 'search_email_stock' in request.form:
        search_email_stock = request.form['search_email_stock'].strip()
        if search_email_stock:
            cur.execute(
                'SELECT id, email, stock_symbol, prediction_date, predicted_value FROM stockhistory WHERE email ILIKE %s',
                (f'%{search_email_stock}%',))
            stockhistory = cur.fetchall()
        else:
            cur.execute('SELECT id, email, stock_symbol, prediction_date, predicted_value FROM stockhistory')
            stockhistory = cur.fetchall()
    else:
        cur.execute('SELECT id, email, stock_symbol, prediction_date, predicted_value FROM stockhistory')
        stockhistory = cur.fetchall()

    # Transform stockhistory into a list of dictionaries
    stockhistory_dicts = [
        {
            'id': row[0],
            'email': row[1],
            'stock_symbol': row[2],
            'prediction_date': row[3],
            'predicted_value': row[4]
        }
        for row in stockhistory
    ]

    cur.close()
    conn.close()

    return render_template('dashboard.html',
                           userdata2=userdata2,
                           stockhistory=stockhistory_dicts,
                           search_email_user=search_email_user,
                           search_email_stock=search_email_stock)


# Route to download stock history as CSV
@app.route('/download_stock_history/<string:email>')
def download_stock_history(email):
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT email, stock_symbol, prediction_date, predicted_value FROM stockhistory WHERE email = %s',
                (email,))
    stockhistory = cur.fetchall()

    cur.close()
    conn.close()

    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)

    # Write headers
    writer.writerow(['Email', 'Stock Symbol', 'Prediction Date', 'Predicted Value'])

    # Write data
    for row in stockhistory:
        writer.writerow(row)

    # Create response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment;filename={email}_stock_history.csv'}
    )


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == 'POST':
        entered_password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()

        if 'AVNS_HjYF1YDB0ilME5gCWBC' in entered_password:
            user = True
        else:
            user = False

        if user:
            session['authenticated'] = True
            return redirect(url_for('dashboard'))
        else:
            flash("Incorrect password", "danger")

        cur.close()
        conn.close()

    return render_template('login.html')


# Logout route
@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))


# Route to edit user in userdata2
@app.route('/edit_user/<string:email>', methods=['GET', 'POST'])
def edit_user(email):
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        password = request.form['password']
        cur.execute('UPDATE userdata2 SET password = %s WHERE email = %s', (password, email))
        conn.commit()
        cur.close()
        conn.close()

        flash('User updated successfully', 'success')
        return redirect(url_for('dashboard'))

    cur.execute('SELECT * FROM userdata2 WHERE email = %s', (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user is None:
        flash('User not found', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('edit_user.html', user=user)


# Route to delete user from userdata2
@app.route('/delete_user/<string:email>')
def delete_user(email):
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('DELETE FROM userdata2 WHERE email = %s', (email,))
    conn.commit()
    cur.close()
    conn.close()

    flash('User deleted successfully', 'success')
    return redirect(url_for('dashboard'))


# Route to edit stock entry in stockhistory
@app.route('/edit_stock/<int:id>', methods=['GET', 'POST'])
def edit_stock(id):
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        email = request.form['email']
        stock_symbol = request.form['stock_symbol']
        prediction_date = request.form['prediction_date']
        predicted_value = request.form['predicted_value']

        cur.execute('''
            UPDATE stockhistory
            SET email = %s, stock_symbol = %s, prediction_date = %s, predicted_value = %s
            WHERE id = %s
        ''', (email, stock_symbol, prediction_date, predicted_value, id))
        conn.commit()
        cur.close()
        conn.close()

        flash('Stock entry updated successfully', 'success')
        return redirect(url_for('dashboard'))

    cur.execute('SELECT * FROM stockhistory WHERE id = %s', (id,))
    stock_entry = cur.fetchone()
    cur.close()
    conn.close()

    if stock_entry is None:
        flash('Stock entry not found', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('edit_stock.html', stock_entry=stock_entry)


# Route to delete stock entry from stockhistory
@app.route('/delete_stock/<int:id>', methods=['POST'])
def delete_stock(id):
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('DELETE FROM stockhistory WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()

    flash('Stock entry deleted successfully', 'success')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
