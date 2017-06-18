import couchdb
from couchdb import ResourceNotFound
import config as cfg


class CouchDB(object):
    db = None

    def __init__(self):
        server = 'http://' + str(cfg.couch['host']) + ':' + str(cfg.couch['port'])

        if len(cfg.couch['user']) > 0 and len(cfg.couch['password']) > 0:
            server = 'http://' + str(cfg.couch['user']) + ":" + str(cfg.couch['password']) + "@" + str(
                cfg.couch['host']) + ':' + str(cfg.couch['port'])

        database_name = cfg.couch['db']
        try:
            couch_client = couchdb.Server(server)
        except:
            print("Cannot find CouchDB Server ... Exiting\n")
            raise
        try:
            self.db = couch_client[database_name]
        except ResourceNotFound:
            print("Couldn't find database trying to create it")
            self.db = couch_client.create(database_name)
        except Exception as e:
            print("Couldn't load specified database: {}".format(database_name))
            print("Confirm database has been created")
            print(type(e).__name__)

    def save(self, data):
        return self.db.save(data)

    def update(self, data):
        return self.db.update(data)

    def get(self, doc_id):
        return self.db.get(doc_id)

    def get_db(self):
        return self.db
