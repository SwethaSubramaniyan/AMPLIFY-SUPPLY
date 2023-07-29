from flask import Flask, render_template, request, session, redirect,url_for, flash
import ibm_db

app=Flask(__name__)
app.secret_key='PBL-NT-GP--4957-1680773817'

conn = ibm_db.connect("database = bludb; hostname = 815fa4db-dc03-4c70-869a-a9cc13f33084.bs2io90l08kqb1od8lcg.databases.appdomain.cloud; port = 30367; uid = hnr97738; password = AfH60dDFHxPvjkV2; security = SSL; sslcertificate = DigiCertGlobalRootCA.crt", " "," ")

@app.route('/')
@app.route('/home')
def home():
    return render_template('login.html', background_image=url_for('static', filename='images/backImg.jpg'))

@app.route('/login',methods=['POST','GET'])
def login():
    global user_email
    if request.method=='POST':
        u_email=request.form['uemail']
        u_pass=request.form['upass']
        sql = 'select * from login where email = ? and password = ?'
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, u_email)
        ibm_db.bind_param(stmt, 2, u_pass)
        ibm_db.execute(stmt)
        ac = ibm_db.fetch_assoc(stmt)
        if ac:
            session['Loggedin']=True
            print(ac)
            session['email']=ac['EMAIL']
            user_email=ac['EMAIL']
            return render_template('home.html')
        else:
            msg='Email and Password are incorrect'
            return render_template('login.html', msg=msg, background_image=url_for('static', filename='images/backImg.jpg'))
    return render_template('login.html', background_image=url_for('static', filename='images/backImg.jpg'))

@app.route('/registration',methods=['POST','GET'])
def register():
    if request.method=='POST':
        u_name=request.form['uname']
        u_email=request.form['uemail']
        u_pass=request.form['upass']
        u_cpass=request.form['ucpass']
        if u_pass!=u_cpass:
            msg = 'Password Doesn\'t Match'
            return render_template('login.html', msg=msg, background_image=url_for('static', filename='images/backImg.jpg'))
        else:
            sql = 'select * from register where email = ?'
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, u_email)
            ibm_db.execute(stmt)
            acc = ibm_db.fetch_assoc(stmt)
            if acc:
                msg='Already Resgistered with this Email'
                return render_template('login.html', msg=msg, background_image=url_for('static', filename='images/backImg.jpg'))
            else:
                sql = 'insert into register values (?,?,?)'
                stmt = ibm_db.prepare(conn,sql)
                ibm_db.bind_param(stmt,1,u_name)
                ibm_db.bind_param(stmt,2,u_email)
                ibm_db.bind_param(stmt,3,u_pass)
                ibm_db.execute(stmt)
                sql = 'insert into login values (?,?)'
                stmt = ibm_db.prepare(conn,sql)
                ibm_db.bind_param(stmt,1,u_email)
                ibm_db.bind_param(stmt,2,u_pass)
                ibm_db.execute(stmt)
                msg='Created Account, Please Login'
                return render_template('login.html', msg=msg, background_image=url_for('static', filename='images/backImg.jpg'))
    return render_template('login.html', background_image=url_for('static', filename='images/backImg.jpg'))

@app.route('/suppliers')
def suppliers():
    if 'Loggedin' in session and session['Loggedin']:
        sql = 'SELECT COUNT(*) FROM supplier'
        stmt = ibm_db.exec_immediate(conn, sql)
        count = ibm_db.fetch_assoc(stmt)
        count = count['1']

        sql = 'SELECT * FROM supplier'
        stmt = ibm_db.exec_immediate(conn, sql)
        result = []

        while ibm_db.fetch_row(stmt):
            row = {
                'supplier_id': ibm_db.result(stmt, 0),
                'supplier_name': ibm_db.result(stmt, 1),
                'contact_person': ibm_db.result(stmt, 2),
                'email': ibm_db.result(stmt, 3),
                'phone_number': ibm_db.result(stmt, 4),
                'address': ibm_db.result(stmt, 5)
            }
            result.append(row)

        return render_template('Suppliers.html', suppliers=result, count=count)
    else:
        return redirect('/index')


    
@app.route('/edit_supplier/<int:supplier_id>', methods=['GET'])
def edit_supplier(supplier_id):
    if 'Loggedin' in session and session['Loggedin']:
        sql = 'SELECT * FROM supplier WHERE supplier_id = ?'
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, supplier_id)
        ibm_db.execute(stmt)
        supplier = ibm_db.fetch_assoc(stmt)
        if supplier:
            return render_template('edit_supplier.html', supplier_id=supplier_id, supplier=supplier)
        else:
            return render_template(message='Supplier not found')
    else:
        return redirect('/index')


@app.route('/update_supplier/<int:supplier_id>', methods=['POST'])
def update_supplier(supplier_id):
    if 'Loggedin' in session and session['Loggedin']:
        supplier_name = request.form.get('supplier-name')
        contact_person = request.form.get('contact_person')
        email = request.form.get('email')
        phone_number = request.form.get('phone-number')
        address = request.form.get('address')

        sql = 'UPDATE supplier SET supplier_name = ?, contact_person = ?, email = ?, phone_number = ?, address = ? WHERE supplier_id = ?'
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, supplier_name)
        ibm_db.bind_param(stmt, 2, contact_person)
        ibm_db.bind_param(stmt, 3, email)
        ibm_db.bind_param(stmt, 4, phone_number)
        ibm_db.bind_param(stmt, 5, address)
        ibm_db.bind_param(stmt, 6, supplier_id)
        
        ibm_db.execute(stmt)

        return redirect(url_for('suppliers'))
    else:
        return redirect('/index')
    
@app.route('/add_supplier', methods=['GET', 'POST'])
def add_supplier():
    if 'Loggedin' in session and session['Loggedin']:
        if request.method == 'POST':
            supplier_id = request.form.get('supplier-id')
            supplier_name = request.form.get('supplier-name')
            contact_person = request.form.get('contact_person')
            email = request.form.get('email')
            phone_number = request.form.get('phone-number')
            address = request.form.get('address')

            sql = 'INSERT INTO supplier (supplier_id, supplier_name, contact_person, email, phone_number, address) VALUES (?, ?, ?, ?, ?, ?)'
            stmt = ibm_db.prepare(conn, sql)

            ibm_db.bind_param(stmt, 1, supplier_id)
            ibm_db.bind_param(stmt, 2, supplier_name)
            ibm_db.bind_param(stmt, 3, contact_person)
            ibm_db.bind_param(stmt, 4, email)
            ibm_db.bind_param(stmt, 5, phone_number)
            ibm_db.bind_param(stmt, 6, address)

            ibm_db.execute(stmt)

            return redirect(url_for('suppliers'))
        else:
            return render_template('add_supplier.html')
    else:
        return redirect('/index')

@app.route('/delete_supplier/<int:supplier_id>', methods=['POST'])
def delete_supplier(supplier_id):
    if 'Loggedin' in session and session['Loggedin']:
        sql = 'DELETE FROM supplier WHERE supplier_id = ?'
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, supplier_id)
        ibm_db.execute(stmt)

        return redirect(url_for('suppliers'))
    else:
        return redirect('/index')

    
@app.route('/index')
def index():
    return render_template('home.html')


@app.route('/inventory')
def inventory():
    if 'Loggedin' in session and session['Loggedin']:
        sql = 'SELECT COUNT(*) FROM product'
        stmt = ibm_db.exec_immediate(conn, sql)
        count = ibm_db.fetch_assoc(stmt)
        count = count['1']

        sql = 'SELECT * FROM product'
        stmt = ibm_db.exec_immediate(conn, sql)
        result = []

        while ibm_db.fetch_row(stmt):
            row = {
                'product_id': ibm_db.result(stmt, 0),
                'product_name': ibm_db.result(stmt, 1),
                'quantity': ibm_db.result(stmt, 2),
                'price': ibm_db.result(stmt, 3),
                'supplier': ibm_db.result(stmt, 4)
            }
            result.append(row)

        return render_template('inventory.html', products=result, count=count)
    else:
        return redirect('/index')


@app.route('/edit_product/<int:product_id>', methods=['GET'])
def edit_product(product_id):
    if 'Loggedin' in session and session['Loggedin']:
        sql = 'SELECT * FROM product WHERE product_id = ?'
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, product_id)
        ibm_db.execute(stmt)
        product = ibm_db.fetch_assoc(stmt)
        if product:
            product['PRODUCT_ID'] = product_id
            return render_template('edit_product.html', product=product)
        else:
            return render_template('message.html', message='Product not found')
    else:
        return redirect('/index')

    

@app.route('/update_product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    if 'Loggedin' in session and session['Loggedin']:
        product_name = request.form.get('product-name')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        supplier = request.form.get('supplier')

        supplier_check_sql = 'SELECT COUNT(*) FROM supplier WHERE supplier_name = ?'
        supplier_check_stmt = ibm_db.prepare(conn, supplier_check_sql)
        ibm_db.bind_param(supplier_check_stmt, 1, supplier)
        ibm_db.execute(supplier_check_stmt)
        supplier_count = ibm_db.fetch_tuple(supplier_check_stmt)[0]
        
        if supplier_count == 0:
            return render_template('message.html', message='Supplier not found')
        
        sql = 'UPDATE product SET product_name = ?, quantity = ?, price = ?, supplier = ? WHERE product_id = ?'
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, product_name)
        ibm_db.bind_param(stmt, 2, quantity)
        ibm_db.bind_param(stmt, 3, price)
        ibm_db.bind_param(stmt, 4, supplier)
        ibm_db.bind_param(stmt, 5, product_id)

        ibm_db.execute(stmt)

        return redirect(url_for('inventory'))
    else:
        return redirect('/index')


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'Loggedin' in session and session['Loggedin']:
        if request.method == 'POST':
            product_id = request.form.get('product-id')
            product_name = request.form.get('product-name')
            quantity = request.form.get('quantity')
            price = request.form.get('price')
            supplier = request.form.get('supplier')

            supplier_check_sql = 'SELECT COUNT(*) FROM supplier WHERE supplier_name = ?'
            supplier_check_stmt = ibm_db.prepare(conn, supplier_check_sql)
            ibm_db.bind_param(supplier_check_stmt, 1, supplier)
            ibm_db.execute(supplier_check_stmt)
            supplier_count = ibm_db.fetch_tuple(supplier_check_stmt)[0]
            
            if supplier_count == 0:
                return render_template('message.html', message='Supplier not found')

            sql = 'INSERT INTO product (product_id, product_name, quantity, price, supplier) VALUES (?, ?, ?, ?, ?)'
            stmt = ibm_db.prepare(conn, sql)

            ibm_db.bind_param(stmt, 1, product_id)
            ibm_db.bind_param(stmt, 2, product_name)
            ibm_db.bind_param(stmt, 3, quantity)
            ibm_db.bind_param(stmt, 4, price)
            ibm_db.bind_param(stmt, 5, supplier)

            ibm_db.execute(stmt)

            return redirect(url_for('inventory'))
        else:
            return render_template('add_product.html')
    else:
        return redirect('/index')



@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'Loggedin' in session and session['Loggedin']:
        sql = 'DELETE FROM product WHERE product_id = ?'
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, product_id)
        ibm_db.execute(stmt)

        return redirect(url_for('inventory'))
    else:
        return redirect('/index')
    
@app.route('/checkout')
def checkout():
    if 'Loggedin' in session and session['Loggedin']:
        sql = "SELECT * FROM product"
        stmt = ibm_db.exec_immediate(conn, sql)
        products = []
        while ibm_db.fetch_row(stmt):
            product = {
                'product_id': ibm_db.result(stmt, 0),
                'product_name': ibm_db.result(stmt, 1),
                'quantity': ibm_db.result(stmt, 2),
                'price': ibm_db.result(stmt, 3),
                'supplier': ibm_db.result(stmt, 4)
            }
            products.append(product)
        return render_template('checkout.html', products=products)
    else:
        return redirect('/index')

    
@app.route('/transaction')
def transaction():
    if 'Loggedin' in session and session['Loggedin']:
        sql = "SELECT * FROM checkout_table"
        stmt = ibm_db.exec_immediate(conn, sql)
        transactions = []
        while ibm_db.fetch_row(stmt):
            transaction = {
                'product_id': ibm_db.result(stmt, 0),
                'product_name': ibm_db.result(stmt, 1),
                'quantity': ibm_db.result(stmt, 2),
                'price': ibm_db.result(stmt, 3),
                'supplier': ibm_db.result(stmt, 4)
            }
            transactions.append(transaction)
        return render_template('transaction.html', transactions=transactions)
    else:
        return redirect('/index')

    
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'Loggedin' in session and session['Loggedin']:
        product_id = request.form.get('product-id')
        product_name = request.form.get('product-name')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        supplier = request.form.get('supplier')

        sql = 'INSERT INTO checkout_table (product_id, product_name, quantity, price, supplier) VALUES (?, ?, ?, ?, ?)'
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, product_id)
        ibm_db.bind_param(stmt, 2, product_name)
        ibm_db.bind_param(stmt, 3, quantity)
        ibm_db.bind_param(stmt, 4, price)
        ibm_db.bind_param(stmt, 5, supplier)

        ibm_db.execute(stmt)

        return redirect(url_for('transaction'))
    else:
        return redirect('/index')


@app.route('/profile')
def profile():
    if 'Loggedin' in session and session['Loggedin']:
        email = session['email']
        print(email)
        
        sql = 'SELECT name, email FROM REGISTER WHERE email = ?'
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        
        if ibm_db.execute(stmt):
            profile = ibm_db.fetch_assoc(stmt)
            if profile:
                print(profile)
                return render_template('profile.html', profile=profile)
            else:
                return render_template('profile.html', message='Profile not found')
        else:
            return render_template('profile.html', message='Error executing SQL statement')
    else:
        return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('LoggedIn', None)
    session.pop('email', None)
    return redirect('home')

if __name__ == '__main__':
    app.run()