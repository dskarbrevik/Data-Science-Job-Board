import dash

from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from pandas_datareader import data as web
from datetime import datetime as dt
import plotly.graph_objs as go
from flask import send_from_directory
import pandas as pd
import numpy as np
import arrow


class app_creator():

    def __init__(self):
        self.top_jobs = []
        self.top_jobs_count = []
        self.top_terms = []
        self.top_terms_count = []

        self.df_jobs = pd.DataFrame()


    def get_all_data(self):
        # with open("../data/app_data/current_plot_data/top-jobs-{}.txt".format(arrow.now().format('MM-DD-YYYY'))) as file:
        with open("../data/app_data/current_plot_data/top-jobs-06-12-2018.txt") as file:
            lines = file.readlines()
            for line in lines:
                line = line.split(";")
                self.top_jobs.append(line[0])
                self.top_jobs_count.append(int(line[1]))

        # with open("../data/app_data/current_plot_data/top-terms-{}.txt".format(arrow.now().format('MM-DD-YYYY'))) as file:
        with open("../data/app_data/current_plot_data/top-terms-06-12-2018.txt") as file:
            lines = file.readlines()
            for line in lines:
                line = line.split(";")
                self.top_terms.append(line[0])
                self.top_terms_count.append(int(line[1]))

        self.df_jobs = pd.read_csv("../data/app_data/jobs-for-app.csv", encoding="ISO-8859-1")
        # self.df_jobs = self.df_jobs.sort_values(by=['rank'], ascending=False)
        # self.df_jobs = self.df_jobs.iloc[:100]

    # get jobs data for left half of website
    def generate_jobs(self):

        position = self.df_jobs['position'].tolist()
        company = self.df_jobs['company'].tolist()
        link = self.df_jobs['link'].tolist()
        location = self.df_jobs['location'].tolist()

        jobs = []

        for i in range(len(position)):
            jobs.append(html.Div([html.A(html.Button('{0} - {1} \n ({2})'.format(position[i], company[i], location[i]), className='job-button',
                                style={'borderColor':'black', 'backgroundColor':'#fff', 'width':'80%', 'fontSize':'20', 'marginBottom':'10'}),
                                href='{}'.format(link[i]), target="_blank")],
                                ),
                        html.Div([dcc.Checklist(options=[{'label':'Applied?', 'value':'Applied?'}], values='')],
                                 style={'display':'inline block'}))

        return html.Div(jobs)

    # LEFT HALF OF THE WEBSITE
    def get_jobs_view(self):

        return(html.Div([html.H1('Data Science Job Board', style={'margin':'0 auto'}), self.generate_jobs()],
                         style={'float':'left', 'width':'30%', 'height':'100%', 'overflow':'hidden',
                                'overflow-x':'auto', 'borderRight':'2px solid black'}
                        ))

    # RIGHT HALF OF THE WEBSITE
    def get_plots_view(self):

        return(html.Div([
                        # top position titles
                        dcc.Graph(figure=go.Figure(data=[go.Bar(x=self.top_jobs,
                                                                y=self.top_jobs_count,
                                                                name='Top jobs',
                                                                marker=go.Marker(color='rgb(55, 83, 109)'))],
                                                   layout=go.Layout(title='Most Common Data Science Job Titles',
                                                   showlegend=False,
                                                   margin=go.Margin(l=40, r=100, t=40, b=200)))),
                                  #style={'width':'75%', 'margin':'0 auto'}),

                        # top job skills
                        dcc.Graph(figure=go.Figure(data=[go.Bar(x=self.top_terms,
                                                                y=self.top_terms_count,
                                                                name='Top terms',
                                                                marker=go.Marker(color='rgb(55, 83, 109)'))],
                                                   layout=go.Layout(title='Most Common Words in Data Science Job Descriptions',
                                                   showlegend=False,
                                                   margin=go.Margin(l=40, r=100, t=40, b=200))))],
                                  #style={'width':'75%', 'margin':'0 auto'})],
                        style={'float':'left', 'width':'65%'}
                        ))

# generates the view of the app
my_app = app_creator()
my_app.get_all_data()


# define the app
app = dash.Dash()

app.head = [html.Link(rel='stylesheet', href='/static/stylesheet.css'),
    ('''
    <style type="text/css">
    html {
        font-size: 50px;
    }

    button:hover {
        background-color: black;
    }

    .job-button:hover{
        background-color: green;
    }
    </style>
    ''')]
    # html.Title(path)

app.layout = html.Div([my_app.get_jobs_view(), my_app.get_plots_view()])


if __name__ == '__main__':
    app.run_server(debug=True)
