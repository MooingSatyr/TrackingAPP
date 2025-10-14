import plotly.graph_objects as go
import plotly.express as px


def get_figure(df, zu_df, axis_ranges, x_axis, y_axis):

    fig = px.scatter(df, x=x_axis, y=y_axis)

    fig.update_traces(
        customdata=df.index,
        mode="markers",
        marker={"color": "rgb(0, 0, 150)", "size": 12, "opacity": 0.7},
    )

    fig.add_trace(
        go.Scatter(
            x=zu_df[x_axis].to_list(),
            y=zu_df[y_axis].to_list(),
            mode="markers+text",
            text=zu_df["Name"],
            marker=dict(size=22, color=zu_df["Color"].to_list(), symbol="triangle-up"),
        )
    )

    # Добавляем отдельный trace для последней точки
    last_point = df.iloc[[-1]]  # последняя точка

    if y_axis == "y":
        fig.add_scatter(
            x=last_point["x"],
            y=last_point[y_axis],
            mode="markers+text",
            marker=dict(size=12, color="red"),
            text=["🡇"],
            textposition="top center",
        )
    else:
        fig.add_scatter(
            x=last_point["x"],
            y=last_point[y_axis],
            mode="markers+text",
            marker=dict(size=12, color="red"),
            text=["🡇"],
            textposition="top center",
        )

    fig.update_layout(
        xaxis=dict(range=axis_ranges["x"]),
        yaxis=dict(range=axis_ranges[y_axis]),
        uirevision="fixed",
    )

    fig.update_traces(showlegend=False, selector=dict(type="scatter"))

    return fig


def expand_range(vmin, vmax, pad_ratio=0.2):
    """Добавляем отступ к диапазону"""
    if vmin == vmax:
        return vmin - 1, vmax + 1
    delta = (vmax - vmin) * pad_ratio
    return vmin - delta, vmax + delta
