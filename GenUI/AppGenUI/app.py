import dash
from dash import html

# Inicializar la aplicación Dash
app = dash.Dash(__name__,external_stylesheets=['GenUI\AppGenUI\style.css'])


# Layout: establecer el layout desde el archivo HTML
app.layout = html.Div([
    # Incrustar el contenido del archivo HTML
    html.Iframe(srcDoc=open('C:\\Users\\aleja\\Desktop\\Work\\GenUI\\assets\\marco_design_file.html', 'r').read(), width='1920px', height='1080px')
])

if __name__ == '__main__':
    app.run_server(debug=True)
