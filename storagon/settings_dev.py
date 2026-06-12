from .settings import *
import mongoengine
import mongomock

# Override database for local dev environment to use SQLite
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
}

# Disconnect production MongoEngine and reconnect using mongomock in-memory client
mongoengine.disconnect()
db_connection = mongoengine.connect(db=MONGODB['NAME'], mongo_client_class=mongomock.MongoClient)
print("WARNING: Using settings_dev.py with local SQLite and mongomock.")
