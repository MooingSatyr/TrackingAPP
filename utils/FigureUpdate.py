import plotly.graph_objects as go


def get_polar_ra(df, zu_df, range_max):
    fig = go.Figure()

    # Наносит основные точки на полярный график
    fig.add_trace(
        go.Scatterpolar(
            r=df[" range"],
            theta=df[" azimuth"],
            mode="markers",
            marker=dict(size=6, color="blue"),
            name="Range-Azimuth",
        )
    )

    fig.add_trace(
        go.Scatterpolar(
            r=zu_df[" range"],
            theta=zu_df[" azimuth"],
            mode="markers+text",
            marker=dict(size=10, color=zu_df["Color"]),
            text=zu_df["Name"],
            textposition="top center",
            showlegend=False,
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(range=[0, range_max * 1.05]),
        ),
        uirevision="fixed",
    )
    last_point = df.iloc[[-1]]

    fig.add_trace(
        go.Scatterpolar(
            r=last_point[" range"],
            theta=last_point[" azimuth"],
            mode="markers+text",
            marker=dict(size=12, color="red"),
            text=["🡇"],
            textposition="top center",
            name="Последняя точка",
        )
    )

    fig.update_traces(showlegend=False)

    return fig


def expand_range_max(max_val, pad_ratio=0.05):
    """
    Строит диапазон радиальной оси от 0 до max_val с расширением.

    Args:
        max_val (float): максимальное значение.
        pad_ratio (float): процент расширения диапазона (0.05 = 5%).

    Returns:
        list: [0, max_val_padded]
    """
    if max_val is None:
        return [0, 1]

    if max_val == 0:
        return [0, 1]  # защита от деления на ноль

    pad = max_val * pad_ratio
    return [0, max_val + pad]
