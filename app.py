from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2

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

# Dashboard to view tables
@app.route('/dashboard')
def dashboard():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    # Get data from userdata2
    cur.execute('SELECT * FROM userdata2')
    userdata2 = cur.fetchall()

    # Get data from stockhistory
    cur.execute('SELECT id, email, stock_symbol, prediction_date, predicted_value FROM stockhistory')
    stockhistory = cur.fetchall()

    cur.close()
    conn.close()

    # Transform stockhistory into a list of dictionaries for easier access in templates
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

    return render_template('dashboard.html', userdata2=userdata2, stockhistory=stockhistory_dicts)


# Login route
# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == 'POST':
        entered_password = request.form['password']  # Get password from form

        conn = get_db_connection()
        cur = conn.cursor()

        if 'AVNS_HjYF1YDB0ilME5gCWBC' in entered_password:
            user=True
        if user:
            # If a matching user is found, authenticate
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
