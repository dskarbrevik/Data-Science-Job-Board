import dash

from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go


class tester():

    def __init__(self):
        self.example = ["No"]*10


test = tester()
test.example



def create_tags():
    tags = []
    for i in range(10):
        tags.append(html.Div([html.A(html.Button([html.Span('Data Scientist - Google', style={'display':'block','border':'1px solid black', 'width':'auto', 'height':'auto'}), html.Span('San Francisco, CA', style={'display':'inline','border':'1px solid black', 'width':'auto', 'height':'auto'})], className='job-button'),
                                     href='https:/www.google.com',
                                     target="_blank", style={'verticalAlign':'middle', 'display':'inline-block'}),
                              html.Button('APPLIED', className='job-button', style={'backgroundColor':'#fff', 'fontSize':'12', 'marginLeft':'10',
                                                                                    'display':'inline-block', 'verticalAlign':'middle'})],
                              style={'verticalAlign':'middle', 'marginBottom':'10'}))

    return (tags)


# define the app
app = dash.Dash()

app.css.append_css({"external_url":"https://codepen.io/chriddyp/pen/bWLwgP.css"})

# app.head = [html.Link(rel='stylesheet', href='./static/stylesheet.css')]

app.layout = html.Div(create_tags())

# @app.callback(
#     Output(),
#     [Input()]
# )
# def update_applied(input_val):
#     test.example[i] = input_val

if __name__ == '__main__':
    app.run_server(debug=True)
