import dash
from dash import html
from dash import dcc
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go
import base64
import tempfile
import scipy.io.wavfile as wav
import fft_scanning
import numpy as np
external_stylesheets = [
    'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css',
]

uploader = html.Div([
    html.Div(
        dcc.Upload(
            id='upload-data',
            children=['Drag and Drop or ', html.A('Select Files')],
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=True),
        className="col")],
    className="row")
            

fft_data = html.Div(
    html.Div(dcc.Graph(id='fft-plot'), className="col"),
    className="row")

settings = html.Div(
    [
        html.Div(
            [
                html.Label("FFT Bins:"),
                dcc.Dropdown(
                    id='fft-bins-dropdown',
                    options=[{'label' : str(bins), 'value' : bins} for bins in [128, 256, 512, 1024, 2048, 4096, 8192, 16384]],
                    value=1024,
                ),
            ],
            className="col")
    ],
    className="row"
)

plot_pane = [uploader, fft_data, settings]

plotter_layout = html.Div(plot_pane, className="container")

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = plotter_layout
server=app.server

@app.callback(Output('fft-plot', 'figure'),
              [
                  Input('upload-data', 'contents'),
                  Input('fft-bins-dropdown', 'value'),
              ],
              [State('upload-data', 'filename')])
def update_output(list_of_contents, fft_bins, list_of_fn):
    fig = go.Figure()
    if list_of_contents is not None:
        for contents, fn in zip(list_of_contents, list_of_fn):
            if fn.endswith(".wav"):
                with tempfile.NamedTemporaryFile() as tempfn:
                    content_type, content_string = contents.split(",")
                    binary_data = base64.b64decode(content_string)
                    tempfn.write(binary_data)
                    fs, data = wav.read(tempfn.name)
                x, y = fft_scanning.fft_scanning(fs, data, fft_bins=fft_bins)
                for channel in range(y.shape[1]):
                    fig.add_trace(go.Scatter(x=x, y=20*np.log10(y[:, channel]), name=f"{fn}:{channel}"))
            else:
                pass
    fig.update_layout(title="Freuency analysis",
                      xaxis_title="Frequency (Hz)",
                      yaxis_title="Amplitude (dB)",
    )
    return fig
    


if __name__ == '__main__':
    app.run_server(debug=True)
