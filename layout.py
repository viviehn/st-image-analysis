import streamlit as st
import utils
import numpy as np
import os, glob
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates

def folder_path_input():
    st.session_state.data_root = st.text_input("Data root")
    filenames = glob.glob(f'{st.session_state.data_root}/**/*.*', recursive=True)
    filenames.sort()
    filenames = [os.path.relpath(f,st.session_state.data_root) for f in filenames]
    return filenames


def file_header(max_ims=None):
    header_cols = st.columns((1,1.5))
    with header_cols[0]:
        filenames = folder_path_input()
        st.session_state.current_images = st.multiselect(
                        'Image list',
                        filenames,
                        max_selections=max_ims
                        )

        num_columns = 4

        for i in range(len(st.session_state.current_images)):
            if i % num_columns == 0:
                cols = st.columns(num_columns)
            cols[i%4].image(utils.full_path(st.session_state.current_images[i]))

        st.session_state.ref_im = st.selectbox('Select a reference image', st.session_state.current_images)
    return header_cols

def display_ref_im(header_cols, interactable='rectangle'):
    if st.session_state.ref_im:
        downscale_factor = 8
        orig_im = Image.open(utils.full_path(st.session_state.ref_im))
        im_w, im_h = orig_im.size
        res_w = int(im_w / downscale_factor)
        res_h = int(im_h / downscale_factor)
        ref_im = orig_im.resize((res_w, res_h))
        draw = ImageDraw.Draw(ref_im)
        if st.session_state["coordinates"]:
            coords = utils.get_rectangle_coords(st.session_state["coordinates"])
            draw.rectangle(coords, fill=None, outline="red", width=2)

        with header_cols[1]:
            if interactable == 'rectangle':
                value = streamlit_image_coordinates(ref_im,
                                                    key='rectangle',
                                                    click_and_drag=True)
        if value is not None:
            point1 = value["x1"], value["y1"]
            point2 = value["x2"], value["y2"]

            if (
                point1[0] != point2[0]
                and point1[1] != point2[1]
                and st.session_state["coordinates"] != (point1, point2)
            ):
                st.session_state["coordinates"] = (point1, point2)
                st.rerun()
