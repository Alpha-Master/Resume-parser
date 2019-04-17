from flask import Flask
from flask import jsonify
from flask import request
import resumeParser as parser
app = Flask(__name__)

@app.route('/resume',methods=['GET'])
def getData():
    print(request.args.get('fileName', type = str))
    name = request.args.get('fileName', type = str)
    location = request.args.get('fileLocation', type = str)
    print(jsonify(parser.resumeParse(name,location)))
    return jsonify(parser.resumeParse(name,location))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8009)