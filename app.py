
from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "blood-bank-project-key"

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="dbmsproject@2007",
        database="blood_bank"
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == "admin" and password == "blood123":
            session["logged_in"] = True
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password. Please try again.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



@app.route("/")
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    db = get_db_connection()
    cursor = db.cursor()

    tables = [
        "donor", "patient", "donation",
        "blood_stock", "blood_request", "hospital"
    ]
    counts = {}

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
        counts[table] = cursor.fetchone()[0]

    cursor.close()
    db.close()
    return render_template("index.html", counts=counts)

@app.route("/donors")
def donors():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT donor_id, name, age, gender, blood_group, phone, address
        FROM donor ORDER BY donor_id DESC
    """)
    donor_list = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("donors.html", donors=donor_list)

@app.route("/add-donor", methods=["POST"])
def add_donor():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Please enter the donor's name.")
        return redirect(url_for("donors"))

    age = request.form.get("age") or None
    gender = request.form.get("gender") or None
    blood_group = request.form.get("blood_group") or None
    phone = request.form.get("phone") or None
    address = request.form.get("address") or None

    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO donor
            (name, age, gender, blood_group, phone, address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, age, gender, blood_group, phone, address))
        db.commit()
        flash("Donor registered successfully!")
    except mysql.connector.Error as error:
        db.rollback()
        flash(f"Could not register donor: {error}")
    finally:
        cursor.close()
        db.close()

    return redirect(url_for("donors"))

@app.route("/patients")
def patients():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT patient_id, patient_name, age, gender,
               blood_group, phone, address
        FROM patient
        ORDER BY patient_id DESC
    """)
    patient_list = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("patients.html", patients=patient_list)


@app.route("/add-patient", methods=["POST"])
def add_patient():
    patient_name = request.form.get("patient_name", "").strip()

    if not patient_name:
        flash("Please enter the patient's name.")
        return redirect(url_for("patients"))

    age = request.form.get("age") or None
    gender = request.form.get("gender") or None
    blood_group = request.form.get("blood_group") or None
    phone = request.form.get("phone") or None
    address = request.form.get("address") or None

    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("""
            INSERT INTO patient
            (patient_name, age, gender, blood_group, phone, address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (patient_name, age, gender, blood_group, phone, address))

        db.commit()
        flash("Patient registered successfully!")

    except mysql.connector.Error as error:
        db.rollback()
        flash(f"Could not register patient: {error}")

    finally:
        cursor.close()
        db.close()

    return redirect(url_for("patients"))

@app.route("/requests")
def blood_requests():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT request_id, patient_name, blood_group,
               units_needed, request_date, status
        FROM blood_request
        ORDER BY request_id DESC
    """)

    request_list = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("requests.html", requests=request_list)


@app.route("/add-request", methods=["POST"])
def add_request():
    patient_name = request.form.get("patient_name", "").strip()
    blood_group = request.form.get("blood_group", "")
    units_needed = request.form.get("units_needed", "")
    request_date = request.form.get("request_date") or None

    if not patient_name or not blood_group or not units_needed:
        flash("Please fill in all required fields.")
        return redirect(url_for("blood_requests"))

    try:
        units_needed = int(units_needed)
        if units_needed < 1:
            raise ValueError
    except ValueError:
        flash("Units needed must be a positive whole number.")
        return redirect(url_for("blood_requests"))

    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("""
            INSERT INTO blood_request
            (patient_name, blood_group, units_needed, request_date)
            VALUES (%s, %s, %s, %s)
        """, (patient_name, blood_group, units_needed, request_date))

        db.commit()
        flash("Blood request submitted successfully!")

    except mysql.connector.Error as error:
        db.rollback()
        flash(f"Could not submit request: {error}")

    finally:
        cursor.close()
        db.close()

    return redirect(url_for("blood_requests"))
@app.route("/stock")
def stock():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT stock_id, blood_group, units_available
        FROM blood_stock
        ORDER BY stock_id
    """)

    stock_list = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("stock.html", stock_list=stock_list)
@app.route("/update-stock", methods=["POST"])
def update_stock():
    blood_group = request.form["blood_group"]
    units_available = int(request.form["units_available"])

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "SELECT stock_id FROM blood_stock WHERE blood_group = %s LIMIT 1",
        (blood_group,)
    )
    existing_stock = cursor.fetchone()

    if existing_stock:
        cursor.execute(
            "UPDATE blood_stock SET units_available = %s WHERE stock_id = %s",
            (units_available, existing_stock[0])
        )
        message = "Blood stock updated successfully!"
    else:
        cursor.execute(
            "INSERT INTO blood_stock (blood_group, units_available) VALUES (%s, %s)",
            (blood_group, units_available)
        )
        message = "Blood stock added successfully!"

    db.commit()
    cursor.close()
    db.close()

    flash(message)
    return redirect(url_for("stock"))


@app.route("/donations")
def donations():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT  
               ROW_NUMBER() OVER (ORDER BY donation.donation_id DESC) AS display_id,
               donation.donation_id,
               donation.donor_id,
               donor.name AS donor_name,
               donation.donation_date,
               donation.units_donated
        FROM donation
        JOIN donor ON donation.donor_id = donor.donor_id
        ORDER BY donation.donation_id DESC
    """)

    donation_list = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("donations.html", donations=donation_list)

@app.route("/hospitals")
def hospitals():
    if not session.get("logged_in"):
         return redirect(url_for("login"))
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT hospital_id, hospital_name, phone, address
        FROM hospital
        ORDER BY hospital_id DESC
    """)

    hospital_list = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("hospitals.html", hospitals=hospital_list)

@app.route("/add-hospital", methods=["POST"])
def add_hospital():
    hospital_name = request.form["hospital_name"]
    phone = request.form.get("phone", "")
    address = request.form.get("address", "")

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO hospital (hospital_name, phone, address) VALUES (%s, %s, %s)",
        (hospital_name, phone, address)
    )

    db.commit()
    cursor.close()
    db.close()

    flash("Hospital added successfully!")
    return redirect(url_for("hospitals"))

@app.route("/add-donation", methods=["POST"])
def add_donation():
    donor_id = request.form["donor_id"]
    donation_date = request.form["donation_date"]
    units_donated = request.form["units_donated"]

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO donation (donor_id, donation_date, units_donated) VALUES (%s, %s, %s)",
        (donor_id, donation_date, units_donated)
    )

    db.commit()
    cursor.close()
    db.close()

    flash("Donation recorded successfully!")
    return redirect(url_for("donations"))

if __name__ == "__main__":
     app.run(debug=True)
    

