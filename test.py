from dash import Dash, html, dcc, Output, Input, State
import pandas as pd
import base64
import io

app = Dash(__name__)

app.layout = html.Div(
    [
        html.H3("Загрузите CSV или LOG файл"),
        dcc.Upload(
            id="upload-data",
            children=html.Div(["Перетащите или ", html.A("выберите файл")]),
            multiple=True,
            style={
                "width": "80%",
                "height": "80px",
                "lineHeight": "80px",
                "borderWidth": "2px",
                "borderStyle": "dashed",
                "borderRadius": "10px",
                "textAlign": "center",
                "margin": "10px auto",
            },
        ),
        html.Div(id="output-data"),
    ]
)


@app.callback(
    Output("output-data", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
)
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        dfs = []
        for content, name in zip(list_of_contents, list_of_names):
            content_type, content_string = content.split(",")
            decoded = base64.b64decode(content_string)
            try:
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
                dfs.append(df)
            except Exception as e:
                return f"⚠️ Ошибка при чтении {name}: {e}"

        df = pd.concat(dfs, ignore_index=True)
        return html.Div(
            [html.H5(f"Загружено файлов: {len(dfs)}"), html.Pre(df.head().to_string())]
        )


if __name__ == "__main__":
    app.run(debug=True)
