import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB


# 2. Create an app
app = Flask(__name__)

@app.route("/")
def home():
    return """<xmp>
              Hello!
              The following routes are available:

              /api/v1.0/precipitation

              /api/v1.0/stations

              /api/v1.0/tobs

              /api/v1.0/start_date/<start_date>
              #Please enter start date in '%Y-%m-%d' format
              #For instance, 2016-27-2 or 2017-8-20

              /api/v1.0/<start_date>/<end_date>
              #Please enter start and end date in '%Y-%m-%d' format
              #For instance, 2016-27-2 or 2017-8-20
              </xmp>"""

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >= dt.date(2016, 8, 23)).all()

    precipitation = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precipitation"] = prcp
        precipitation.append(prcp_dict)
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""
    # Query all stations
    session = Session(engine)
    results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
    import os
    import csv
    csvpath = ('Resources\hawaii_measurements.csv')

    session = Session(engine)
    results = session.query(Station.name, Station.station).all()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    with open(csvpath, newline='') as csvfile:

        # CSV reader specifies delimiter and variable that holds contents
        csvreader = csv.reader(csvfile, delimiter=',')

        #print(csvreader)

         # Read the header row first (skip this step if there is now header)
        csv_header = next(csvreader)
        #print(f"CSV Header: {csv_header}")
    
        tobs = []
        # Read each row of data after the header
        for row in csvreader:
        #print(row)
        #print(dt.datetime.strptime(row[1], '%Y-%m-%d'))
            if (dt.datetime.strptime(row[1], '%Y-%m-%d') >= dt.datetime(2016,8,18)) and (row[0] in all_names):
                tobs_dict = {}
                station_name = session.query(Station.name).\
                    filter(row[0]==Station.station).all()
                tobs_dict["station_name"] = str(station_name).replace('[','').replace(']','')
                tobs_dict["station"] = row[0]
                tobs_dict["date"] = row[1]
                tobs_dict["tobs"] = row[3]
                tobs.append(tobs_dict)
    return jsonify(tobs)

@app.route("/api/v1.0/start_date/<start_date>")
def start (start_date):
# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
       
    import os
    import csv
    from statistics import mean, median
    import datetime as dt
    csvpath = ('Resources\hawaii_measurements.csv')

    with open(csvpath, newline='') as csvfile:

        # CSV reader specifies delimiter and variable that holds contents
        csvreader = csv.reader(csvfile, delimiter=',')

        # Read the header row first (skip this step if there is now header)
        csv_header = next(csvreader)
           
        temp_stats = {}
        temp_calc = []
    
        
        # Read each row of data after the header
        for row in csvreader:
            if (dt.datetime.strptime(row[1], '%Y-%m-%d') >= dt.datetime.strptime(start_date, '%Y-%m-%d' )):
                temp_calc.append(int(row[3]))

        #print(temp_calc)
        max_temp = max(temp_calc)
        min_temp = min(temp_calc)
        mean_temp = mean(temp_calc)
        temp_stats.update({"max_temp": max_temp, "min_temp": min_temp, "mean":mean_temp})

    return temp_stats

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end (start_date, end_date):
# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.

    import os
    import csv
    from statistics import mean, median
    import datetime as dt
    csvpath = ('Resources\hawaii_measurements.csv')
    
    with open(csvpath, newline='') as csvfile:

        # CSV reader specifies delimiter and variable that holds contents
        csvreader = csv.reader(csvfile, delimiter=',')

        # Read the header row first (skip this step if there is now header)
        csv_header = next(csvreader)
           
        temp_stats = {}
        temp_calc = []
        sd = dt.datetime.strptime(start_date, '%Y-%m-%d')
        ed = dt.datetime.strptime(end_date, '%Y-%m-%d')
    
        
        # Read each row of data after the header
        for row in csvreader:
            x = dt.datetime.strptime(row[1], '%Y-%m-%d')
            if (x >= sd and x <= ed):
                temp_calc.append(int(row[3]))

        #print(temp_calc)
        max_temp = max(temp_calc)
        min_temp = min(temp_calc)
        mean_temp = mean(temp_calc)
        temp_stats.update({"max_temp": max_temp, "min_temp": min_temp, "mean":mean_temp})

    return temp_stats



# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)

