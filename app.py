from flask import Flask, render_template, request, redirect, url_for, flash
from database import init_db, get_db, seed_demo_data
from analysis import monthly_usage, yearly_usage, high_usage, validate_readings, chart_data
from config import SECRET_KEY, DEFAULT_HIGH_USAGE_THRESHOLD

app = Flask(__name__)
app.secret_key = SECRET_KEY
with app.app_context():
    init_db()
    seed_demo_data()

@app.route("/")
def dashboard():
    db = get_db()
    return render_template("index.html",
        consumers=db.execute("SELECT COUNT(*) FROM consumers").fetchone()[0],
        meters=db.execute("SELECT COUNT(*) FROM meters").fetchone()[0],
        readings=db.execute("SELECT COUNT(*) FROM meter_readings").fetchone()[0],
        high=high_usage(float(request.args.get("threshold", DEFAULT_HIGH_USAGE_THRESHOLD))),
        threshold=request.args.get("threshold", DEFAULT_HIGH_USAGE_THRESHOLD),
        chart=chart_data())

@app.route("/consumers", methods=["GET","POST"])
def consumers_page():
    db=get_db()
    if request.method=="POST":
        name=request.form.get("name","").strip(); typ=request.form.get("consumer_type","Residential"); region=request.form.get("region","").strip()
        if not name or not region: flash("Name and region are required.","error")
        else:
            db.execute("INSERT INTO consumers(name,consumer_type,region) VALUES(?,?,?)",(name,typ,region)); db.commit()
            flash("Consumer added.","success"); return redirect(url_for("consumers_page"))
    return render_template("consumers.html", consumers=db.execute("SELECT * FROM consumers ORDER BY consumer_id DESC").fetchall())

@app.post("/consumers/delete/<int:cid>")
def delete_consumer(cid):
    db=get_db(); db.execute("DELETE FROM consumers WHERE consumer_id=?",(cid,)); db.commit()
    flash("Consumer and related records deleted.","success"); return redirect(url_for("consumers_page"))

@app.route("/meters", methods=["GET","POST"])
def meters_page():
    db=get_db()
    if request.method=="POST":
        try:
            db.execute("INSERT INTO meters(consumer_id,meter_code) VALUES(?,?)",(int(request.form["consumer_id"]),request.form["meter_code"].strip()))
            db.commit(); flash("Meter added.","success"); return redirect(url_for("meters_page"))
        except Exception: db.rollback(); flash("Could not add meter. Meter code must be unique.","error")
    consumers=db.execute("SELECT * FROM consumers ORDER BY name").fetchall()
    meters=db.execute("SELECT m.*,c.name consumer_name FROM meters m JOIN consumers c USING(consumer_id) ORDER BY meter_id DESC").fetchall()
    return render_template("meters.html",consumers=consumers,meters=meters)

@app.post("/meters/delete/<int:mid>")
def delete_meter(mid):
    db=get_db(); db.execute("DELETE FROM meters WHERE meter_id=?",(mid,)); db.commit()
    flash("Meter and readings deleted.","success"); return redirect(url_for("meters_page"))

@app.route("/readings",methods=["GET","POST"])
def readings_page():
    db=get_db()
    if request.method=="POST":
        try:
            mid=int(request.form["meter_id"]); date=request.form["reading_date"]; value=float(request.form["cumulative_kwh"])
            if value<0: raise ValueError("Reading must be zero or greater.")
            prev=db.execute("SELECT reading_date,cumulative_kwh FROM meter_readings WHERE meter_id=? ORDER BY reading_date DESC LIMIT 1",(mid,)).fetchone()
            if prev and date<=prev["reading_date"]: raise ValueError("Date must be later than the previous reading.")
            note="Possible meter reset/rollover: cumulative value decreased." if prev and value<prev["cumulative_kwh"] else ""
            db.execute("INSERT INTO meter_readings(meter_id,reading_date,cumulative_kwh,validation_note) VALUES(?,?,?,?)",(mid,date,value,note))
            db.commit(); flash("Reading saved. Check validation report if flagged.","success"); return redirect(url_for("readings_page"))
        except ValueError as e: flash(str(e) or "Enter a valid reading.","error")
        except Exception: db.rollback(); flash("Could not save reading. Check meter and date.","error")
    meters=db.execute("SELECT m.*,c.name consumer_name FROM meters m JOIN consumers c USING(consumer_id) ORDER BY c.name").fetchall()
    readings=db.execute("SELECT r.*,m.meter_code,c.name consumer_name FROM meter_readings r JOIN meters m USING(meter_id) JOIN consumers c USING(consumer_id) ORDER BY reading_date DESC LIMIT 100").fetchall()
    return render_template("readings.html",meters=meters,readings=readings)

@app.route("/reports")
def reports():
    threshold=float(request.args.get("threshold",DEFAULT_HIGH_USAGE_THRESHOLD))
    return render_template("monthly_report.html",monthly=monthly_usage(),yearly=yearly_usage(),high=high_usage(threshold),threshold=threshold)

@app.route("/validation")
def validation():
    return render_template("validation.html",rows=validate_readings())

if __name__=="__main__":
    app.run(debug=True)
