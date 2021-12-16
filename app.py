import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from Functions import *

# Streamlit App Setup
st.set_page_config(layout="wide", page_title="PVT Calculator")
plt.style.use('seaborn')

# FUNCTIONS
# arguments (P, T, gas_SG, oil_API, Pb, Psep, Tsep, sat_condition, TDS, corr, Psc, H2S, CO2, N2)

def output(P, T, gas_SG, oil_API, Pb, Psep, Tsep, sat_condition, TDS, corr, Psc, H2S, CO2, N2):
	df = pd.DataFrame()
	df['Properties'] = ['P (psia)', 'Bo (RB/STB)', 'Rs (Mscf/STB)', 'Bg (RB/Mscf)', 'Bw (RB/STB)', 'Rsw (scf/STB)', 'Z (Vol/Vol)', 'Oil Density (lbm/cf)', 'Gas Density (lbm/cf)', 'Brine Density (lbm/cf)', 'Oil Viscosity (cp)', 'Gas Viscosity (cp)', 'Brine Viscosity (cp)', 'Co x 10^-5 (1/MMpsi)', 'Cg x 10^-5 (1/MMpsi)', 'Cw x 10^-5 (1/MMpsi)']

	# setup
	T_rankine = T + 460
	oil_SG = oil_SG_(oil_API)
	Ygs = Ygs_(gas_SG, oil_API, Tsep, Psep)
	Ma = Mg_(gas_SG)

	Ppc = Ppc_(gas_SG, corr)
	Tpc = Tpc_(gas_SG, corr)

	# corrected
	Ppc = Ppc_corr_(Ppc, H2S, CO2, N2)
	Tpc = Tpc_corr_(Tpc, H2S, CO2, N2)

	Ppr = Ppr_(P, Ppc)
	Tpr = Tpr_(T_rankine, Tpc)

	Z = DranchukAbouKassem_(Ppr, Tpr)

	# calculate
	Rs = Rso_(P, oil_API, T, Psep, Ygs, Pb)
	Co = co(P, Pb, oil_API, T, gas_SG, Rs)
	Bob = oilfvf_(oil_API, T_rankine, Rs, Ygs, P, Pb, Co)
	Bo = oilfvf_(oil_API, T_rankine, Rs, Ygs, P, Pb, Co)
	Bg = Bg_(Z,T_rankine,P, Psc)
	Bw = Bw_(P, T)
	Rsw = Rsw_(P, T, TDS)
	Conditions = sat_condition_(P, Pb)
	oil_density = oil_density_(oil_SG, gas_SG, Rs, T_rankine)
	gas_density = gas_density_(P,gas_SG,Z,T)
	brine_density = brine_density_(TDS)
	oil_viscosity = oil_viscosity_(T ,gas_SG, Rs, P, Pb, oil_API)
	gas_viscosity = gas_viscosity_(gas_density, T, Ma)
	brine_viscosity = brine_viscosity_(TDS, T)
	Co = co(P, Pb, oil_API, T, gas_SG, Rs)
	Cg = Cg_(Tpr,Ppr,Z,Ppc)
	Cw = Cw_(P, T)

	#konversi unit
	P = round(P, 1)
	Rs = Rs * 1e-3
	Bg = Bg * 1e3
	Cw = Cw * 1e5
	Co = Co * 1e5
	Cg = Cg * 1e5

	df['Values'] = [P, Bo, Rs, Bg, Bw, Rsw, Z, oil_density, gas_density, brine_density, oil_viscosity, gas_viscosity, brine_viscosity, Co, Cg, Cw]

	st.write(f'Condition: {Conditions}')
	st.dataframe(df)

def show_table(P, T, gas_SG, oil_API, Pb, Psep, Tsep, sat_condition, TDS, corr, Psc, H2S, CO2, N2):
	table = pd.DataFrame()
	# setup
	T_rankine = T + 460
	oil_SG = oil_SG_(oil_API)
	Ygs = Ygs_(gas_SG, oil_API, Tsep, Psep)
	Ma = Mg_(gas_SG)

	Ppc = Ppc_(gas_SG, corr)
	Tpc = Tpc_(gas_SG, corr)

	# corrected
	Ppc = Ppc_corr_(Ppc, H2S, CO2, N2)
	Tpc = Tpc_corr_(Tpc, H2S, CO2, N2)
	Tpr = Tpr_(T_rankine, Tpc)

	list_P = np.arange(150, 4600, 150)
	table = pd.DataFrame()

	Rs_list = list()
	Co_list = list()
	Bo_list = list()
	Bg_list = list()
	Bw_list = list()
	Rsw_list = list()
	Z_list = list()
	Conditions_list = list()
	oil_density_list = list()
	gas_density_list = list()
	brine_density_list = list()
	oil_viscosity_list = list()
	gas_viscosity_list = list()
	brine_viscosity_list = list()
	Cg_list = list()
	Cw_list = list()


	# buat list sendiri, append ke df
	for P in list_P:
	    # Rs
	    Rs = Rso_(P, oil_API, T, Psep, Ygs, Pb) 
	    Rs_list.append(Rs*1e-3)

	    #Co
	    Co = co(P, Pb, oil_API, T, gas_SG, Rs)
	    Co_list.append(Co*1e5)

	    # Bo
	    Bo = oilfvf_(oil_API, T_rankine, Rs, Ygs, P, Pb, Co)
	    Bo_list.append(Bo)

	    # Z
	    Ppr = Ppr_(P, Ppc)
	    Z = DranchukAbouKassem_(Ppr, Tpr)
	    Z_list.append(Z)

	    # Bg
	    Bg = Bg_(Z,T_rankine,P, Psc)
	    Bg_list.append(Bg*1e3)

	    # Bw   
	    Bw = Bw_(P, T)
	    Bw_list.append(Bw)

	    # Rsw
	    Rsw = Rsw_(P, T, TDS)
	    Rsw_list.append(Rsw)

	    # conditions
	    Conditions = sat_condition_(P, Pb)
	    Conditions_list.append(Conditions)

	    # oil density
	    oil_density = oil_density_(oil_SG, gas_SG, Rs, T_rankine)
	    oil_density_list.append(oil_density)

	    # gas_density
	    gas_density = gas_density_(P,gas_SG,Z,T)
	    gas_density_list.append(gas_density)

	    # brine density
	    brine_density = brine_density_(TDS)
	    brine_density_list.append(brine_density)

	    # oil viscosity
	    oil_viscosity = oil_viscosity_(T ,gas_SG, Rs, P, Pb, oil_API)
	    oil_viscosity_list.append(oil_viscosity)

	    # gas viscosity
	    Ma = Mg_(gas_SG)
	    gas_viscosity = gas_viscosity_(gas_density, T, Ma)
	    gas_viscosity_list.append(gas_viscosity)

	    # brine viscosity
	    brine_viscosity = brine_viscosity_(TDS, T)
	    brine_viscosity_list.append(brine_viscosity)

	    # Cg
	    Cg = Cg_(Tpr,Ppr,Z,Ppc)
	    Cg_list.append(Cg*1e5)

	    # Cw
	    Cw = Cw_(P, T)
	    Cw_list.append(Cw*1e5)

	# append ke table
	table['P'] = list_P
	table['Bo'] = Bo_list
	table['Rs'] = Rs_list
	table['Bg'] = Bg_list
	table['Bw'] = Bw_list
	table['Rsw'] = Rsw_list
	table['Conditions'] = Conditions_list
	table['Z'] = Z_list
	table['Oil Density'] = oil_density_list
	table['Gas Density'] = gas_density_list
	table['Brine Density'] = brine_density_list
	table['Oil Viscosity'] = oil_viscosity_list
	table['Gas Viscosity'] = gas_viscosity_list
	table['Brine Viscosity'] = brine_viscosity_list
	table['Co'] = Co_list
	table['Cg'] = Cg_list
	table['Cw'] = Cw_list

	return table



# STREAMLIT UI
st.title('PVT Calculator')
st.markdown('''**Tugas Besar Fluida Reservoir oleh:**  
1. Bagus Aulia Ahmad Fahrezi - 12220108  
2. Dimas Naufal Al Ghifari - 12220114  
3. Haris Permana - 12220075  
4. Muhammad Naufal Aurora - 12220081  
5. Rizqy Wahyu Bachtiar - 12220087''')

col1, col2, col3 = st.columns(3)

with col1:
	st.subheader('General Data')
	T = st.number_input('Reservoir Temperature (°F)')
	P_initial = st.number_input('Initial Reservoir Pressure (psia)')
	Psc = st.number_input('Standard Pressure, Psc (psia)')
	gas_SG = st.number_input('Gas Gravity (Air = 1.0)')


with col2:
	st.subheader('Separator Data')
	Psep = st.number_input('Separator Pressure, Psep (psia)')
	Tsep = st.number_input('Separator Temperature, Tsep (psia)')

	st.subheader('Brine Data')
	sat_condition = st.selectbox('Saturation Condition', 
		('Gas Saturated Brine', 'Gas Free Brine'))
	TDS = st.number_input('Total Dissolved Solids, TDS (% Weight)')

with col3:
	st.subheader('Correlation Method')
	corr = st.selectbox('Ppc/Tpc Correlation',
		('Sutton', 'Misc Standing', 'Condensate Standing'))

	st.subheader('Impurities')
	H2S = st.number_input('H2S (% mole)')
	CO2 = st.number_input('CO2 (% mole)')
	N2 = st.number_input('N2 (% mole)')

col1_1, col2_1 = st.columns(2)

with col1_1:
	st.subheader('Oil Data')
	oil_API = st.number_input('Oil API (°API)')
	Pb = st.number_input('Bubblepoint Pressure, Pb (psia)')
	
with col2_1:
	st.subheader('Pressure of Interest')
	P = st.number_input('Pressure, P (psia)')

st.subheader('PVT Output')
output(P, T, gas_SG, oil_API, Pb, Psep, Tsep, sat_condition, TDS, corr, Psc, H2S, CO2, N2)

st.subheader('Property Table')
table = show_table(P, T, gas_SG, oil_API, Pb, Psep, Tsep, sat_condition, TDS, corr, Psc, H2S, CO2, N2)
st.dataframe(table)

st.subheader('Graphs')
colx, coly = st.columns(2)

with colx:
	x_axis = st.selectbox('Select X Axis',
		('P', 'Bo', 'Rs', 'Bg', 'Bw', 'Rsw', 'Z', 'Oil Density', 'Gas Density', 'Brine Density', 'Oil Viscosity', 'Gas Viscosity', 'Brine Viscosity', 'Co', 'Cg', 'Cw'))

with coly:
	y_axis = st.selectbox('Select Y Axis',
		('P', 'Bo', 'Rs', 'Bg', 'Bw', 'Rsw', 'Z', 'Oil Density', 'Gas Density', 'Brine Density', 'Oil Viscosity', 'Gas Viscosity', 'Brine Viscosity', 'Co', 'Cg', 'Cw'))

# show graph
x = table[x_axis]
y = table[y_axis]
fig, ax = plt.subplots()
ax.plot(x,y)
plt.xlabel(x_axis)
plt.ylabel(y_axis)
plt.title(f'Grafik {x_axis} ~ {y_axis} ')
st.pyplot(fig)