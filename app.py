from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'


# Database connection function (adjust as per your configuration)
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="newDB",
        user="postgres",
        password="123456"  # Main database password
    )


# Root route
@app.route('/')
def home():
    # Redirect to login if not authenticated
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    else:
        return redirect(url_for('dashboard'))


# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db_password = request.form['db_password']

        # Compare with the actual database password
        if db_password == '123456':  # Replace with the actual DB password
            session['authenticated'] = True
            return redirect(url_for('dashboard'))
        else:
            flash("Incorrect database password", "danger")

    return render_template('login.html')


# Logout route
@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))


# Dashboard route to view tables
@app.route('/dashboard')
def dashboard():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    # Query to get data from both tables
    cur.execute('SELECT * FROM userdata2')
    userdata2 = cur.fetchall()

    cur.execute('SELECT * FROM stockhistory')
    stockhistory = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('dashboard.html', userdata2=userdata2, stockhistory=stockhistory)


# Route to edit a user in userdata2
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur.execute('UPDATE userdata2 SET email = %s, password = %s WHERE id = %s', (email, password, user_id))
        conn.commit()
        cur.close()
        conn.close()

        flash('User updated successfully', 'success')
        return redirect(url_for('dashboard'))

    cur.execute('SELECT * FROM userdata2 WHERE id = %s', (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user is None:
        flash('User not found', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('edit_user.html', user=user)


# Route to delete a user from userdata2
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('DELETE FROM userdata2 WHERE id = %s', (user_id,))
    conn.commit()
    cur.close()
    conn.close()

    flash('User deleted successfully', 'success')
    return redirect(url_for('dashboard'))


# Route to edit a stock entry in stockhistory
@app.route('/edit_stock/<int:stock_id>', methods=['GET', 'POST'])
def edit_stock(stock_id):
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
        ''', (email, stock_symbol, prediction_date, predicted_value, stock_id))
        conn.commit()
        cur.close()
        conn.close()

        flash('Stock entry updated successfully', 'success')
        return redirect(url_for('dashboard'))

    cur.execute('SELECT * FROM stockhistory WHERE id = %s', (stock_id,))
    stock_entry = cur.fetchone()
    cur.close()
    conn.close()

    if stock_entry is None:
        flash('Stock entry not found', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('edit_stock.html', stock_entry=stock_entry)


# Route to delete a stock entry from stockhistory
@app.route('/delete_stock/<int:stock_id>')
def delete_stock(stock_id):
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('DELETE FROM stockhistory WHERE id = %s', (stock_id,))
    conn.commit()
    cur.close()
    conn.close()

    flash('Stock entry deleted successfully', 'success')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
