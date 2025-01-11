from flask import Flask, render_template, request, url_for, redirect


app = Flask(__name__)




@app.route('/')
def hello_world():
    return 'hello world'

@app.route('/html')
def html():
    return render_template('index.html')

'''
@app.route('/auswertungen')
def auswertungen():
    return render_template('auswertungen.html')
'''


@app.route('/auswertungen', methods=['GET', 'POST'])
def index_func():
    if request.method == 'POST':
        # do stuff when the form is submitted
        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('auswertungen'))
    # show the form, it wasn't submitted
    return render_template('auswertungen.html')

'''
@app.route('/monitoring', methods=['GET', 'POST'])
def index_func():
    if request.method == 'POST':
        # do stuff when the form is submitted
        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('monitoring'))
    # show the form, it wasn't submitted
    return render_template('monitoring.html')
'''

if __name__ == '__main__':
    app.run(debug=True)