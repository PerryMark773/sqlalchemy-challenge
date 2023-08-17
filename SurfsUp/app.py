from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
from datetime import datetime, timedelta

app = Flask(__name__)

# Database setup
engine = create_engine("sqlite:///SurfsUp/Resources\hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station
Session = sessionmaker(bind=engine)

@app.route('/')
def home():
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session()
    try:
        # Retrieve the last 12 months of precipitation data
        last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
        one_year_ago = datetime.strptime(last_date, "%Y-%m-%d") - timedelta(days=365)
        
        prcp_data = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >= one_year_ago).all()
        
        # Convert the query results to a dictionary
        prcp_dict = {date: prcp for date, prcp in prcp_data}
        return jsonify(prcp_dict)
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        session.close()

@app.route('/api/v1.0/stations')
def stations():
    session = Session()
    try:
        stations_data = session.query(Station.station, Station.name).all()
        stations_list = [{"station": station, "name": name} for station, name in stations_data]
        return jsonify(stations_list)
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        session.close()

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session()
    try:
        # Identify the most active station
        most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
            group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

        # Retrieve the last 12 months of temperature observation data
        last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
        one_year_ago = datetime.strptime(last_date, "%Y-%m-%d") - timedelta(days=365)
        
        temp_data = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.station == most_active_station).\
            filter(Measurement.date >= one_year_ago).all()

        temp_list = [{"date": date, "temperature": temp} for date, temp in temp_data]
        return jsonify(temp_list)
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        session.close()

@app.route('/api/v1.0/<start>', defaults={'end': None})
@app.route('/api/v1.0/<start>/<end>')
def temp_range(start, end):
    session = Session()
    try:
        if end:
            results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        else:
            results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()

        temp_stats = [{"TMIN": min, "TAVG": avg, "TMAX": max} for min, avg, max in results]
        return jsonify(temp_stats)
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True, port=8080) 
    # was running into issues with the endpoint browser url loading indefinetly was able to get a 
    # work around by changing the port number 