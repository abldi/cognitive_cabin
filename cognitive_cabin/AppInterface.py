import dash
from dash import html, dcc, Input, Output
from datetime import datetime
import dash_bootstrap_components as dbc
import threading
import logging


class AppInterface():

    #---------------------------------Methods------------------------------------------
    def __init__(self) -> None:

        
        #--------------------------------Attributes---------------------------------------
        # Create a Dash application
        self.app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP,"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"])

        #--------------------------------Interface config----------------------------------
       

        #Config for it to use local CSS
        self.app.css.config.serve_locally = True



        #Alternative contents for On and Off
        on_content=[dbc.Col(
                        html.Div(
                            id='animatedText',
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
        self.app.layout = html.Div(
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
                                id='animatedText',
                                className='showContentPlacer',
                                children=[
                                    html.P("Example text of AI speech",style={"color":"white","font-size":"50px"}),
                                    dcc.Interval(
                                                        id='interval-text-update',
                                                        interval=1000,  # each second
                                                        n_intervals=0
                                                    )
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
                                    html.I(className="fa fa-power-off"),
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

        @self.app.callback(
            Output('timenow', 'children'),
            [Input('interval-clock', 'n_intervals')]
        )
        def update_time(n):
            current_time = datetime.now().strftime('%H:%M:%S')
            return current_time

        @self.app.callback(
            Output('weekday', 'children'),
            [Input('interval-weekday', 'n_intervals')]
        )
        def update_weekday(n):
            weekdays = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
            current_day = datetime.now().weekday()
            return weekdays[current_day]

        @self.app.callback(
            Output('main', 'children'),
            [Input('on_off', 'n_clicks')]
        )
        def change_content(n_clicks):
            if n_clicks is not None:
                if n_clicks % 2 == 0:  # Alternar entre el contenido inicial y el alternativo
                    return on_content
                else:
                    return off_content
            else:
                return on_content
            
        @self.app.callback(
        Output('animatedText', 'children'),
        [Input('interval-text-update', 'n_intervals')]
        )
        def updateText(text):
            return text
        

    def startThreadInterface(self):
        self.InterfaceThread = threading.Thread(target=self.run_server_in_thread)
        self.InterfaceThread.daemon=True
        self.InterfaceThread.start()
    
    def run_server_in_thread(self):
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        self.app.run_server(debug=False,use_reloader=False)
        
    #It is stopped by killing main execution because of daemon
    # def stopThreadInterface(self):
    #     self.InterfaceThread.join()
    #     print("Interface exited succesfully")


    def _extractRecommendation(self,text):
    # Find the index where "Recommendation:" starts
        start_index = text.find("Recommendation:")
        
        # If "Recommendation:" is found
        if start_index != -1:
            # Extract the text starting from the end of "Recommendation:"
            recommendation_text = text[start_index + len("Recommendation:"):]
            # Remove leading and trailing whitespace
            recommendation_text = recommendation_text.strip()
            return recommendation_text
        else:
            return None  # Return None if "Recommendation:" is not found

    def sendToInterface(self,text):
        #Preprocess the text
        recom = self._extractRecommendation(text)
        if recom is not None: #there is a recommendation made
            #Append the part that is going to be presented on the interface
            self._showText(recom)

    
    def _showText(self,textToShow):
        self.app.layout['animatedText'].children = html.P(textToShow,style={"color":"white","font-size":"50px"})
        self.app.callback(Output('animatedText','children'),[])