from flask import Flask, redirect,url_for, render_template, request
# from werkzeug.wrappers import request
from search import alphaIndex, docIds, search
app = Flask(__name__)

# results = []

# @app.route('/')
# def index():
#    return render_template('search.html')

@app.route('/', methods=['POST', 'GET'])
def index_form():
   if request.method == "POST":
      text = request.form['search']
      return redirect(url_for("displayResults", query=text))
   else:
      return render_template('search.html')

@app.route('/<query>', methods=['POST', 'GET'])
def displayResults(query):
   if request.method == "POST":
      text = request.form['search']
      return redirect(url_for("displayResults", query=text))
   else:
      urls = []
      postings, total_time = search(query)
      for posting in postings:
            urls.append(docIds[int(posting[0])])

      return render_template('results.html', results=urls, time=total_time, query=query)


# @app.route('/results', methods=["GET"])
# def results():
#    return render_template('results.html')


if __name__ == '__main__':
   app.run(debug = True)