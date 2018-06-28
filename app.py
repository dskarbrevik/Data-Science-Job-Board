import dash

from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from pandas_datareader import data as web
from datetime import datetime as dt
import plotly.graph_objs as go
from flask import send_from_directory
from collections import Counter
import pandas as pd
import numpy as np
import arrow


class app_creator():

    def __init__(self):
        self.top_jobs = []
        self.top_jobs_count = []
        self.top_terms = []
        self.top_terms_count = []
        self.locs = 0
        self.df = pd.DataFrame()
        self.df_jobs = pd.DataFrame()


    def get_all_data(self):
        # with open("../data/app_data/current_plot_data/top-jobs-{}.txt".format(arrow.now().format('MM-DD-YYYY'))) as file:
        with open("./data/current_plot_data/top-jobs-{0}.txt".format(arrow.now().shift(days=-1).format('MM-DD-YYYY'))) as file:
            lines = file.readlines()
            for line in lines:
                line = line.split(";")
                self.top_jobs.append(line[0])
                self.top_jobs_count.append(int(line[1]))

        # with open("../data/app_data/current_plot_data/top-terms-{}.txt".format(arrow.now().format('MM-DD-YYYY'))) as file:
        with open("./data/current_plot_data/top-terms-{0}.txt".format(arrow.now().shift(days=-1).format('MM-DD-YYYY'))) as file:
            lines = file.readlines()
            for line in lines:
                line = line.split(";")
                self.top_terms.append(line[0])
                self.top_terms_count.append(int(line[1]))

        self.df = pd.read_csv('./data/cleaned_ranked_scrapes/glassdoor-df-{0}.csv'.format(arrow.now().shift(days=-1).format('MM-DD-YYYY')), encoding="ISO-8859-1")
        self.df_jobs = self.df[self.df['applied']=="No"].iloc[:100]
        locations = self.df['location'].tolist()

        locs = []

        for i in range(len(locations)):
            try:
                state = locations[i].split(",")[1].strip()
                if len(state)==2:
                    locs.append(state)
            except:
                pass
        self.locs = Counter(locs)

        # self.df_jobs = pd.read_csv("../data/app_data/app_jobs/jobs-for-app-new.csv", encoding="ISO-8859-1")
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

            try:
                if len(position[i]) > 45:
                    position[i] = "{0:^42}...".format(position[i][:42])
                else:
                    position[i] = "{0:^42}".format(position[i])
            except:
                position[i] = "ERROR"

            try:
                if len(company[i]) > 45:
                    company[i] = "{0:^42}...".format(company[i][:42])
                else:
                    company[i] = "{0:^42}".format(company[i])
            except:
                company[i] = "ERROR"

            try:
                if len(location[i]) > 45:
                    location[i] = "{0:^42}...".format(location[i][:42])
                else:
                    location[i] = "{0:^42}".format(location[i])
            except:
                location[i] = "ERROR"


            jobs.append(html.Div([html.A(html.Button([html.Span('{0}'.format(position[i]),
                                                                style={'display':'block', 'marginBottom':'-20', 'marginTop':'0', 'fontSize':'14'}),
                                                      html.Span('{0}'.format(company[i]),
                                                                style={'display':'block', 'marginBottom':'-20', 'fontSize':'12', 'color':'black'}),
                                                      html.Span('({0})'.format(location[i]),
                                                                style={'display':'block'})],
                                                      id='job-button-{0}'.format(i),
                                                      style={'height':'80', 'width':'500', 'border-radius':'8px', 'border':'2px solid grey'}),
                                        href='{0}'.format(link[i]),
                                        target="_blank",
                                        style={'verticalAlign':'middle', 'display':'inline-block','height':'80', 'width':'500',
                                               'border-radius':'8px', 'marginLeft':'50', 'backgroundColor':'white'}),
                                html.Button(html.Span(u'\U00002764', style={'fontSize':'38', 'marginLeft':'-15', 'marginTop':'80', 'paddingTop':'40'}),
                                            id='good-button-{0}'.format(i),
                                            style={'background':'none', 'border':'none', 'fontSize':'12', 'display':'inline',
                                                   'width':'30', 'marginTop':'-20'}),
                                html.Button(html.Span(u'\U0001F5D9', style={'fontSize':'38', 'marginLeft':'-15', 'marginTop':'50'}),
                                            id='bad-button-{0}'.format(i),
                                            style={'background':'none', 'border':'none', 'fontSize':'12', 'display':'inline',
                                                   'width':'30'})],
                                style={'verticalAlign':'middle', 'marginBottom':'10', 'backgroundColor':'WhiteSmoke'}))



        return html.Div(jobs,style={'backgroundColor':'WhiteSmoke'})

    # LEFT HALF OF THE WEBSITE
    def get_jobs_view(self):

        return(html.Div([html.Div([html.H2('Job Listings', style={'width':'68.3%','marginBottom':'5','marginLeft':'210','marginRight':'-295',
                                                        'display':'inline-block'}),
                                   html.Span('(last updated: {})'.format(arrow.now().format('MM-DD-YYYY')))],
                                   style={'width':'100%'}),
                        html.Div([self.generate_jobs()], style={'display':'block','height':'82%', 'width':'38%', 'position':'fixed','overflow':'auto',
                                                                'backgroundColor':'WhiteSmoke'})],
                        style={'display':'inline-block', 'width':'39%', 'height':'100%', 'backgroundColor':'WhiteSmoke'}
                        ))

    # RIGHT HALF OF THE WEBSITE
    def get_plots_view(self):

        # colors = np.linspace(50,220,10)[::-1]
        # scl = []
        #
        # for i,color in enumerate(colors):
        #     scl.append([i/10,'rgb({0:.0f},{0:.0f},{0:.0f})'.format(color)])
        #     scl.append([(i+1)/10,'rgb({0:.0f},{0:.0f},{0:.0f})'.format(color)])

        scl=['#ECEFF1','#DADFE4','#C8D0D7','#B6C0C9','#A4B0BC','#91A1AF','#7F91A2','#6D8194','#5B7287','#49627A','#37536D',
             '#324C64','#2E445A','#293D50','#233546','#1E2E3C','#192632','#141F28','#0F171E','#0A1014']

        rgb = []

        for index in range(len(scl)):
            if(len(rgb) < 20):
                h = scl[index+3].lstrip('#')
                rgb.append([index/10,'rgb{}'.format(tuple(int(h[i:i+2], 16) for i in (0, 2 ,4)))])
                rgb.append([(index+1)/10,'rgb{}'.format(tuple(int(h[i:i+2], 16) for i in (0, 2 ,4)))])

        return(html.Div([html.Div(html.H2('Trends in Data Science', style={'marginTop':'60','marginLeft':'380'})),
                         html.Div([dcc.Graph(id='top-job-titles',figure=go.Figure(data=[go.Bar(x=self.top_jobs[:10],
                                                                            y=self.top_jobs_count[:10],
                                                                            name='Top jobs',
                                                                            marker=go.Marker(color='rgb(55, 83, 109)'))],
                                                               layout=go.Layout(title='Most Common Data Science Job Titles',
                                                                                paper_bgcolor = 'WhiteSmoke',
                                                                                plot_bgcolor = 'WhiteSmoke',
                                                                                showlegend=False,
                                                                                margin=go.Margin(l=40, r=100, t=40, b=200))),
                                              config={'modeBarButtonsToRemove':['pan2d', 'lasso2d',], 'displaylogo':False},
                                              style={'width':'45%','height':'400px', 'display':'inline-block','marginTop':'15', 'backgroundColor':'WhiteSmoke',
                                                     'marginLeft':'50'}),

                                    # top job skills
                                    dcc.Graph(id='top-terms',figure=go.Figure(data=[go.Bar(x=self.top_terms[:10],
                                                                            y=self.top_terms_count[:10],
                                                                            name='Top terms',
                                                                            marker=go.Marker(color='rgb(55, 83, 109)'))],
                                                               layout=go.Layout(title='Most Common Words in Data Science Job Descriptions',
                                                                                paper_bgcolor = 'WhiteSmoke',
                                                                                plot_bgcolor = 'WhiteSmoke',
                                                                                showlegend=False,
                                                                                margin=go.Margin(l=40, r=100, t=40, b=200))),
                                              config={'modeBarButtonsToRemove':['pan2d', 'lasso2d','zoomIn2d','zoomOut2d'], 'displaylogo':False},
                                              style={'width':'45%','height':'400px', 'display':'inline-block', 'marginTop':'15', 'backgroundColor':'WhiteSmoke',
                                                     'marginLeft':'10'}),
                                    dcc.Graph(id='job-locations',
                                              figure=go.Figure(data=[dict(type='choropleth',
                                                                         colorscale=rgb,
                                                                         autocolorscale=False, locationmode='USA-states',
                                                                         locations=list(self.locs.keys()), z=list(self.locs.values()),
                                                                         marker = dict(line=dict(color='rgb(255,255,255)', width=2)),
                                                                         colorbar=dict(title="Number of Listings"),
                                                                         zauto=False, zmin=0, zmax=150)],
                                                                layout=dict(title="Number of Job Listings by State",
                                                                            geo = dict(scope='usa', bgcolor='WhiteSmoke'),
                                                                            paper_bgcolor = 'WhiteSmoke',
                                                                            plot_bgcolor = 'WhiteSmoke')),
                                              # config={'displayModeBar':False},
                                              config={'modeBarButtonsToRemove':['pan2d', 'lasso2d', 'zoomInGeo','zoomOutGeo', 'select2d'], 'displaylogo':False},
                                              style={'width':'80%','height':'480px', 'marginTop':'-125', 'marginLeft':'100', 'backgroundColor':'WhiteSmoke'})],
                                        style={'backgroundColor':'WhiteSmoke'})],
                                    style={'display':'inline-block', 'float':'right', 'width':'61.8%', 'marginTop':'-110', 'backgroundColor':'WhiteSmoke'}
                                ))





# generates the view of the app
my_app = app_creator()
my_app.get_all_data()


# define the app
app = dash.Dash()

app.css.append_css({"external_url":"https://codepen.io/dskarbrevik/pen/bKmZaB.css"})

app.layout = html.Div([html.H1('Data Science Job Board', style={'width':'97.5%', 'margin':'auto 0', 'padding':'20px', 'text-align':'center',
                                                                'border':'3px solid black', 'display':'inline-block', 'height':'50',
                                                                'backgroundColor':'#37536D', 'color':'white', 'border-radius':'8px'}),
                       my_app.get_jobs_view(),
                       my_app.get_plots_view()],
                       style={'backgroundColor':'WhiteSmoke', 'width':'100%'})


if __name__ == '__main__':
    app.run_server(debug=True)
