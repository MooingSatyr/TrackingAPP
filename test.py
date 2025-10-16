import plotly.graph_objects as go
fig = go.Figure(data=go.Scatter(y=[1,2,3]))
fig.write_image("screens/test.png")