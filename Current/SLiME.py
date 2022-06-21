#!/usr/bin/env python3

import altair as alt
import argparse
import numpy as np
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
# IMPORTANT: Cache the conversion to prevent computation on every rerun
@st.cache
def get_flatdata():
    return(pd.read_csv(os.path.join(os.getcwd(), args.flatdata)))
@st.cache
def get_clv_predictions():
    return(pd.read_csv(os.path.join(os.getcwd(), args.clvdata)))
@st.cache
def convert_df_to_csv(df):
  return df.to_csv().encode('utf-8')

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
        ).encode(
            x = alt.X(x_ax, 
                scale = alt.Scale(domain = [x_span[0], x_span[1]])),
            y = alt.Y(y_ax, 
                scale = alt.Scale(domain = [y_span[0], y_span[1]])),
            tooltip = ['sequenceID', 'Gene_Sym','PC1','Omega', 'calc_AF']
        ).configure_axis(
            labelFontSize = 14,
            titleFontSize = 16
        ).configure_title(fontSize = 18)
    return(s_chart)

# set up altair bar plot for clv pvals
def get_barchart(data, seqID: str, x_ax: str, y_ax: str, y_ax2: str, x_hi: int, y_hi: int, desc = "transcript"):
    bchart = alt.Chart(data, 
        title = f"Detected cleavage sites in {seqID} ({desc}, {x_hi}AAs)"
        ).mark_bar(opacity = 0.8
        ).encode(
            x = alt.X(x_ax, 
                title = 'P4 start (AA pos)',
                scale = alt.Scale(domain = [1, x_hi+50])),
            y=alt.Y(y_ax, 
                title='motif -log(p-val)',
                scale = alt.Scale(domain = [0, y_hi])),
                color = alt.Color('human_hit',
                    scale = alt.Scale(
                        domain = sorted(data.human_hit.tolist(), reverse = True),
                        range = ['orange','violet'])),
            tooltip = ['start', 'count', 'Num_Unique','concat_sites', 'org_pvals', 'Non_hits', 'best_pval', 'human_site', 'pval_hg38', 'FUBAR_PSRs']
        )

    s_chart = alt.Chart(data,
        ).mark_circle(opacity = 0.9
        ).encode(
            x = alt.X(x_ax, 
                scale = alt.Scale(domain = [1, x_hi+50])),
            y = alt.Y(y_ax2,
                scale = alt.Scale(domain = [0, y_hi])),
            tooltip = ['start', 'count', 'Num_Unique','concat_sites', 'org_pvals', 'Non_hits', 'best_pval', 'human_site', 'pval_hg38', 'FUBAR_PSRs']
        )
    
    # line drawn to indicate end of human transcript
    overlay = pd.DataFrame({'x': [0, x_hi]})
    vline = alt.Chart(overlay).mark_rule(color = 'red', strokeWidth = 1).encode(x = 'x:Q')


    layered = alt.layer(vline, bchart, s_chart
        ).configure_view(stroke = 'transparent'
        ).configure_axis(labelFontSize = 14,
            titleFontSize = 16
        ).configure_title(fontSize = 18)
    return(layered)

# Page configs
st.set_page_config(layout="wide")
# CSS to inject contained in a string
hide_table_row_index = """
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            """
# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)

# load dataframes
df_flat = get_flatdata()
df_clv = get_clv_predictions()

st.title('SLiME vizualisation tool')
st.markdown("""
This app performs simple visualization from evolutionary and cleavage prediction datasets!
If you want to clear options, refresh the page.
***
""")

# set drop-down filter options
axes_list = ['<Select>', 'Omega vs PC1', 'PC1 vs Omega', 'log_calc_AF vs PC1', 'log_calc_AF vs Omega']
ID_list = ['<Select>', 'sequenceID', 'Gene_Sym']

ifn_list = ['<Select>', 'Ifn_u2', 'Ifn_u5', 'Ifn_d2', 'Ifn_d5']
hu_status = ['<Select>', 'Yes', 'No']
evo_list = ['<Select>', 'PC1', 'Omega']

# Add filter widgets
clv_query_list = []
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
    by_human_search = st.selectbox(label = "Human Hit Status:", 
                            options = hu_status)
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
    clv_query_list.append(f"human_hit=='{by_human}'")
if by_ifn != '<Select>':
    clv_query_list.append(f"{by_ifn}=='YES'")
if by_evo != '<Select>':
    evo_min, evo_max = values
    clv_query_list.append(f"{by_evo}>={evo_min} and {by_evo}<={evo_max}")

clv_query = " and ".join(clv_query_list)

# Perform clv query filtering based on sidebar inputs
if target_ID:
    ini_search = [f"sequenceID=='{target_ID}' or Gene_Sym=='{target_ID}'"]
    if by_human_search != '<Select>':
        ini_search.append(f"human_hit=='{by_human_search}'")
    search_query = " and ".join(ini_search)
    df_clv_filtered = df_clv.query(search_query).sort_values('AA_seqlength', ascending=False)
    # Add log10 data
    df_clv_filtered['log_best_pval'] = np.log10(df_clv_filtered['best_pval']) * -1
    df_clv_filtered['log_pval_hg38'] = np.log10(df_clv_filtered['pval_hg38']) * -1
    # Set col and vals for ORFeome data
    # ORFeome_headers = list(df_clv_filtered[['Resource_Plate', 'Resource_Position', 'hORF_Length']].columns)
    # ORFeome_data = list(df_clv_filtered[['Resource_Plate', 'Resource_Position', 'hORF_Length']].values.flatten())
    # for col_i, col in enumerate(st.columns(3)):
    #     col.metric(label = ORFeome_headers[col_i], value = ORFeome_data[col_i])
    st.table(df_clv_filtered[['Resource_Plate', 'Resource_Position', 'hORF_Length']].iloc[0:1])
    st.table(df_clv_filtered[['Ifn_u2', 'Ifn_u5', 'Ifn_d2', 'Ifn_d5']].iloc[0:1])
    for uniqID in df_clv_filtered['sequenceID'].unique():
        uniqID_df = df_clv_filtered.query(f"sequenceID=='{uniqID}'")
        bar_xlim = uniqID_df['AA_seqlength'].max()
        bar_ylim = uniqID_df['log_best_pval'].max()
        desc_parse = uniqID_df['description'].iloc[0]
        if 'transcript' in desc_parse:
            tscript_num = desc_parse.split(',')[-2]
        else:
            tscript_num = "transcript"
        barchart = get_barchart(uniqID_df, uniqID, 'start', 'log_best_pval', 'log_pval_hg38', bar_xlim, bar_ylim, tscript_num)
        st.altair_chart(barchart, use_container_width = True)
elif clv_query:
    df_clv_filtered = df_clv.query(clv_query)
else:
    df_clv_filtered = df_clv

st.dataframe(df_clv_filtered.iloc[ :, :17])

st.download_button(
  label="Download as CSV",
  data=convert_df_to_csv(df_clv_filtered.iloc[ :, :17]),
  file_name='clv_data.csv',
  mime='text/csv',
)
st.markdown("***")

# Perform flat query filtering based on sidebars
if by_evo != '<Select>' and by_type != '<Select>':
    mask_flat = df_flat[by_type].isin(df_clv_filtered[by_type])
    df_flat_filtered = df_flat[mask_flat].query(f"{by_evo}>={evo_min} and {by_evo}<={evo_max}")
    st.write(f"Matching clv data by {by_type}")
elif by_evo == '<Select>' and by_type != '<Select>':
    mask_flat = df_flat[by_type].isin(df_clv_filtered[by_type])
    df_flat_filtered = df_flat[mask_flat]
elif by_evo != '<Select>' and by_type == '<Select>':
    df_flat_filtered = df_flat.query(f"{by_evo}>={evo_min} and {by_evo}<={evo_max}")
else:
    df_flat_filtered = df_flat

# set up Altair plot for selected hits
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

# Counters for clv data
clv_counter = len(df_clv_filtered.index)
clv_by_transcript_counter = len(df_clv_filtered['sequenceID'].unique())
clv_by_gene_counter = len(df_clv_filtered['Gene_Sym'].unique())
st.markdown("""***
### Summary of counts
""")
st.write(f"Clv hits (Total): {clv_counter} \n ")
st.write(f"Clv hits by (Aligned Transcripts, Genes): ({clv_by_transcript_counter}, {clv_by_gene_counter})")

# # Counters for flat data
flat_counter = len(df_flat_filtered.index)
flat_by_gene_counter = len(df_flat_filtered['Gene_Sym'].unique())
st.write(f"Flat (Aligned Transcripts, Genes): ({flat_counter}, {flat_by_gene_counter})")

#Filter summary
st.write(f"Filters used: {clv_query}")

