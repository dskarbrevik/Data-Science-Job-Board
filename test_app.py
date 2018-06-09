import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from pandas_datareader import data as web
from datetime import datetime as dt
import plotly.graph_objs as go


example_x = ['Data Scientist', 'Data Analyst']
example_y = [909, 537]

app = dash.Dash()

app.layout = html.Div([
    html.H1('Stock Tickers'),
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'Coke', 'value': 'COKE'},
            {'label': 'Tesla', 'value': 'TSLA'},
            {'label': 'Apple', 'value': 'AAPL'}
        ],
        value='COKE'
    ),
    dcc.Graph(
    figure=go.Figure(
        data=[
            go.Bar(
                x=example_x,
                y=example_y,
                name='Rest of world',
                marker=go.Marker(
                    color='rgb(55, 83, 109)'
                )
            )
        ],
        layout=go.Layout(
            title='US Export of Plastic Scrap',
            showlegend=True,
            legend=go.Legend(
                x=0,
                y=1.0
            ),
            margin=go.Margin(l=40, r=0, t=40, b=30)
        )
    ),
    style={'height': 300, 'width':600},
    id='my-graph'
),
    html.P("Hey there this is some text I'm just testing this out hiiiii", style={'color':'blue', 'fontSize':14}, className='my-class')
    
])

# @app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
# def update_graph(selected_dropdown_value):
#     df = web.DataReader(
#         selected_dropdown_value, data_source='google',
#         start=dt(2017, 1, 1), end=dt.now())
#     return {
#         'data': [{
#             'x': df.index,
#             'y': df.Close
#         }]
#     }

if __name__ == '__main__':
    app.run_server()