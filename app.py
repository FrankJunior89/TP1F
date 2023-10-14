from flask import Flask,request,render_template
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    OrderBy,
)
from google.analytics.data_v1beta.types import RunReportRequest as Run 
import logging
import requests
import os
import pandas as pd
import numpy as np





app = Flask(__name__)

# Configuration pour servir des fichiers statiques
app.static_url_path = '/static'
app.static_folder = 'static'

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'Test-4ad6fecd71e5.json'
#property_id = '407503759'
property_id = '410311446'

client = BetaAnalyticsDataClient()

def format_report(req):
    response = client.run_report(req)
    
    # Row index
    row_index_names = [header.name for header in response.dimension_headers]
    row_header = []
    for i in range(len(row_index_names)):
        row_header.append([row.dimension_values[i].value for row in response.rows])

    row_index_named = pd.MultiIndex.from_arrays(np.array(row_header), names = np.array(row_index_names))
    # Row flat data
    metric_names = [header.name for header in response.metric_headers]
    data_values = []
    for i in range(len(metric_names)):
        data_values.append([row.metric_values[i].value for row in response.rows])

    output = pd.DataFrame(data = np.transpose(np.array(data_values, dtype = 'f')), 
                          index = row_index_named, columns = metric_names)
    return output

req = Run(
        property='properties/'+property_id,
        dimensions=[Dimension(name="month"), 
                    Dimension(name="sessionMedium")],
        metrics=[Metric(name="averageSessionDuration"), 
                 Metric(name="activeUsers")],
        order_bys = [OrderBy(dimension = {'dimension_name': 'month'}),
                    OrderBy(dimension = {'dimension_name': 'sessionMedium'})],
        date_ranges=[DateRange(start_date="2022-06-01", end_date="today")],
    )

nb_users = format_report(req)['activeUsers'].sum()

@app.route('/', methods=['GET', 'POST'])
def hello_world(nb_users=nb_users):
    prefix_google = """
    <!-- Google tag (gtag.js) -->
    <script async
    src="https://www.googletagmanager.com/gtag/js?id=G-55763RC5D7"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-LGFTF0XVHD');
    </script>
    """


    return prefix_google + render_template('home.html',nb_users=nb_users)

@app.route("/make_google_request", methods=["POST"])
def make_google_request():
    try:
        # Make a request to Google
        response = requests.get("https://www.google.com/")

        # Check if the request was successful
        if response.status_code == 200:
            return render_template('home.html',nb_users=nb_users,output_cookies=response.cookies.get_dict(),output_text=response.text)
        else:
            return "Google request failed with status code: " + str(response.status_code)
    except Exception as e:
        return "An error occurred: " + str(e)
    

@app.route("/analytics_request", methods=["POST"])
def make_analytics_request():
    try:
        # Make a request to Google
        response = requests.get("https://analytics.google.com/analytics/web/#/p407503759/reports/intelligenthome")

        # Check if the request was successful
        if response.status_code == 200:
            return render_template('home.html',nb_users=nb_users,output_cookies=response.cookies.get_dict(),output_text=response.text)
        else:
            return "Request failed with status code: " + str(response.status_code)
    except Exception as e:
        return "An error occurred: " + str(e)

@app.route('/logger', methods=["GET","POST"])
def logger_page():
    # Log a message on the server-side
    with open('app.log', 'r') as log_file:
        log_message = log_file.read()

    logging.warning(log_message)
    log_script = """<script>console.log("Je suis NFJ")</script>"""
    
    return render_template('home.html', output_text=log_message)

if __name__ == "__main__":
    app.run()

