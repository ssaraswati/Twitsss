from couchdb.mapping import Document, TextField, IntegerField, DateTimeField, DecimalField


class Tweet(Document):
    created_at = DateTimeField()
    text = TextField()
    city = TextField()
    user_id = IntegerField()
    user_home = TextField()
    iso_language_code = TextField()
    source = TextField()
    type = TextField()
    latitude = DecimalField()
    longitude = DecimalField()