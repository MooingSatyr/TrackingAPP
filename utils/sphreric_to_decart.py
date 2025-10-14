import pandas as pd
from numpy import sin, cos
import numpy as np


def to_decart(df: pd.DataFrame):
    az = np.deg2rad(df[" azimuth"])
    rng = df[" range"]
    elev = np.deg2rad(df[" elevation"])

    x = rng * cos(elev) * sin(az)
    y = rng * cos(elev) * cos(az)
    z = rng * sin(elev)
    df["x"] = x
    df["y"] = y
    df["z"] = z

    df.drop(columns=[" azimuth", " range", " elevation"], inplace=True)
