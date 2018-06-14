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
        tags.append(html.Div([html.H1('Hi there!', style={'display':'inline-block'}),
                              html.Button('click me!', className='job-button',
                                          style={'borderColor':'black', 'backgroundColor':'#fff', 'width':'2%', 'fontSize':'20', 'marginBottom':'10'})]))

    return (tags)


# define the app
app = dash.Dash()

app.css.append_css({"https://github.com/dskarbrevik/Data-Science-Job-Board/blob/master/app/static/stylesheet.css"})

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
