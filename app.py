from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import datetime

app = Flask(__name__)

# Create Database
def init_db():
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_no TEXT UNIQUE,
            name TEXT,
            address TEXT,
            designation TEXT,
            department TEXT,
            achievements TEXT,
            basic_salary REAL,
            deduction REAL,
            ta REAL,
            da REAL,
            hra REAL,
            other_allowance REAL,
            pf REAL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_no TEXT,
            month TEXT,
            total_days INTEGER,
            days_present INTEGER,
            leaves INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS salaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_no TEXT,
            month TEXT,
            gross_salary REAL,
            deductions REAL,
            net_salary REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        data = (
            request.form['emp_no'],
            request.form['name'],
            request.form['address'],
            request.form['designation'],
            request.form['department'],
            request.form['achievements'],
            float(request.form['basic_salary']),
            float(request.form['deduction']),
            float(request.form['ta']),
            float(request.form['da']),
            float(request.form['hra']),
            float(request.form['other_allowance']),
            float(request.form['pf'])
        )
        conn = sqlite3.connect('payroll.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO employees (emp_no, name, address, designation, department, achievements, basic_salary, deduction, ta, da, hra, other_allowance, pf)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)
        conn.commit()
        conn.close()
        return redirect(url_for('view_employees'))
    return render_template('add_employee.html')

@app.route('/employees')
def view_employees():
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()
    c.execute('SELECT * FROM employees')
    employees = c.fetchall()
    conn.close()
    return render_template('employees.html', employees=employees)

@app.route('/add_attendance', methods=['GET', 'POST'])
def add_attendance():
    if request.method == 'POST':
        data = (
            request.form['emp_no'],
            request.form['month'],
            int(request.form['total_days']),
            int(request.form['days_present']),
            int(request.form['leaves'])
        )
        conn = sqlite3.connect('payroll.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO attendance (emp_no, month, total_days, days_present, leaves)
            VALUES (?, ?, ?, ?, ?)
        ''', data)
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    return render_template('add_attendance.html')

@app.route('/generate_salary', methods=['GET', 'POST'])
def generate_salary():
    if request.method == 'POST':
        emp_no = request.form['emp_no']
        month = request.form['month']

        conn = sqlite3.connect('payroll.db')
        c = conn.cursor()
        c.execute('SELECT * FROM employees WHERE emp_no = ?', (emp_no,))
        employee = c.fetchone()

        c.execute('SELECT * FROM attendance WHERE emp_no = ? AND month = ?', (emp_no, month))
        attendance = c.fetchone()

        if employee and attendance:
            basic_salary = employee[7]
            deduction = employee[8]
            ta = employee[9]
            da = employee[10]
            hra = employee[11]
            other_allowance = employee[12]
            pf = employee[13]

            total_working_days = attendance[3]
            total_days = attendance[2]

            gross_salary = basic_salary + ta + da + hra + other_allowance
            total_deductions = deduction + pf
            daily_salary = gross_salary / float(total_days)

            net_salary = (daily_salary * total_working_days) - total_deductions

            c.execute('''
                INSERT INTO salaries (emp_no, month, gross_salary, deductions, net_salary)
                VALUES (?, ?, ?, ?, ?)
            ''', (emp_no, month, gross_salary, total_deductions, net_salary))
            conn.commit()
            conn.close()

            return render_template('salary_slip.html', employee=employee, attendance=attendance, gross_salary=gross_salary, deductions=total_deductions, net_salary=net_salary)
        else:
            return "Employee or Attendance record not found."
    return render_template('generate_salary.html')

@app.route('/salary_reports')
def view_salary_reports():
    conn = sqlite3.connect('payroll.db')
    c = conn.cursor()
    c.execute('SELECT * FROM salaries')
    salaries = c.fetchall()
    conn.close()
    return render_template('view_salary_reports.html', salaries=salaries)

if __name__ == '__main__':
    app.run(debug=True)
