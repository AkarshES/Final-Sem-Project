from server import db

class LogsetMetadata(db.Document):
    '''
    An inheritable class that represents the metadata for a logset stored in another location
    '''
    name = db.StringField(required = True)
    creator_name = db.StringField(required = True)
    fields = db.ListField(db.StringField())
    users_with_access = db.ListField(db.StringField(), required = True)

    meta = {
        'allow_inheritance': True,
        'indexes': [
            {'fields': ('name', 'creator_name'), 'unique': True}
        ]
    }

class ApacheAccessLogsetMetadata(LogsetMetadata):
    '''
    A class that represents the metadata for an apache access logset
    '''
    fields = db.ListField(db.StringField()\
        , default = ["status", "client_ip", "browser", "browser_string", "request", "request_size", "base_url", "date", "referer", "device", "os", "request_country"]\
        )
