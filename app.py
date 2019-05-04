# Note: There is no mention of stations in the instructions that i can find, so all calculations ignore it

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.sql.expression import text


import datetime as dt

# import Flask
from flask import Flask, jsonify

app = Flask(__name__)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

def get_twelve_months_ago():
	# Calculate the date 1 year ago from the last data point in the database
	latest_date = (session
					.query(func.max(Measurement.date))
					.first()
				)
	dt_latest_date = dt.datetime.strptime(latest_date[0],'%Y-%m-%d')
	return dt.date(dt_latest_date.year - 1, dt_latest_date.month, dt_latest_date.day)


@app.route("/")
def home():
	return ("""/api/v1.0/precipitation <br>
		/api/v1.0/stations <br>
		/api/v1.0/tobs <br>
		/api/v1.0/{start_date} <br>
		/api/v1.0/{start_date}/{end_date}"""
	)

@app.route("/api/v1.0/precipitation")
def precipitation():
	session = Session(engine)
	twelve_months_ago = get_twelve_months_ago() 
	# Perform a query to retrieve the data and precipitation scores
	precipitation = (session
					.query(Measurement.date, Measurement.prcp)
					.filter(Measurement.date > func.strftime('%Y-%m-%d', twelve_months_ago))
					.order_by(Measurement.date.desc())
					).all()	
	
	precipitation_dict = {}
	for precip in precipitation:
		precipitation_dict[precip[0]] = precip[1]

	return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
	session = Session(engine)
	stations = (session
             .query(Station.station, Station.name)
             .all()
            )
	return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
	session = Session(engine)
	twelve_months_ago = get_twelve_months_ago() 
	tobs = (session
            .query(Measurement.date, Measurement.tobs)
            .filter(Measurement.date > func.strftime('%Y-%m-%d', twelve_months_ago))
            .all()
        )
	temps = {}
	for t in tobs:
		temps[t[0]] = t[1]
	return jsonify(temps)

@app.route("/api/v1.0/<start>")
def stats_start(start):
	session = Session(engine)
	temperatures = (session
					.query(func.max(Measurement.tobs),
							func.min(Measurement.tobs), 
							func.avg(Measurement.tobs)
						)
					.filter(Measurement.date >= start)
					.first()
               	)

	results = {}
	results['highest'] = temperatures[0]
	results['lowest']  = temperatures[1]
	results['average'] = temperatures[2]
	return jsonify(results)

@app.route("/api/v1.0/<start>/<end>")
def stats_start_end(start, end):
	session = Session(engine)
	temperatures = (session
					.query(func.max(Measurement.tobs),
							func.min(Measurement.tobs), 
							func.avg(Measurement.tobs)
							)
					.filter(Measurement.date >= start, Measurement.date <= end)
					.first()
				)

	results = {}
	results['highest'] = temperatures[0]
	results['lowest']  = temperatures[1]
	results['average'] = temperatures[2]
	return jsonify(results)	


if __name__ == "__main__":
    app.run(debug=True)
