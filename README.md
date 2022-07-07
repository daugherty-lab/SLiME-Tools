# SLiME-Tools
Short Linear Motif Evolution Tools

# In progress:
1. Automate testing for all related bash and python code.

# Two approaches to use this tool:
1. [Google Colaboratory](https://colab.research.google.com/drive/1q6UIrzrNZEaI6Wyy7jOMt6M8WyKJ0YJv?usp=sharing) (Instructions included within this resource)
2. Cromwell->WDL pipeline for user-friendly control (Discontinued support)

After obtaining the .csv output from SLiME.ipynb, you can visualize the .csv in SLiMED (SLiME Dashboard). See below:

# Stage: Visualize using clv data dashboard
## SLiMED.py
### Pre-reqs:
1. [miniconda](https://docs.conda.io/en/latest/miniconda.html#macos-installers)
* Download the pkg corresponding to your system architecture (e.g. intel or ARM64 for macOS)
* Make sure you meet the system requirements (e.g. 64-bit macOS must be updated to 10.13+)
2. Streamlit
* ```conda install -c conda-forge streamlit```
3. Altair
* ```conda install -c conda-forge altair```
4. Pandas
* ```conda install -c anaconda pandas```
5. SLiMED.py app
If you have wget (Linux, macOS with Homebrew):
* ```wget https://raw.githubusercontent.com/daugherty-lab/SLiME-Tools/master/Current/SLiMED.py -O [/path/to/desired/local_directory/SLiMED.py]```
OR
If you have curl (macOS):
* ```curl https://raw.githubusercontent.com/daugherty-lab/SLiME-Tools/master/Current/SLiMED.py > [/path/to/desired/local_directory/SLiMED.py]```

### Usage: 
1. Visualize clvdata (annotated-concat-hitsum-out.csv) using Streamlit, Altair on localhost
* ```streamlit run propredict.py -- -clvdata [path/to/clvdata.csv] -flatdata [path/to/flatdata.csv]```