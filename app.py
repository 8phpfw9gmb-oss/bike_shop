from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

def get_db():
    conn = psycopg2.connect(
        host="localhost",
        database="bike_shop",
        user="macbook",
        password=""
    )
    return conn

@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bikes")
    bikes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', bikes=bikes)

@app.route('/order/<int:bike_id>', methods=['GET', 'POST'])
def order(bike_id):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM bikes WHERE id = %s", (bike_id,))
    bike = cur.fetchone()
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        
        cur.execute("""
            INSERT INTO customers (first_name, last_name, email, phone, address)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email) DO UPDATE SET phone = %s
            RETURNING id
        """, (first_name, last_name, email, phone, address, phone))
        
        customer_id = cur.fetchone()[0]
        
        cur.execute("""
            INSERT INTO orders (customer_id, bike_id, total_price, status)
            VALUES (%s, %s, %s, 'новый')
        """, (customer_id, bike_id, bike[14]))
        
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('success'))
    
    cur.close()
    conn.close()
    return render_template('order.html', bike=bike)

@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True)
    