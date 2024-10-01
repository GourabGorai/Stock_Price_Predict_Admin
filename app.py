from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database connection function
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="newDB",
        user="postgres",
        password="123456"
    )
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM userdata2')
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', users=users)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM userdata2 WHERE id = %s', (id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        # Add other fields as necessary

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE userdata2 SET email = %s, name = %s WHERE id = %s',
                    (email, name, id))
        conn.commit()
        cur.close()
        conn.close()
        flash('User updated successfully!')
        return redirect(url_for('index'))

    return render_template('edit.html', user=user)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM userdata2 WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('User deleted successfully!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
