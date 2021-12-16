import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import json
plt.style.use('seaborn')

st.title('Production Data Viewer')

# load data
@st.cache
def load_data():
	df = pd.read_csv('produksi_minyak_mentah.csv')
	df = df[df.columns[:3]]
	return df

# load json data
@st.cache
def load_json():
	file_json = open('./kode_negara_lengkap.json')
	json_data = json.load(file_json)
	return json_data

df = load_data()
json_data = load_json()


# buat list kode negara utk filter kode negara yg avalilable
@st.cache
def dict_nama_negara_generator():
	list_kode_negara = df.kode_negara.unique()
	dict_nama_negara = dict()
	for negara in json_data:
	    if negara['alpha-3'] in list_kode_negara:
	        dict_nama_negara.update({negara['alpha-3']: negara['name']})
	return dict_nama_negara

dict_nama_negara = dict_nama_negara_generator()

# setup function untuk mengconvert kode negara
def convert_kode_negara(kode):
    try:
        return dict_nama_negara[kode]
    except:
        return kode

#========
# no 1) line chart produksi per negara (produksi vs tahun)
negara_options = df.kode_negara.unique()
st.subheader('Production by country')
negara = st.selectbox(label="Negara", options=negara_options, key='negara_1')

line_chart_data = df[df['kode_negara'] == negara][['tahun', 'produksi']]
line_chart_x = df[df['kode_negara'] == negara].tahun
line_chart_y = df[df['kode_negara'] == negara].produksi
fig_1, ax1 = plt.subplots()
ax1.plot(line_chart_x, line_chart_y)
ax1.set_title(f'Produksi {convert_kode_negara(negara)}')
st.pyplot(fig_1)


#===========
# no 2) bar chart n negara terbesar pada tahun tertentu
st.subheader('N Negara Produksi Terbesar')
number_2 = st.slider(label='Banyak negara', min_value=1, max_value=142, key='number_2') # buat slider streamlit
tahun = st.slider(label='Tahun', min_value=1970, max_value=2015, key='tahun_2')
# algo
max_prod = df[df.tahun == tahun].produksi.sort_values(ascending=False)[:number_2].values
fig_2, ax2 = plt.subplots()
for prod in max_prod:
	# find kode negara
	kode_negara_prod_max = df[(df.tahun == tahun) & (df.produksi == prod)].kode_negara.item() # dah dalam string
	# convert ke nama negara
	nama_negara_prod_max = convert_kode_negara(kode_negara_prod_max)
	# buat plot
	ax2.barh(nama_negara_prod_max, prod)
    
plt.title(f'{number_2} Negara dengan Produksi Terbesar Tahun {tahun}')
st.pyplot(fig_2)


#========
# no 3) barh chart n negara dengan produksi kumulatif terbesar
st.subheader('N Negara Produksi Kumulatif Terbesar')
number_3 = st.slider(label='Banyak negara', min_value=1, max_value=142, key='number_3')

xs = df.groupby(['kode_negara']).sum().sort_values(by='produksi', ascending=False).produksi[:number_3].index
ys = df.groupby(['kode_negara']).sum().sort_values(by='produksi', ascending=False).produksi[:number_3]
fig3, ax3 = plt.subplots()

for x, y in zip(xs, ys):
	x = convert_kode_negara(x)
	ax3.barh(x, y)

plt.title(f'{number_3} Negara dengan Produksi Kumulatif Terbesar')
st.pyplot(fig3)


#==========
# no 4)
def search_in_json(kode):
    for negara in json_data:
        if negara['alpha-3'] == kode:
            return negara

tahun4 = st.slider(label='Tahun', min_value=1970, max_value=2015, key='tahun4')

# tunjukkin yang terbesar
kode_negara_terbesar = df[df.tahun == tahun4].sort_values(by='produksi', ascending=False).kode_negara[:1].values[0]
kode_negara_terkecil = df[(df.tahun == tahun4) & (df.produksi != 0)].sort_values(by='produksi').kode_negara[:1].values[0]
kode_negara_nol = df[(df.tahun == tahun4) & (df.produksi == 0)].kode_negara.values

# ambil data json lewt kode
# terbesar
negara = search_in_json(kode_negara_terbesar)
st.write('**Produksi Terbesar**')
if negara == None: # kode negaranya gaada di data json
	st.write(f'Data {kode_negara_terbesar} tidak ada di JSON')
else:
	st.write(negara['name'],
	    negara['alpha-3'],
	    negara['region'],
	    negara['sub-region'],
	    df[(df.kode_negara == kode_negara_terbesar) & (df.tahun == tahun4)].produksi.values[0])

# terkecil
negara = search_in_json(kode_negara_terkecil)
st.write('**Produksi Terkecil**')
if negara == None: # kode negaranya gaada di data json
    st.write(f'Data {kode_negara_terkecil} tidak ada di JSON')
else:
    st.write(negara['name'],
	    negara['alpha-3'],
	    negara['region'],
	    negara['sub-region'],
	    df[(df.kode_negara == kode_negara_terkecil) & (df.tahun == tahun4)].produksi.values[0])
    
# yg 0
st.write('**Produksi 0**')
for kode in kode_negara_nol:
    negara = search_in_json(kode)
    if negara == None: # kode negaranya gaada di data json
        st.write(f'Data {kode} tidak ada di JSON')
    else:
        st.write(negara['name'],
            negara['alpha-3'],
            negara['region'],
            negara['sub-region'],
            df[(df.kode_negara == kode) & (df.tahun == tahun4)].produksi.values[0])