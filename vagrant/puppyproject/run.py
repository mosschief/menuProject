__author__ = 'mossc'
from puppyproject import app
app.secret_key = 'super secret key'
app.debug = True
app.run(host='0.0.0.0', port=5000)