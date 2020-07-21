# Import the various dependencies and SQL Alchemy, Flask & Jasonify setup
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#-------------------#

# Database set-up
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

#-------------------#

# Flask set-up
app = Flask(__name__)

#-------------------#
# Flask Routes

@app.route("/")
def home():
    return(f" <h1> Welcome to the Climate App API </h1> <br/>"
           f" <h2> Available routes: </h2> <br/>"           
           f" <h3> /api/v1.0/precipitation </h3> <br/>"           
           f" <h3> /api/v1.0/stations </h3> <br/>"           
           f" <h3> /api/v1.0/tobs </h3> <br/>"           
           f" <h3> /api/v1.0/&lt;start&gt; </h3>"
           f" <h4> In place of start, enter a date between 2010-01-01 and 2017-08-23 in YYYY-MM-DD format </h4> <br/>"           
           f" <h3> /api/v1.0/&lt;start&gt;/&lt;end&gt; </h3>"
           f" <h4> In place of start and end, enter a date between 2010-01-01 and 2017-08-23 in YYYY-MM-DD format </h4> <br/>"
          )


# Convert the query results to a dictionary using date as the key and prcp as the value.
# Reflecting the filter criteria of past 12 months from the Python assignment
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create the session, query the desired criteria and close the session
    session = Session(engine)
    results = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>='2016-08-23',\
                                                                      Measurement.date<='2017-08-23').order_by(Measurement.date).all()
    session.close()
    
    # Create empty list(s) and dictionary(s) to store results
    all_dates = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_dates.append(prcp_dict)
    return jsonify(all_dates)


# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Create the session, query the desired criteria and close the session
    session = Session(engine)
    results = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    session.close()
    
    # Create empty list(s) and dictionary(s) to store results    
    active_stations = []
    for id, name in results:
        station_dict = {}
        station_dict[id] = name
        active_stations.append(station_dict)
    return jsonify(active_stations)


# Query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create the session, query the desired criteria and close the session
    session = Session(engine)
    results = session.query(Measurement.station, Measurement.date, Measurement.prcp).filter(Measurement.station == "USC00519281").\
                filter(Measurement.date >= "2016-08-23", Measurement.date <= "2017-08-23" ).order_by(Measurement.date).all()
    session.close()
    
    # Create empty list(s) and dictionary(s) to store results
    active_station_tobs = list(np.ravel(results))
    return jsonify(active_station_tobs)


# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def start(start):
    # Declare the variables
    start_date = start

    # Create the session, query the desired criteria and close the session
    session = Session(engine)
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs),
                            func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).group_by(Measurement.date).all()

    session.close()
    
    # Create empty list(s) and dictionary(s) to store results    
    date_range_data = []
    for start_date, min, max, avg in results:
        data = {}
        data["Start Date"] = start
        data["Minimum Temperature"] = min
        data["Maximum Temperature"] = max
        data["Average Temperature"] = round(avg,2)
        date_range_data.append(data) 
    return jsonify(date_range_data)


# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def end(start, end):
    # Declare the variables
    start_date = start
    end_date = end

    # Create the session, query the desired criteria and close the session
    session = Session(engine)
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs),\
                            func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).\
                            filter(Measurement.date <= end_date).group_by(Measurement.date).all()
    session.close()
    
    # Create empty list(s) and dictionary(s) to store results    
    date_range_data = []
    for start_date,min, max, avg in results:
        data = {}
        data["Start Date"] = start
        data["Minimum Temperature"] = min
        data["Maximum Temperature"] = max
        data["Average Temperature"] = round(avg,2)
        date_range_data.append(data) 
    return jsonify(date_range_data)


if __name__ == '__main__':
    app.run(debug = False)