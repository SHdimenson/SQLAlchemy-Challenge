# Import Flask
from flask import Flask, jsonify

# Dependencies and Setup
import numpy as np
import datetime as dt

# Python SQL Toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.pool import StaticPool
import dateutil.parser as dparser

# Database Setup by creating engine to the db path
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# Reflect hawaii database into Base 
Base = automap_base()
# Reflect all the tables in hawaii db 
Base.prepare(engine, reflect=True)

# Create instances each Table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Setting-up Flask
# Initialize Flask app
app = Flask(__name__)

# set-up all the routes 
@app.route("/api/v1.0/precipitation")
def percipation():
    # Create our session (thread) from Python to the DB
    session = Session(engine)
    
    date = session.query(Measurement.date).order_by(Measurement.date.desc())[0][0]
    latest_date = dt.datetime.strptime(date, "%Y-%m-%d").date()
    latest_12 = latest_date - dt.timedelta(days=365)
    percipitation_data = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc()).filter(Measurement.date >= latest_12 ).all()
    
    session.close()

    return dict(percipitation_data)
        

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (thread) from Python to the DB
    session = Session(engine)
    
    stations = session.query(Station.id, Station.station).distinct().all()
    
    session.close()
    
    results = []
    for row in stations:
        station = {}
        station["id"] = row[0]
        station["station"] = row[1]
        results.append(station)
    return jsonify(results)
    

@app.route("/api/v1.0/tobs") 
def tobs():
    # Create our session (thread) from Python to the DB
    session = Session(engine)
    
    active_stations = session.query(Measurement.id, Station.id, Measurement.station).\
                    filter(Station.station == Measurement.station).\
                    group_by(Measurement.station).\
                    order_by(Measurement.id.desc()).all()
    most_active_station = active_stations[0][1]
    
    recent_date = session.query(Measurement.date).filter(Station.station == Measurement.station).filter(Station.id == most_active_station).order_by(Measurement.date.desc())[0][0]
    recent_date = dt.datetime.strptime(recent_date, "%Y-%m-%d").date()
    recent_year = recent_date - dt.timedelta(days=365)
    recent_year_temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= recent_year).order_by(Measurement.date.desc()).all()
    
    session.close()
    
    return dict(recent_year_temp)
    

@app.route("/api/v1.0/<start_date>") 
def start_date(start_date):  

    session = Session(engine)
    
    result = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.tobs).filter(Measurement.date >= start_date).first()
    
    session.close()
    
    aggre = {}
    aggre["Date"]= result[0]
    aggre["Min"] = result[1]
    aggre["Max"] = result[2]
    aggre["Average"] = result[3]
    
    return aggre
    
    
@app.route("/api/v1.0/<start_date>/<end_date>") 
def range_date(start_date, end_date):
    session = Session(engine)
    
    start_date = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
    start_date = dt.datetime.strptime(end_date, "%Y-%m-%d").date()
    result = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                filter(Measurement.date >= start_date).filter(Measurement.date <= start_date)[0]

    session.close()
    
    aggre = {}
    aggre["Date"]= result[0]
    aggre["Min"] = result[1]
    aggre["Max"] = result[2]
    aggre["Average"] = result[3]
    return aggre
        
@app.route("/api/v1.0/questions") 
def questions():
    return """<html>
            <center>
            <img src="/static/silly.png", alt="There you go!!!", width="700",height="680" />
            </center>
            </html>"""

# set-up Home routes
@app.route("/")
def welcomepage():
    return """<html>
                        <h1>Welcome to Hawaii Climate Analysis!!!</h1>
                        <h4> By Shilpa...</h4>
                        <a href = "http://climate.geography.hawaii.edu/interactivemap.html" target = "_blank" ><img src="/static/hawaii_climate.png",width="718" height="135", alt="Hawaii Climate Analysis"/></a>
                        <h2><b>Analysis</b><img src="/static/Hawaii_surfing2.png",width="300",height="115", style="float:right", alt="Surf's up!!!"></h2>
                                <p><i>Below are the analysis performed on the Hawaii Climate data: </i></p>
                                
                                <dl><dt><li><b>Percipitation Data</b></li></dt>
                                    <dd><a href="/api/v1.0/precipitation" target = "_blank">Percipitation(last 12-months)</a></dd>
                                    <dd> Reurns 'Date' & 'Percipitation' for last 12-month period</dd>
                                </dl>
                                
                                <dl><dt><li><b>Stations Data</b></li></dt>
                                    <dd><a href="/api/v1.0/stations" target = "_blank">Most active Stations</a></dd>
                                    <dd>Returns List of Station 'id's' & 'station names' in Hawaii </dd>
                                </dl>
                                
                                <dl><dt><li><b>Temperature of Bias(Tobs)</b></li></dt>
                                    <dd><a href="/api/v1.0/tobs" target = "_blank">Temperature of Bias for last 12-months</a></dd>
                                    <dd>Returns 'Date' & 'Temperature' of most active station in the last 12 month period </dd>
                                </dl>
                                
                                <dl><dt><li><b>MIN, MAX & AVERAGE Temperatures</b></li></dt>
                                    <dd><a href="/api/v1.0/2016-8-23" target = "_blank">Temperature Aggregations starting 2016-8-23</a></dd>
                                    <dd><a href="/api/v1.0/2017-6-23/2017-8-15" target = "_blank">Temperature Aggregations from 2016-8-23 to 2017-1-15</a></dd>
                                    <dd>Returns 'Min', 'Max' & 'Average' for the given date or range of dates</dd>
                                </dl>

                                <dl><dt><li><b>Question & Concerns</b></li></dt>
                                    <dd><a href="/api/v1.0/questions" target = "_blank">Have Questions?? Contact-us here</a></dd>
                                </dl>
            </html>"""

if __name__ == '__main__':
    app.run(debug=True)
