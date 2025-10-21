from app import create_app
#from db_migration import db_migrations
#db_migrations()

app = create_app()

if __name__ == "__main__":
    # Using port 5001 because port 5000 is used by macOS AirPlay
    app.run(debug=True, port=5001, host='0.0.0.0')