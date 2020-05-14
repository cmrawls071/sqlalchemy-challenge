from flask import Flask, jsonify
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


# Set up database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create app
app = Flask(__name__)

@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Welcome to the Hawaii Weather API!<br><br>"
        f"Available Routes:<br>"
        f"<blockquote>/api/v1.0/precipitation<br><br>"
        f"/api/v1.0/stations<br><br>"
        f"/api/v1.0/tobs<br><br>"
        f"/api/v1.0/**start_date**"
        f"<blockquote>Enter start date as: yyyy-m-d</blockquote>"
        f"/api/v1.0/*start_date**/*end_date**"
        f"<blockquote>Enter start and end dates as: yyyy-m-d</blockquote></blockquote>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Query all precipitation data
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    prcp_data = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        prcp_data.append(precipitation_dict)
    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.name).all()

    session.close()

    stations = list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == "USC00519523").filter(func.strftime(Measurement.date)>=year_ago)

    session.close()

    temp_data = []
    for date, tobs in results:
        temp_dict = {}
        temp_dict[date] = tobs
        temp_data.append(temp_dict)
    return jsonify(temp_data)


@app.route("/api/v1.0/<start_date>")
def start(start_date):
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs).all()

    all_temps = []
    for date, tobs in results:
        all_temps_dict = {}
        all_temps_dict['date'] = date
        all_temps_dict['temp'] = tobs
        all_temps.append(all_temps_dict)

    stringed = str(start_date)
    for value in all_temps:
        search_term = str(value['date'])

        if search_term == stringed:
            data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()
            info = []
            for tmin, tmax, tavg in data:
                info_dict = {}
                info_dict['min'] = tmin
                info_dict['max'] = tmax
                info_dict['avg'] = tavg
                info.append(info_dict) 
            return jsonify(info)           


    session.close()

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs).all()

    all_temps = []
    for date, tobs in results:
        all_temps_dict = {}
        all_temps_dict['date'] = date
        all_temps_dict['temp'] = tobs
        all_temps.append(all_temps_dict)

    stringed_start = str(start)
    for s in all_temps:
        start_term = str(s['date'])
        for e in all_temps:
            end_term = str(e['date'])

            if start_term == stringed_start:
                data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
                info = []
                for tmin, tmax, tavg in data:
                    info_dict = {}
                    info_dict['min'] = tmin
                    info_dict['max'] = tmax
                    info_dict['avg'] = tavg
                    info.append(info_dict) 
                return jsonify(info)           

    session.close()

if __name__ == "__main__":
    app.run(debug=True)