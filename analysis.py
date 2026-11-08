from database import get_db
from collections import defaultdict
from datetime import datetime

def _rows():
    return get_db().execute("""SELECT r.*,m.meter_code,c.consumer_id,c.name consumer_name
      FROM meter_readings r JOIN meters m USING(meter_id) JOIN consumers c USING(consumer_id)
      ORDER BY r.meter_id,r.reading_date""").fetchall()

def _intervals():
    prev={}; out=[]
    for r in _rows():
        mid=r["meter_id"]; current=(r["reading_date"],float(r["cumulative_kwh"]))
        if mid in prev and not r["validation_note"]:
            pd,pv=prev[mid]
            if current[1]>=pv:
                try:
                    days=(datetime.fromisoformat(current[0])-datetime.fromisoformat(pd)).days
                    if days>0: out.append({"period":current[0][:7],"year":current[0][:4],"consumer":r["consumer_name"],"kwh":current[1]-pv})
                except ValueError: pass
        prev[mid]=current
    return out

def _group(key):
    totals=defaultdict(float)
    for x in _intervals(): totals[(x[key],x["consumer"])]+=x["kwh"]
    return [{"period":p,"consumer":c,"kwh":round(v,2)} for (p,c),v in sorted(totals.items())]

def monthly_usage(): return _group("period")
def yearly_usage(): return _group("year")
def high_usage(threshold): return [x for x in monthly_usage() if x["kwh"]>threshold]
def validate_readings():
    out=[]
    for r in _rows():
        status=r["validation_note"] or "Valid"
        out.append({"date":r["reading_date"],"consumer":r["consumer_name"],"meter":r["meter_code"],"value":r["cumulative_kwh"],"status":status})
    return out
def chart_data():
    totals=defaultdict(float)
    for x in _intervals(): totals[x["period"]]+=x["kwh"]
    keys=sorted(totals); return {"labels":keys,"values":[round(totals[k],2) for k in keys]}
