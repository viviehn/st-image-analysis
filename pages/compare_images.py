import streamlit as st
import numpy as np
import os, glob
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates


st.set_page_config(layout='wide')
for state_key in ['coordinates', 'data_root', 'ref_im']:
    if state_key not in st.session_state:
        st.session_state[state_key] = None

def folder_path_input():
    st.session_state.data_root = st.text_input("Data root")
    filenames = glob.glob(f'{st.session_state.data_root}/**/*.*', recursive=True)
    filenames.sort()
    return filenames

def file_selector(folder_path='.'):
    selected_filename = st.selectbox('Select a file', filenames)
    return os.path.join(folder_path, selected_filename)

def full_path(fname):
    return fname
    #return f'{st.session_state.data_root}/{fname}'

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

@st.fragment
def show_crop(toggle_ims):
    im_idx = st.slider('im_idx', min_value=0, max_value=len(current_images)-1)
    st.image(toggle_ims[im_idx])

header_cols = st.columns((1,1.5))
with header_cols[0]:
    filenames = folder_path_input()
    current_images = st.multiselect(
                    'Image list',
                    filenames,
                    )

    num_columns = 4

    for i in range(len(current_images)):
        if i % num_columns == 0:
            cols = st.columns(num_columns)
        cols[i%4].image(full_path(current_images[i]))

    st.session_state.ref_im= st.selectbox('Select a reference image', current_images)
if st.session_state.ref_im:

    downscale_factor = 8
    orig_im = Image.open(full_path(st.session_state.ref_im))
    im_w, im_h = orig_im.size
    res_w = int(im_w / downscale_factor)
    res_h = int(im_h / downscale_factor)
    res_im = orig_im.resize((res_w, res_h))
    with res_im as img:
        draw = ImageDraw.Draw(img)

        if st.session_state["coordinates"]:
            coords = get_rectangle_coords(st.session_state["coordinates"])
            draw.rectangle(coords, fill=None, outline="red", width=2)


        coord_cols = st.columns((3,1))
        with header_cols[1]:
            value = streamlit_image_coordinates(img,
                                                key="rectangle",
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

        if st.session_state["coordinates"]:
            coords = get_rectangle_coords(st.session_state["coordinates"])
            new_image = img.crop(coords)
            new_image = new_image.resize(
                (int(new_image.width * 1.5), int(new_image.height * 1.5))
            )
            with header_cols[0]:
                st.image(new_image, use_container_width=True)

            toggle_ims = []
            res_coords = (coords[0]*downscale_factor,
                          coords[1]*downscale_factor,
                          coords[2]*downscale_factor,
                          coords[3]*downscale_factor,)
            for im_fname in current_images:
                downscale_factor = 8
                orig_im = Image.open(full_path(im_fname))
                im_w, im_h = orig_im.size
                res_w = int(im_w / downscale_factor)
                res_h = int(im_h / downscale_factor)
                #res_im = orig_im.resize((res_w, res_h))
                #new_full_image = np.array(res_im.crop(coords))
                new_full_image = np.array(orig_im.crop(res_coords))
                toggle_ims.append(new_full_image)
                print(im_fname)

            show_crop(toggle_ims)

    st.write(current_images)

