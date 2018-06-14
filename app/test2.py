import dash
import dash_core_components as dcc
import dash_html_components as html


#Define Dash App
app=dash.Dash()

# TO ADD CSS VIA CDN
# app.css.append_css({
#     'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'

app.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar'}
                ],
                'layout': {
                    'title': 'Dash Data Visualization',
                    'height':500
                    }
                }
            ),
        ],
        style={'width': '10%', 'display': 'inline-block'}
        ),

    html.Div([
        html.Label('Multi-Select Dropdown'),
        dcc.Dropdown(
            options=[
                {'label': 'New York City', 'value': 'NYC'},
                {'label': 'Montreal', 'value': 'MTL'},
                {'label': 'San Francisco', 'value': 'SF'}
                ],
            value=['MTL', 'SF'],
            multi=True
        ),

        dcc.Graph(
            id='example-graph3',
            figure={
                'data': [
                    {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar'}
                ],
                'layout': {
                    'title': 'Dash Data Visualization',
                    'height':250
                    }
                }
            )
        ],
        style={'width': '10%', 'display': 'inline-block'}
        ),

    html.Div([
        dcc.Graph(
            id='example-graph4',
            figure={
                'data': [
                    {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar'}
                ],
                'layout': {
                    'title': 'Dash Data Visualization',
                    'height':500
                    }
                }
            )
        ],
        style={'width': '10%', 'display': 'inline-block', 'float': 'right'},
        )
    ]
)


if __name__ == '__main__':
    app.run_server()
