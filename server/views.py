from . import app
from views_logic import *

app.add_url_rule('/signin', view_func=signin, methods=['GET', 'POST'])
app.add_url_rule('/signout', view_func=signout)
app.add_url_rule('/signup', view_func=signup, methods=['GET', 'POST'])
app.add_url_rule('/changePassword', view_func=changePassword, methods=['GET', 'POST'])

app.add_url_rule('/', view_func=index)
app.add_url_rule('/logsets', view_func=upload_logset, methods=['POST'])
app.add_url_rule('/logsets', view_func=get_logsets, methods=['GET'])
app.add_url_rule('/data/<string:collection_name>', view_func=log_data_retriever)

app.add_url_rule('/sample_data/<path:filename>', view_func=sample_data_returner)
