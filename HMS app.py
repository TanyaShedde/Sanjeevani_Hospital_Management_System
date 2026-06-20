from flask import Flask, render_template, request, redirect
import mysql.connector
from datetime import date

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    host=" ",
    user=" ",
    password=" ",
    database="project_hms"
)
cursor = db.cursor()

def generate_id(prefix, table_name, id_column):
    cursor.execute(f"SELECT {id_column} FROM {table_name}")
    all_ids = cursor.fetchall()
    if not all_ids:
        return f"{prefix}001"
    
    max_num = 0
    for record in all_ids:
        if record[0] and record[0].startswith(prefix):
            try:
                num = int(record[0][len(prefix):])
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
                
    return f"{prefix}{(max_num + 1):03d}"

# ---------------- Patients ----------------
@app.route('/patients')
def patients():
    return redirect('/patients/search')

@app.route('/patients/add')
def add_patient_form():
    next_id = generate_id('P', 'patients', 'patient_id')
    reg_date = date.today().strftime('%Y-%m-%d')
    return render_template('patients.html', mode='add', next_id=next_id, reg_date=reg_date)

@app.route('/patients/search', methods=['GET', 'POST'])
def search_patients():
    if request.method == 'POST':
        search_term = request.form.get('search_query', '')
        query = "SELECT * FROM patients WHERE patient_id LIKE %s OR first_name LIKE %s OR last_name LIKE %s OR contact_number LIKE %s"
        cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        data = cursor.fetchall()
        return render_template('patients.html', patients=data, mode='search', search_term=search_term)
    return render_template('patients.html', patients=[], mode='search')

@app.route('/add_patient', methods=['POST'])
def add_patient():
    new_id = generate_id('P', 'patients', 'patient_id')
    reg_date = date.today().strftime('%Y-%m-%d')
    values = (
        new_id, request.form['first_name'], request.form['last_name'], request.form['gender'],
        request.form['date_of_birth'], request.form['contact_number'], request.form['address'],
        reg_date, request.form['insurance_provider'],
        request.form['insurance_number'], request.form['email']
    )
    cursor.execute("""INSERT INTO patients 
        (patient_id,first_name,last_name,gender,date_of_birth,contact_number,address,registration_date,
         insurance_provider,insurance_number,email) 
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", values)
    db.commit()
    return redirect('/patients')

@app.route('/delete_patient/<pid>', methods=['POST'])
def delete_patient(pid):
    cursor.execute("DELETE FROM patients WHERE patient_id=%s", (pid,))
    db.commit()
    return redirect('/patients/search')

@app.route('/edit_patient/<pid>', methods=['GET'])
def edit_patient(pid):
    cursor.execute("SELECT * FROM patients WHERE patient_id=%s", (pid,))
    data = cursor.fetchone()
    return render_template('patients.html', patient=data, mode='edit')

@app.route('/update_patient', methods=['POST'])
def update_patient():
    pid = request.form['patient_id']
    values = (
        request.form['first_name'], request.form['last_name'], request.form['gender'],
        request.form['date_of_birth'], request.form['contact_number'], request.form['address'],
        request.form['insurance_provider'], request.form['insurance_number'], 
        request.form['email'], pid
    )
    cursor.execute("""UPDATE patients SET 
        first_name=%s, last_name=%s, gender=%s, date_of_birth=%s, contact_number=%s, 
        address=%s, insurance_provider=%s, insurance_number=%s, email=%s 
        WHERE patient_id=%s""", values)
    db.commit()
    # Fetch the updated record to show it immediately
    cursor.execute("SELECT * FROM patients WHERE patient_id=%s", (pid,))
    updated_data = cursor.fetchall()
    return render_template('patients.html', patients=updated_data, mode='search', search_term=pid)

# ---------------- Doctors ----------------
@app.route('/doctors')
def doctors():
    return redirect('/doctors/search')

@app.route('/doctors/add')
def add_doctor_form():
    next_id = generate_id('D', 'doctors', 'doctor_id')
    return render_template('doctors.html', mode='add', next_id=next_id)

@app.route('/doctors/search', methods=['GET', 'POST'])
def search_doctors():
    if request.method == 'POST':
        search_term = request.form.get('search_query', '')
        query = "SELECT * FROM doctors WHERE doctor_id LIKE %s OR first_name LIKE %s OR last_name LIKE %s OR specialization LIKE %s"
        cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        data = cursor.fetchall()
        return render_template('doctors.html', doctors=data, mode='search', search_term=search_term)
    return render_template('doctors.html', doctors=[], mode='search')

@app.route('/add_doctor', methods=['POST'])
def add_doctor():
    new_id = generate_id('D', 'doctors', 'doctor_id')
    values = (
        new_id, request.form['first_name'], request.form['last_name'], request.form['specialization'],
        request.form['phone_number'], request.form['years_experience'],
        request.form['hospital_branch'], request.form['email']
    )
    cursor.execute("""INSERT INTO doctors 
        (doctor_id,first_name,last_name,specialization,phone_number,years_experience,hospital_branch,email) 
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", values)
    db.commit()
    return redirect('/doctors')

@app.route('/delete_doctor/<did>', methods=['POST'])
def delete_doctor(did):
    cursor.execute("DELETE FROM doctors WHERE doctor_id=%s", (did,))
    db.commit()
    return redirect('/doctors/search')

@app.route('/edit_doctor/<did>', methods=['GET'])
def edit_doctor(did):
    cursor.execute("SELECT * FROM doctors WHERE doctor_id=%s", (did,))
    data = cursor.fetchone()
    return render_template('doctors.html', doctor=data, mode='edit')

@app.route('/update_doctor', methods=['POST'])
def update_doctor():
    did = request.form['doctor_id']
    values = (
        request.form['first_name'], request.form['last_name'], request.form['specialization'],
        request.form['phone_number'], request.form['years_experience'],
        request.form['hospital_branch'], request.form['email'], did
    )
    cursor.execute("""UPDATE doctors SET 
        first_name=%s, last_name=%s, specialization=%s, phone_number=%s, 
        years_experience=%s, hospital_branch=%s, email=%s 
        WHERE doctor_id=%s""", values)
    db.commit()
    # Fetch the updated record to show it immediately
    cursor.execute("SELECT * FROM doctors WHERE doctor_id=%s", (did,))
    updated_data = cursor.fetchall()
    return render_template('doctors.html', doctors=updated_data, mode='search', search_term=did)

# ---------------- Appointments ----------------
@app.route('/appointments')
def appointments():
    return redirect('/appointments/search')

@app.route('/appointments/add')
def add_appointment_form():
    next_id = generate_id('A', 'appointments', 'appointment_id')
    return render_template('appointments.html', mode='add', next_id=next_id)

@app.route('/appointments/search', methods=['GET', 'POST'])
def search_appointments():
    if request.method == 'POST':
        search_term = request.form.get('search_query', '')
        query = "SELECT * FROM appointments WHERE appointment_id LIKE %s OR patient_id LIKE %s OR doctor_id LIKE %s"
        cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        data = cursor.fetchall()
        return render_template('appointments.html', appointments=data, mode='search', search_term=search_term)
    return render_template('appointments.html', appointments=[], mode='search')

@app.route('/add_appointment', methods=['POST'])
def add_appointment():
    new_id = generate_id('A', 'appointments', 'appointment_id')
    values = (
        new_id, request.form['patient_id'], request.form['doctor_id'],
        request.form['appointment_date'], request.form['appointment_time'],
        request.form['reason_for_visit'], request.form.get('status')
    )
    cursor.execute("""INSERT INTO appointments 
        (appointment_id,patient_id,doctor_id,appointment_date,appointment_time,reason_for_visit,status) 
        VALUES (%s,%s,%s,%s,%s,%s,%s)""", values)
    db.commit()
    return redirect('/appointments')

@app.route('/delete_appointment/<aid>', methods=['POST'])
def delete_appointment(aid):
    cursor.execute("DELETE FROM appointments WHERE appointment_id=%s", (aid,))
    db.commit()
    return redirect('/appointments/search')

@app.route('/edit_appointment/<aid>', methods=['GET'])
def edit_appointment(aid):
    cursor.execute("SELECT * FROM appointments WHERE appointment_id=%s", (aid,))
    data = cursor.fetchone()
    return render_template('appointments.html', appointment=data, mode='edit')

@app.route('/update_appointment', methods=['POST'])
def update_appointment():
    aid = request.form['appointment_id']
    values = (
        request.form['patient_id'], request.form['doctor_id'],
        request.form['appointment_date'], request.form['appointment_time'],
        request.form['reason_for_visit'], request.form.get('status'), aid
    )
    cursor.execute("""UPDATE appointments SET 
        patient_id=%s, doctor_id=%s, appointment_date=%s, appointment_time=%s, 
        reason_for_visit=%s, status=%s WHERE appointment_id=%s""", values)
    db.commit()
    # Fetch the updated record to show it immediately
    cursor.execute("SELECT * FROM appointments WHERE appointment_id=%s", (aid,))
    updated_data = cursor.fetchall()
    return render_template('appointments.html', appointments=updated_data, mode='search', search_term=aid)

# ---------------- Treatments ----------------
@app.route('/treatments')
def treatments():
    return redirect('/treatments/search')

@app.route('/treatments/add')
def add_treatment_form():
    next_id = generate_id('T', 'treatments', 'treatment_id')
    return render_template('treatments.html', mode='add', next_id=next_id)

@app.route('/treatments/search', methods=['GET', 'POST'])
def search_treatments():
    if request.method == 'POST':
        search_term = request.form.get('search_query', '')
        query = "SELECT * FROM treatments WHERE treatment_id LIKE %s OR appointment_id LIKE %s OR treatment_type LIKE %s"
        cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        data = cursor.fetchall()
        return render_template('treatments.html', treatments=data, mode='search', search_term=search_term)
    return render_template('treatments.html', treatments=[], mode='search')

@app.route('/add_treatment', methods=['POST'])
def add_treatment():
    new_id = generate_id('T', 'treatments', 'treatment_id')
    values = (
        new_id, request.form['appointment_id'], request.form['treatment_type'],
        request.form['description'], request.form['cost'], request.form['treatment_date']
    )
    cursor.execute("""INSERT INTO treatments 
        (treatment_id,appointment_id,treatment_type,description,cost,treatment_date) 
        VALUES (%s,%s,%s,%s,%s,%s)""", values)
    db.commit()
    return redirect('/treatments')

@app.route('/delete_treatment/<tid>', methods=['POST'])
def delete_treatment(tid):
    cursor.execute("DELETE FROM treatments WHERE treatment_id=%s", (tid,))
    db.commit()
    return redirect('/treatments/search')

@app.route('/edit_treatment/<tid>', methods=['GET'])
def edit_treatment(tid):
    cursor.execute("SELECT * FROM treatments WHERE treatment_id=%s", (tid,))
    data = cursor.fetchone()
    return render_template('treatments.html', treatment=data, mode='edit')

@app.route('/update_treatment', methods=['POST'])
def update_treatment():
    tid = request.form['treatment_id']
    values = (
        request.form['appointment_id'], request.form['treatment_type'],
        request.form['description'], request.form['cost'], request.form['treatment_date'], tid
    )
    cursor.execute("""UPDATE treatments SET 
        appointment_id=%s, treatment_type=%s, description=%s, cost=%s, 
        treatment_date=%s WHERE treatment_id=%s""", values)
    db.commit()
    # Fetch the updated record to show it immediately
    cursor.execute("SELECT * FROM treatments WHERE treatment_id=%s", (tid,))
    updated_data = cursor.fetchall()
    return render_template('treatments.html', treatments=updated_data, mode='search', search_term=tid)

# ---------------- Billing ----------------
@app.route('/billing')
def billing():
    return redirect('/billing/search')

@app.route('/billing/add')
def add_bill_form():
    next_id = generate_id('B', 'billing', 'bill_id')
    return render_template('billing.html', mode='add', next_id=next_id)

@app.route('/billing/search', methods=['GET', 'POST'])
def search_billing():
    if request.method == 'POST':
        search_term = request.form.get('search_query', '')
        query = "SELECT * FROM billing WHERE bill_id LIKE %s OR patient_id LIKE %s OR payment_status LIKE %s"
        cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        data = cursor.fetchall()
        return render_template('billing.html', billing=data, mode='search', search_term=search_term)
    return render_template('billing.html', billing=[], mode='search')

@app.route('/add_bill', methods=['POST'])
def add_bill():
    new_id = generate_id('B', 'billing', 'bill_id')
    values = (
        new_id, request.form['patient_id'], request.form['treatment_id'],
        request.form['bill_date'], request.form['amount'],
        request.form['payment_method'], request.form['payment_status']
    )
    cursor.execute("""INSERT INTO billing 
        (bill_id,patient_id,treatment_id,bill_date,amount,payment_method,payment_status) 
        VALUES (%s,%s,%s,%s,%s,%s,%s)""", values)
    db.commit()
    return redirect('/billing')

@app.route('/delete_bill/<bid>', methods=['POST'])
def delete_bill(bid):
    cursor.execute("DELETE FROM billing WHERE bill_id=%s", (bid,))
    db.commit()
    return redirect('/billing/search')

@app.route('/edit_bill/<bid>', methods=['GET'])
def edit_bill(bid):
    cursor.execute("SELECT * FROM billing WHERE bill_id=%s", (bid,))
    data = cursor.fetchone()
    return render_template('billing.html', bill=data, mode='edit')

@app.route('/update_bill', methods=['POST'])
def update_bill():
    bid = request.form['bill_id']
    values = (
        request.form['patient_id'], request.form['treatment_id'],
        request.form['bill_date'], request.form['amount'],
        request.form['payment_method'], request.form['payment_status'], bid
    )
    cursor.execute("""UPDATE billing SET 
        patient_id=%s, treatment_id=%s, bill_date=%s, amount=%s, 
        payment_method=%s, payment_status=%s WHERE bill_id=%s""", values)
    db.commit()
    # Fetch the updated record to show it immediately
    cursor.execute("SELECT * FROM billing WHERE bill_id=%s", (bid,))
    updated_data = cursor.fetchall()
    return render_template('billing.html', billing=updated_data, mode='search', search_term=bid)

# ---------------- Home ----------------
@app.route('/')
def home():
    return render_template('Base.html')

import webbrowser
import os

if __name__ == '__main__':
    # This prevents Chrome from opening a new tab every single time you save a file
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        webbrowser.open('http://127.0.0.1:5000')
        
    app.run(debug=True)
