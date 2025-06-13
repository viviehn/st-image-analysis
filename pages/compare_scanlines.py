import streamlit as st
import numpy as np
import os, glob, datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates
from skimage import color


st.set_page_config(layout='wide')
for state_key in ['data_root', 'ref_im', 'current_ims', 'plot', 'cur_idx', 'use_downsized', 'all_rows']:
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

@st.fragment
def show_plot(data, init_row):
    fig = go.Figure()
    num_ims = data.shape[0]
    im_w = data.shape[2]
    im_h = data.shape[1]

    for im_idx in range(num_ims):
        im = data[im_idx]
        if st.session_state.all_rows:
            for row in list(range(0, im_h)):
                fig.add_trace(
                        go.Line(
                            visible=False,
                            name=f'{im_idx}-{row}',
                            x=list(range(0, im_w)),
                            y=im[row,:]
                            ))
        else:
            fig.add_trace(
                    go.Line(
                        visible=True,
                        name=f'{im_idx}-{init_row}',
                        x=list(range(0, im_w)),
                        y=im[init_row,:]
                        ))

    if st.session_state.all_rows:
        for n in range(num_ims):
            fig.data[init_row+(im_h*n)].visible=True

    if st.session_state.all_rows:
        steps = []
        for i in range(int(len(fig.data)/num_ims)):
            step = dict(
                    method="update",
                    args=[
                        {"visible": [False]*len(fig.data)},
                        {"title": 'Slider switched to step: ' + str(i)}],
                    )
            for n in range(num_ims):
                step['args'][0]['visible'][i+(im_h*n)] = True
            steps.append(step)

        sliders = [dict(
            active=init_row,
            currentvalue={"prefix": "Row: "},
            pad={"t": 50},
            steps=steps
            )]

        fig.update_layout(
                sliders=sliders
        )
        st.session_state['plot'] = fig

    st.plotly_chart(fig)


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
    st.session_state.use_downsized = st.pills(
        "downsize",
        options=[1,2,4,8],
        default=8,
        selection_mode="single",
    )
    st.session_state.all_rows = st.checkbox('pre-compute all rows', value=False)


if st.session_state.ref_im:
    # compute dictionary of plots
    downscale_factor = st.session_state.use_downsized
    orig_im = Image.open(full_path(st.session_state.ref_im))
    im_w, im_h = orig_im.size
    display_downscale_factor = 8
    res_w = int(im_w / display_downscale_factor)
    res_h = int(im_h / display_downscale_factor)
    res_im = orig_im.resize((res_w, res_h))
    res_im_clean = np.array(res_im)
    with res_im as img:

        draw = ImageDraw.Draw(img)
        row_val = 0
        if st.session_state["cur_idx"]:
            row_val = st.session_state['cur_idx']
            draw.line(((0,row_val), (res_w,row_val)), fill="red", width=2)
        with header_cols[1]:
            value = streamlit_image_coordinates(img,
                                            )
        if value is not None:
            st.session_state['cur_idx'] = value['y']
            st.rerun()

        toggle_ims = []

        for im_fname in current_images:
            orig_im = Image.open(full_path(im_fname))
            im_w, im_h = orig_im.size
            res_w = int(im_w / downscale_factor)
            res_h = int(im_h / downscale_factor)
            res_im = orig_im.resize((res_w, res_h))
            im_lab = np.array(color.rgb2lab(res_im))[...,0]
            toggle_ims.append(im_lab)

        data = np.stack(toggle_ims)
        init_row = row_val * int(display_downscale_factor / downscale_factor)
        show_plot(data, init_row)
