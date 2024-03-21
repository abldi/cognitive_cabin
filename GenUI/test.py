import dash
from dash import html, dcc, Input, Output
from datetime import datetime
import dash_bootstrap_components as dbc

# Create a Dash application

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.css.config.serve_locally = True


#Alternative contents for On and Off
on_content=[dbc.Col(
                html.Div(
                        className='showContentPlacer',
                        children=[
                            html.P("Example text of AI speech",style={"color":"white","font-size":"50px"})
                        ]
                ),
                class_name='textColumn',
            ),
            dbc.Col(
                html.Div(
                        className='showContentPlacer',
                        children=[
                            html.Img(src="assets\\img\\screenshot.png",className='resizable-img'),
                        ]
                ),
                class_name='genUIColumn'
            )]


off_content=[
    html.Div(
        className="offPlaceholder",
        children=[
            html.Img(src="assets\\img\\logo.png",className='resizable_img'),
            html.P("Cognitive Cabin",style={"color":"white","font-size":"50px"})
        ]
    )
]


# Define the layout of the app
app.layout = html.Div(
    className='background',
    children=[
        dbc.Row(
            children=[
                #Navigation bar
                html.Div(
                    className='topBar',
                    children=[
                        html.Div(
                            className='datetime',
                            children=[
                                    html.Div(
                                        className='clockStyle',
                                        children=[
                                            html.P(id='timenow', className='textDateTime', children='02:00:00'),
                                            dcc.Interval(
                                                id='interval-clock',
                                                interval=1000,  # each second
                                                n_intervals=0
                                            )
                                        ]
                                    ),
                                    html.Div(
                                        className='dayStyle',
                                        children=[
                                            html.P(id='weekday', className='textDateTime', children='Tue'),
                                            dcc.Interval(
                                                id='interval-weekday',
                                                interval=60*1000,  # each minute
                                                n_intervals=0
                                            )
                                        ]
                                    )
                            ]
                        ),
                        html.Div(
                            className='tempStyle',
                            children=[
                                html.P(id='currentTemp', className='textTemp', children='24º')
                            ]
                        )
                    ]
                )
            ]
        ),
        dbc.Row(
            class_name='mainContent',
            id='main',
            children=[
            dbc.Col(
                html.Div(
                        className='showContentPlacer',
                        children=[
                            html.P("Example text of AI speech",style={"color":"white","font-size":"50px"})
                        ]
                ),
                class_name='textColumn',
            ),
            dbc.Col(
                html.Div(
                        className='showContentPlacer',
                        children=[
                            html.Img(src="assets\\img\\screenshot.png",className='resizable-img')
                        ]
                ),
                class_name='genUIColumn'
            )
        ]),
        dbc.Row(
            class_name='bottomButton',
            children=[
                html.Div(
                    className='buttonPlacer',
                    children=[
                        dbc.Button(
                            "On",
                            id='on_off',
                            className='onoffButton',
                            
                        )
                    ]
                )
            ]   
        )
        
    ]
)


#Functions for it to work
@app.callback(
    Output('timenow', 'children'),
    [Input('interval-clock', 'n_intervals')]
)
def update_time(n):
    current_time = datetime.now().strftime('%H:%M:%S')
    return current_time

@app.callback(
    Output('weekday', 'children'),
    [Input('interval-weekday', 'n_intervals')]
)
def update_weekday(n):
    weekdays = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    current_day = datetime.now().weekday()
    return weekdays[current_day]

@app.callback(
    Output('main', 'children'),
    [Input('on_off', 'n_clicks')]
)
def cambiar_contenido(n_clicks):
    if n_clicks is not None:
        if n_clicks % 2 == 0:  # Alternar entre el contenido inicial y el alternativo
            return on_content
        else:
            return off_content
    else:
        return on_content

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)