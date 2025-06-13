import streamlit as st
import numpy as np
import os, glob
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates

def get_rectangle_coords(
    points: tuple[tuple[int, int], tuple[int, int]],
) -> tuple[int, int, int, int]:
    point1, point2 = points
    minx = min(point1[0], point2[0])
    miny = min(point1[1], point2[1])
    maxx = max(point1[0], point2[0])
    maxy = max(point1[1], point2[1])
    return (
        minx,
        miny,
        maxx,
        maxy,
    )

def full_path(fname):
    #return fname
    return f'{st.session_state.data_root}/{fname}'
