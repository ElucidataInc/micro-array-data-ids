from plotly.subplots import make_subplots
import boto3
import sys
from boto3.dynamodb.conditions import Attr
from boto3.dynamodb.conditions import Key
from datetime import datetime
import csv
import json
import pandas as pd
import plotly
import plotly.graph_objects as go
import os

testing = False


if not(testing):
    os.system("rm -rf results")
    os.system("mkdir results")
now = datetime.now()
year = now.year


def number_of_days(y, m):
    leap = 0
    if y % 400 == 0:
        leap = 1
    elif y % 100 == 0:
        leap = 0
    elif y % 4 == 0:
        leap = 1
    if m == 2:
        return 28 + leap
    list = [1, 3, 5, 7, 8, 10, 12]
    if m in list:
        return 31
    return 30


def start_epoc(year, month):
    return round((datetime.strptime(str(year) + "-" + str(month) + "-01T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ") - datetime(1970, 1, 1)).total_seconds() * 1000)


def end_epoc(year, month):
    return round((datetime.strptime(str(year) + "-" + str(month) + "-" + str(number_of_days(int(year), int(month))) + "T23:59:59.999Z", "%Y-%m-%dT%H:%M:%S.%fZ") - datetime(1970, 1, 1)).total_seconds() * 1000)


def get_data(table_name, range):
    client = boto3.resource('dynamodb', aws_access_key_id=sys.argv[1],
                            aws_secret_access_key=sys.argv[2], region_name="us-west-2")

    table = client.Table(table_name)

    scan_kwargs = {
        'FilterExpression': Key('created_ts').between(*range),
    }

    response = table.scan(**scan_kwargs)

    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = table.scan(
            ExclusiveStartKey=response['LastEvaluatedKey'], **scan_kwargs)
        data.extend(response['Items'])

    return data


date_to_epoc = {
    "Q1": (start_epoc(year, 1), end_epoc(year, 3)),
    "Q2": (start_epoc(year, 4), end_epoc(year, 6)),
    "Q3": (start_epoc(year, 7), end_epoc(year, 9)),
    "Q4": (start_epoc(year, 10), end_epoc(year, 12)),
    "1": (start_epoc(year, 1), end_epoc(year, 1)),
    "2": (start_epoc(year, 2), end_epoc(year, 2)),
    "3": (start_epoc(year, 3), end_epoc(year, 3)),
    "4": (start_epoc(year, 4), end_epoc(year, 4)),
    "5": (start_epoc(year, 5), end_epoc(year, 5)),
    "6": (start_epoc(year, 6), end_epoc(year, 6)),
    "7": (start_epoc(year, 7), end_epoc(year, 7)),
    "8": (start_epoc(year, 8), end_epoc(year, 8)),
    "9": (start_epoc(year, 9), end_epoc(year, 9)),
    "10": (start_epoc(year, 10), end_epoc(year, 10)),
    "11": (start_epoc(year, 11), end_epoc(year, 11)),
    "12": (start_epoc(year, 12), end_epoc(year, 12)),
}

dataset_id = {
    6584: "geo_sc_connector",
    6575: "micro_array",
    6583: "rnaseq_dee2_human",
    6595: "rnaseq_dee2_mouse",
    6623: "rnaseq_dee2_human_revamped",
    6628: "rnaseq_dee2_rat",
    6647: "rna_dee2_celegans",
    6658: "rna_dee2_ecoli",
    6682: "rna_dee2_athaliana",
    6683: "rna_dee2_drerio",
    6714: "rna_dee2_scerevisiae"
}

dataset_id_success = {
    "geo_sc_connector": [],
    "micro_array": [],
    "rnaseq_dee2_human": [],
    "rnaseq_dee2_mouse": [],
    "accumulative_per_day": [],
    "rnaseq_dee2_human_revamped": [],
    "rnaseq_dee2_rat": [],
    "rna_dee2_celegans": [],
    "rna_dee2_ecoli": [],
    "rna_dee2_athaliana": [],
    "rna_dee2_drerio": [],
    "rna_dee2_scerevisiae": []
}
dataset_id_error = {
    "geo_sc_connector": [],
    "micro_array": [],
    "rnaseq_dee2_human": [],
    "rnaseq_dee2_mouse": [],
    "accumulative_per_day": [],
    "rnaseq_dee2_human_revamped":[],
    "rnaseq_dee2_rat":[],
    "rna_dee2_celegans": [],
    "rna_dee2_ecoli": [],
    "rna_dee2_athaliana": [],
    "rna_dee2_drerio": [],
    "rna_dee2_scerevisiae": []

}

dataset_id_color = {
    "geo_sc_connector": 'Blue',
    "micro_array": 'Green',
    "rnaseq_dee2_human": 'Red',
    "rnaseq_dee2_mouse": 'Violet',
    "accumulative_per_day": 'Pink',
    "total_accumulative": 'Orange',
    "rnaseq_dee2_human_revamped": "Yellow",
    "rnaseq_dee2_rat": "Goldenrod",
    "rna_dee2_celegans": "#636EFA",
    "rna_dee2_ecoli": "#AB63FA",
    "rna_dee2_athaliana": "Magenta",
    "rna_dee2_drerio": "#00CC96",
    "rna_dee2_scerevisiae": "#FF6692"
}

one_day = 86400000
monthly_data = {}

for number in range(1, now.month + 1):
    new_range = date_to_epoc[str(number)]
    table_name = "compute-prod-job-id-store-v1"
    if not(testing):
        data = get_data(table_name, new_range)
        with open("./results/compute_jobs_" + str(number) + ".csv", 'w',) as csvfile1:
            writer = csv.writer(csvfile1)
            writer.writerow(['project_id', 'job_id', 'created_ts', 'state'])
            for item in data:
                if item["project_id"] in list(dataset_id.keys()):
                    writer.writerow(
                        (item["project_id"], item["job_id"], item["created_ts"], item["state"]))
    df = pd.read_csv("./results/compute_jobs_" + str(number) + ".csv")
    latest_time = date_to_epoc[str(number)][0]
    passed_day = 0
    monthly_data[str(number)] = {}
    while latest_time < date_to_epoc[str(number)][1]:
        passed_day += 1
        for each_id in list(dataset_id.keys()):
            if not (str(passed_day) in monthly_data[str(number)].keys()):
                monthly_data[str(number)][str(passed_day)] = {}
            success_rows = df[(df['project_id'] == each_id) & (df['state'] == 'SUCCESS') & (
                df['created_ts'] >= latest_time) & (df['created_ts'] <= latest_time+one_day)].shape[0]
            error_rows = df[(df['project_id'] == each_id) & (df['state'].str.contains('ERROR')) & (
                df['created_ts'] >= latest_time) & (df['created_ts'] <= latest_time+one_day)].shape[0]

            if error_rows > 0 or success_rows > 0:
                monthly_data[str(number)][str(passed_day)][dataset_id[each_id]] = {
                    "success": success_rows, "error": error_rows
                }
        if len(monthly_data[str(number)][str(passed_day)].keys()) == 0:
            del monthly_data[str(number)][str(passed_day)]
        latest_time += one_day

with open('./results/result.json', 'w') as fp:
    json.dump(monthly_data, fp, indent=4)

x_axis = []
for month in monthly_data.keys():
    for day in monthly_data[month].keys():
        x_axis.append(month + "/" + day)
        total_success = 0
        total_error = 0
        for each_data_type in dataset_id_error.keys():
            if each_data_type != "accumulative_per_day":
                data_to_fill = [None, None]
                try:
                    data_to_fill = [monthly_data[month][day][each_data_type]["success"],
                                    monthly_data[month][day][each_data_type]["error"]]
                except Exception:
                    pass
                dataset_id_success[each_data_type].append(data_to_fill[0])
                dataset_id_error[each_data_type].append(data_to_fill[1])
                if not (data_to_fill[0] is None):
                    total_success += data_to_fill[0]
                    total_error += data_to_fill[1]

        dataset_id_success['accumulative_per_day'].append(total_success)
        dataset_id_error['accumulative_per_day'].append(total_error)

cuml_error_final = []
cuml_error_total = 0
for cumul in dataset_id_error['accumulative_per_day']:
    cuml_error_total += cumul
    cuml_error_final.append(cuml_error_total)

cuml_success_final = []
cuml_success_total = 0
for cumul in dataset_id_success['accumulative_per_day']:
    cuml_success_total += cumul
    cuml_success_final.append(cuml_success_total)

# fig = go.Figure()
fig = make_subplots(rows=2, cols=1, row_heights=[0.6, 0.4],
                    subplot_titles=("Individual results", "Accumulative results"), vertical_spacing=0.07,
                    x_title='<b>Days in Day/Month format</b>',
                    y_title='<b># of public data set connector runs</b>')


for each_data_type in dataset_id_success:
    if each_data_type != "accumulative_per_day":
        fig.add_trace(go.Scatter(
            x=x_axis,
            y=dataset_id_success[each_data_type],
            name=each_data_type + " success",  # Style name/legend entry with html tags
            # connectgaps=True # override default to connect the gaps
            mode='lines+markers',
            marker=dict(
                size=12,
                color=dataset_id_color[each_data_type],
            ),
            connectgaps=True  # override default to connect the gaps
        ),
            row=1, col=1

        )

for each_data_type in dataset_id_error:
    if each_data_type != "accumulative_per_day":
        fig.add_trace(go.Scatter(
            x=x_axis,
            y=dataset_id_error[each_data_type],
            name=each_data_type + " error",  # Style name/legend entry with html tag
            mode='lines+markers',
            marker_symbol="x",
            marker=dict(
                size=12,
                color=dataset_id_color[each_data_type],
            ),
            connectgaps=True  # override default to connect the gaps
        ),
            row=1, col=1

        )
fig.add_trace(go.Scatter(
    x=x_axis,
    y=cuml_success_final,
    name="all success",  # Style name/legend entry with html tag
    mode='lines+markers',
    marker=dict(
        size=12,
        color='Orange',
    ),
    connectgaps=True  # override default to connect the gaps
),
    row=2, col=1

)

fig.add_trace(go.Scatter(
    x=x_axis,
    y=cuml_error_final,
    name="all errors",  # Style name/legend entry with html tag
    mode='lines+markers',
    marker_symbol="x",
    marker=dict(
        size=12,
        color='Orange',
    ),
    connectgaps=True  # override default to connect the gaps
),
    row=2, col=1

)

fig.add_trace(go.Scatter(
    x=x_axis,
    y=dataset_id_success["accumulative_per_day"],
    name="per day success",  # Style name/legend entry with html tag
    mode='lines+markers',
    marker=dict(
        size=12,
        color='Pink',
    ),
    connectgaps=True  # override default to connect the gaps
),
    row=1, col=1

)

fig.add_trace(go.Scatter(
    x=x_axis,
    y=dataset_id_error["accumulative_per_day"],
    name="per day errors",  # Style name/legend entry with html tag
    mode='lines+markers',
    marker_symbol="x",
    marker=dict(
        size=12,
        color='Pink',
    ),
    connectgaps=True  # override default to connect the gaps
),
    row=1, col=1

)
fig.update_layout(title_text='<b>Public dataset addition rate</b>',
                  title_x=0.5,
                  font=dict(
                      size=18,
                  )
                  )
plotly.offline.plot(fig, filename='./results/index.html')

fig.show()
