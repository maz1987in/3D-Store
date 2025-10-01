from app import create_app
#from db_migration import db_migrations
#db_migrations()

app = create_app()

if __name__ == "__main__":
    import os
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    app.run(port=port)