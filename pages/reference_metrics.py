import layout, utils
import streamlit as st
import numpy as np
import os, glob
import matplotlib.pyplot as plt
from matplotlib import gridspec
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import mean_squared_error
from skimage import color

metrics_list = ['ssim', 'rmse']
plt.rcParams["font.size"] = 8

st.set_page_config(layout='wide')
for state_key in ['coordinates', 'data_root', 'ref_im', 'other_im', 'current_images', 'current_metrics']:
    if state_key not in st.session_state:
        st.session_state[state_key] = None

header_cols = layout.file_header(max_ims=2)

layout.display_ref_im(header_cols)

with header_cols[0]:
    st.session_state.current_metrics = st.multiselect(
                    'Metrics',
                    metrics_list,
                    )

if len(st.session_state.current_images) == 2:
    if st.session_state.current_images[0] == st.session_state.ref_im:
        st.session_state.other_im = st.session_state.current_images[1]
    elif st.session_state.current_images[1] == st.session_state.ref_im:
        st.session_state.other_im = st.session_state.current_images[0]

@st.fragment
def compute_ssim(im1, im2):
    ssim_avg, ssim_grad, ssim_full = ssim(im1, im2,
                                          data_range=1.,
                                          gradient=True, full=True,
                                          )
    fig, ax1 = plt.subplots()
    cax = ax1.imshow(ssim_full, vmin=-1, vmax=1, cmap='jet')
    ax1.set_title(f'SSIM={ssim_avg:.4f}')

    cbar = fig.colorbar(cax,
                        ticks=[-1, 0, 1],
                        fraction=0.046, pad=0.04
                        )
    labels = cbar.ax.get_yticklabels()
    labels[0].set_verticalalignment('top')
    labels[-1].set_verticalalignment('bottom')

    st.pyplot(fig)

@st.fragment
def compute_rmse(im1, im2):
    diff = im1 - im2
    diff = np.sqrt(np.square(diff))
    rmse = diff.mean()
    fig, ax = plt.subplots()
    cax = ax.imshow(diff, vmin=0, vmax=1, cmap='jet')
    ax.set_title(f'RMSE={rmse:4f}')

    cbar = fig.colorbar(cax,
                        ticks=[0, 1],
                        )
    labels = cbar.ax.get_yticklabels()
    labels[0].set_verticalalignment('top')
    labels[-1].set_verticalalignment('bottom')
    st.pyplot(fig)

@st.fragment
def compute_mse(im1, im2):
    diff = im1 - im2
    mse = diff.mean()
    fig, ax = plt.subplots()
    cax = ax.imshow(diff, vmin=0, vmax=1, cmap='jet')
    ax.set_title(f'MSE={mse:4f}')

    cbar = fig.colorbar(cax,
                        ticks=[0, 1],
                        )
    labels = cbar.ax.get_yticklabels()
    labels[0].set_verticalalignment('top')
    labels[-1].set_verticalalignment('bottom')
    st.pyplot(fig)

@st.fragment
def compute_psnr(im1, im2):

    print('todo')

    '''
    cax = ax.imshow(psnr, vmin=0, vmax=1, cmap='jet')
    ax.set_title(f'MSE={mse:4f}')

    cbar = fig.colorbar(cax,
                        ticks=[0, 1],
                        )
    labels = cbar.ax.get_yticklabels()
    labels[0].set_verticalalignment('top')
    labels[-1].set_verticalalignment('bottom')
    st.pyplot(fig)
    '''


if st.session_state["coordinates"]:
    downscale_factor = 8
    coords = utils.get_rectangle_coords(st.session_state["coordinates"])
    res_coords = (coords[0]*downscale_factor,
                  coords[1]*downscale_factor,
                  coords[2]*downscale_factor,
                  coords[3]*downscale_factor,)
    ref_im_crop_l = color.rgb2lab(np.array(Image.open(utils.full_path(st.session_state.ref_im)).crop(res_coords)))[...,0]/100.
    other_im_crop_l = color.rgb2lab(np.array(Image.open(utils.full_path(st.session_state.other_im)).crop(res_coords)))[...,0]/100.
    '''
    ref_im_crop_l = np.array(Image.open(utils.full_path(st.session_state.ref_im)).crop(res_coords))[...]/255.
    other_im_crop_l = np.array(Image.open(utils.full_path(st.session_state.other_im)).crop(res_coords))[...]/255.
    '''

    if 'ssim' in st.session_state.current_metrics:
        compute_ssim(ref_im_crop_l, other_im_crop_l)

    if 'rmse' in st.session_state.current_metrics:
        compute_rmse(ref_im_crop_l, other_im_crop_l)

    if 'mse' in st.session_state.current_metrics:
        compute_mse(ref_im_crop_l, other_im_crop_l)

    if 'psnr' in st.session_state.current_metrics:
        compute_psnr(ref_im_crop_l, other_im_crop_l)

