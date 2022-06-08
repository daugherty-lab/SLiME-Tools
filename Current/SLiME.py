#!/usr/bin/env python3

import altair as alt
import argparse
import os
import pandas as pd
import streamlit as st

# Currently a hack to pass args into streamlit
parser = argparse.ArgumentParser(prog='concat-hitsum.py', conflict_handler='resolve', description='This app visualizes SLiME data')
parser.add_argument('-clvdata', type=str, required=True, help='=> path/to/clvdata.csv')
parser.add_argument('-flatdata', type=str, required=True, help='=> path/to/flatdata.csv')

# If the args aren't there, abort
try:
    args = parser.parse_args()
except SystemExit as e:
    # This exception will be raised if --help or invalid command line arguments
    # are used. Currently streamlit prevents the program from exiting normally
    # so we have to do a hard exit.
    os._exit(e.code)

# Loading the data
@st.cache
def get_flatdata():
    return(pd.read_csv(os.path.join(os.getcwd(), args.clvdata)))
@st.cache
def get_clv_predictions():
    return(pd.read_csv(os.path.join(os.getcwd(), args.flatdata)))

# set slider option
def update_slider():
    st.session_state.slider = (st.session_state.lower, st.session_state.upper)
    print(st.session_state.slider)

def update_numin():
    st.session_state.lower, st.session_state.upper = st.session_state.slider
    print(st.session_state.slider)

# set up altair evo sig scatter plot
def get_scatterchart(data, x_ax: str, y_ax: str, x_span: tuple[int], y_span: tuple[int]):
    s_chart = alt.Chart(data, title = 'OWM Primate Evolutionary Fingerprinting'
        ).mark_circle(size = 30,opacity = 0.8
        ).encode(x = alt.X(x_ax, title = x_ax,
                scale = alt.Scale(domain = [x_span[0], x_span[1]])),
                y=alt.Y(y_ax, title=y_ax, 
                scale = alt.Scale(domain=[y_span[0], y_span[1]])),
                tooltip=['sequenceID', 'Gene_Sym','PC1','Omega', 'calc_AF']
        ).configure_axis(labelFontSize=14,
                        titleFontSize=14
        )
    return(s_chart)

# set up altair bar plot for clv pvals
def get_barchart(data, seqID: str, x_ax: str, y_ax1: str, y_ax2: str, x_span_upper: int, desc = "unknown"):
    bchart = alt.Chart(data, title = f"Detected cleavage sites in {seqID} ({desc}, {x_span_upper} AAs)"
        ).mark_bar(opacity = 0.6
        ).encode(x = alt.X(x_ax, title = 'P4 start (AA pos)',
                scale = alt.Scale(domain = [1, x_span_upper+100])),
                y=alt.Y(y_ax1, title='motif p-val'),
                color=alt.condition(alt.datum.human_hit == 'Yes',
                alt.value('orange'),
                alt.value('blue')
                ),
                tooltip=['start', 'count', 'Num_Unique','concat_sites', 'org_pvals', 'Non_hits', 'best_pval', 'human_site', 'pval_hg38', 'FUBAR_PSRs']
        )
    
    # best hit data
    bchart2 = alt.Chart(data
        ).mark_bar(opacity = 1
        ).encode(x = alt.X(x_ax,
                scale = alt.Scale(domain = [1, x_span_upper+100])),
                y = y_ax2,
                tooltip=['start', 'count', 'Num_Unique','concat_sites', 'org_pvals', 'Non_hits', 'best_pval', 'human_site', 'pval_hg38', 'FUBAR_PSRs']
        )
    
    # line drawn to indicate end of human transcript
    overlay = pd.DataFrame({'x': [x_span_upper]})
    vline = alt.Chart(overlay).mark_rule(color='red', strokeWidth=1).encode(x='x:Q')


    layered = alt.layer(bchart2, bchart, vline
        ).configure_view(stroke='transparent'
        ).configure_axis(labelFontSize=14,
                        titleFontSize=14
        )
    return(layered)

# configuration of the page
st.set_page_config(layout="wide")

# load dataframes
df_flat = get_flatdata()
df_clv = get_clv_predictions()

st.title('SLiME vizualisation tool')
st.markdown("""
This app performs simple visualization from evolutionary and cleavage prediction datasets!
""")

# set drop-down filter options
axes_list = ['<Select>', 'Omega vs PC1', 'PC1 vs Omega', 'log_calc_AF vs PC1', 'log_calc_AF vs Omega']
ID_list = ['<Select>', 'sequenceID', 'Gene_Sym']

ifn_list = ['<Select>', 'Ifn_u2', 'Ifn_u5', 'Ifn_d2', 'Ifn_d5']
hu_status = ['<Select>', 'Yes', 'No']
evo_list = ['<Select>', 'PC1', 'Omega']

# Add filter widgets
query_list = []
with st.sidebar:
    st.header("Filter Cleavage Data")

    # Set scatter axes and ID to map, otherwise unsynced
    by_axes = st.selectbox(label = "Select Evolutionary Fingerprinting axes", 
                            options = axes_list)
    by_type = st.selectbox(label = "Map cleavage hits by (required to sync)", 
                            options = ID_list)
    st.markdown("***") # Add line space in sidebar

    # input gene or transcript ID of interest
    st.subheader("By Target ID")
    target_ID = st.text_input(label = 'Input sequenceID or Gene_Sym', 
                                value= '')
    st.markdown("***") # Add line space in sidebar

    # Simple dropdown filters
    st.subheader("By orthogonal data")
    by_ifn = st.selectbox(label = "By Interferome", 
                            options = ifn_list)
    by_human = st.selectbox(label = "By Human Hit", 
                            options = hu_status)
    by_evo = st.selectbox(label = "By Evolutionary Signatures", 
                            options = evo_list)

    # Expand out evo option for range filters
    if by_evo != '<Select>':
        st.subheader(f"By {by_evo}")
        val_lo = st.number_input(label = f'{by_evo} Lowerbound:', 
                            value = min(df_flat[f'{by_evo}']), 
                            step = 0.01,
                            key = 'lower', 
                            on_change = update_slider)

        val_hi = st.number_input(label= f'{by_evo} Upperbound:', 
                                value = max(df_flat[f'{by_evo}']), 
                                step = 0.01,
                                key = 'upper', 
                                on_change = update_slider)

        values = st.slider(label = f'Select a range of {by_evo} values',
                            min_value = min(df_flat[f'{by_evo}']), 
                            max_value = max(df_flat[f'{by_evo}']),
                            value = (val_lo, val_hi),
                            key = 'slider',
                            on_change= update_numin
                            )
    st.markdown("***") # Add line space in sidebar

# Set query if filtering by orthogonal data
if by_human != '<Select>':
    query_list.append(f"human_hit=='{by_human}'")
if by_ifn != '<Select>':
    query_list.append(f"{by_ifn}=='YES'")
if by_evo != '<Select>':
    evo_min, evo_max = values
    query_list.append(f"{by_evo}>={evo_min} and {by_evo}<={evo_max}")
query = " and ".join(query_list)

# Perform query filtering based on sidebar inputs
if target_ID:
    df_clv_filtered = df_clv.query(f"sequenceID=='{target_ID}' or Gene_Sym=='{target_ID}'"
                                ).sort_values('AA_seqlength', ascending=False)
    for uniqID in df_clv_filtered['sequenceID'].unique():
        bar_xlim = df_clv_filtered.query(f"sequenceID=='{uniqID}'")['AA_seqlength'].max()
        tscript_num = df_clv_filtered.query(f"sequenceID=='{uniqID}'")['description'].iloc[0].split(',')[-2]
        barchart = get_barchart(df_clv_filtered, uniqID, 'start', 'pval_hg38', 'best_pval', bar_xlim, tscript_num)
        st.altair_chart(barchart, use_container_width = True)
elif query:
    df_clv_filtered = df_clv.query(query)
else:
    df_clv_filtered = df_clv
st.write(df_clv_filtered)

# set up Altair plot for selected hits
if by_type != '<Select>':
    mask_flat = df_flat[by_type].isin(df_clv_filtered[by_type])
    df_flat_filtered = df_flat[mask_flat]
else:
    df_flat_filtered = df_flat

if by_axes != '<Select>':
    X_axis = by_axes.split(' vs ')[1]
    Y_axis = by_axes.split(' vs ')[0]
else:
    X_axis = 'PC1'
    Y_axis = 'Omega'

scatter_xlims = (df_flat[X_axis].min(skipna=True), df_flat[X_axis].max(skipna=True))
scatter_ylims = (df_flat[Y_axis].min(skipna=True), df_flat[Y_axis].max(skipna=True))
scatterchart = get_scatterchart(df_flat_filtered, X_axis, Y_axis, scatter_xlims, scatter_ylims)

st.altair_chart(scatterchart, use_container_width = True)