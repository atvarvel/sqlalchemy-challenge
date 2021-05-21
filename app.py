import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///C://Users//atvar//OneDrive//Documents//Bootcamp//May_Homework//10-SQLAlchemy_Homework//Resources//hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Temperatures from start date (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperatures from start to end dates (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    sel = [Measurement.date, Measurement.prcp]

    results = session.query(*sel).all()

    session.close()

    precip = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict['Date'] = date
        prcp_dict['Precipitation'] = prcp
        precip.append(prcp_dict)

    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]

    results = session.query(*sel).all()

    session.close()

    stations = []
    for station, name, lat, lon, elev in results:
        station_dict = {}
        station_dict['Station'] = station
        station_dict['Name'] = name
        station_dict['Latitude'] = lat
        station_dict['Longitude'] = lon
        station_dict['Elevation'] = elev
        stations.append(station_dict)

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    most_recent_date = dt.datetime.strptime(most_recent, '%Y-%m-%d')

    query_date = dt.date(most_recent_date.year -1, most_recent_date.month, most_recent_date.day)

    sel = [Measurement.date, Measurement.tobs]

    results = session.query(*sel).filter(Measurement.date >= query_date).all()

    session.close()

    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict['Date'] = date
        tobs_dict['Tobs'] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def temp_start(start):

    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()

    session.close()

    all_tobs = []
    for min, max, avg in results:
        tobs_dict = {}
        tobs_dict['Min'] = min
        tobs_dict['Max'] = max
        tobs_dict['Average'] = avg
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end):

    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    all_tobs = []
    for min, max, avg in results:
        tobs_dict = {}
        tobs_dict['Min'] = min
        tobs_dict['Max'] = max
        tobs_dict['Average'] = avg
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


if __name__ == '__main__':
    app.run(debug=True)
