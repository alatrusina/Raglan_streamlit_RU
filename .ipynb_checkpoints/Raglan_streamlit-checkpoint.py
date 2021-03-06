#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure



import numpy as np

def stitch_density(L_measured, N_st_measured):# plotnosti veazania petli
    if L_measured !=0:
        st_density = N_st_measured/L_measured
    else:
        st_density = 0
    return np.mean(st_density)

def row_density(H_measured, R_measured):# plotnosti veazania ruady
    if H_measured != 0:
        r_density = R_measured/H_measured
    else:
        r_density = 0
    return np.mean(r_density)

def cm_to_stitches(st_density, L):
    '''
    st_density = [st/cm]
    L = desired lenghth in cm
    '''
    return st_density*L
    
def cm_to_rows(r_density, H):
    '''
    r_density = [row/cm]
    H = desired height in cm
    '''
    return r_density*H

def r_st_to_cm(density, N):
    return N/density

def reglan_start(st_density, row_density, L_neck = 56, N_regl = 3):
    '''
    L_neck = 56 cm, corcumference of the corall
    N_regl = 4 , number of stitches per reglan line
    
    '''
    N_neck = np.floor(cm_to_stitches(st_density, L_neck))
    y = (N_neck - 4*N_regl)/8
    N_sleeve = np.floor(y)
    
    N_turns = np.floor(N_sleeve/2) # this can be adjusted, gives the N_rostok, but has to be less than N_sleeve_int/2
    R_rostok = 2*N_turns # the height of rostok in Rows, for checking... the Rostok in cm can be an input to check
    L_rostok = r_st_to_cm(r_density,R_rostok)
    print("So far the number of turns is ", N_turns)
    print("and Rostok is ", R_rostok,'rows and ', L_rostok,' cm')
    
    
    N_front_corr = np.floor(3*y) + N_turns
    N_back_corr = np.floor(3*y) - N_turns
    
    # cecking if lost anything
    
    N_neck_added = N_back_corr + N_front_corr + 2*N_sleeve + 4*N_regl
    if N_neck_added!=N_neck:
        print("You've lost some titches while rounging off")
        print('After adding up, you N_neck = ', N_neck_added, " but you started with N_neck=", N_neck)
        print('Adding the differnce to the front, N_diff = ', N_neck-N_neck_added)
        N_front_corr += N_neck-N_neck_added
    else:
        print("all is good no lost stitches!")
        
    print('Final output: N_sleeve=', N_sleeve, ' N_front=', N_front_corr, 'N_back = ', N_back_corr)
    return N_sleeve, N_front_corr, N_back_corr, R_rostok, L_rostok, N_turns

def increase_rate(N_bottom, N_top, N_podrez, R_regl, diag_rate_specified = -1):
    '''Calculates the decrease rate for e.g. front, back, sleeve.
    input args: N_bottom - the desired number of stithes at the bottom of the reglan line
                N_top - the number of stitches at the top of the  reglan line
                N_podrez - the length of "podrez" , e.g. 50% of "prolojenie ruki u podmyshki"
                H_regl - the height of reglan line (vertical)
    '''
    Width_regl =(N_bottom - N_top - N_podrez)/2 
    print("Width_regl =", Width_regl, " R_regl = ", R_regl)
    diag_rate_calculated = Width_regl/R_regl
    
    if (diag_rate_specified!=-1):
        if diag_rate_specified != diag_rate_calculated:
            print("SPecified and calcualted rates of increases/Decreases differ!")
            print("Calcualted rate=", diag_rate_calculated)
            print("Specified rate=", diag_rate_specified)
    print("Calcualted rate=", diag_rate_calculated)
            
    return diag_rate_calculated 

def calc_podrez(st_density, L_arm_interface, coeff=0.3):   
    L_podrez = L_arm_interface*coeff# the coefficient is highest the higher is the projma. I.e. 0.5 v podmyshkae, 0.3-0.2 if oversize, i.e. 10 cm below podmushki
    N_podrez = cm_to_rows(st_density, L_podrez)
    print('N_podrez=', N_podrez, 'stitches')
    return N_podrez

def front_increase_rate(Circ_breast, Circ_additional, N_podrez, R_regl, N_neck_front):
    Width_at_end_reglan_line = (Circ_breast + Circ_additional)/2
    N_at_end_reglan_line = cm_to_stitches(st_density, Width_at_end_reglan_line)

    f_increase_rate = increase_rate(N_bottom = N_at_end_reglan_line, N_top = N_neck_front, N_podrez=N_podrez, R_regl = R_regl)
    return f_increase_rate



def sleeve_increase_rate(st_density, Circ_arm, Circ_arm_addl, N_neck_sleeve):
    Width_at_end_reglan_line_sl = (Circ_arm + Circ_arm_addl)
    N_at_end_reglan_line_sl = cm_to_rows(st_density,Width_at_end_reglan_line_sl)
    #print("N_width_sleeve = ", N_at_end_reglan_line_sl)
    sl_increase_rate = increase_rate(N_bottom = N_at_end_reglan_line_sl, N_top = N_neck_sleeve, N_podrez=N_podrez, R_regl = R_regl)
    return sl_increase_rate

def inc_rate_to_width(inv_diag_rate_specified, R_regl, N_top, N_podrez, st_density):
    rate = 1/inv_diag_rate_specified
    X_regl = rate*R_regl #X at the reglan end, in stitches, i.e. horisontal increase form diagonal
    total_N_at_regl_end = 2*X_regl + N_top + N_podrez
    total_L_at_Regl_end = r_st_to_cm(st_density,total_N_at_regl_end)
    return total_N_at_regl_end, total_L_at_Regl_end



st.set_page_config(layout = 'wide', initial_sidebar_state="collapsed")
header  = st.container()
inputs_knit_density =  st.container()
inputs_reglan_start  = st.container()
inputs_podrez = st.container()
inputs_front  = st.container()
inputs_sleeve  = st.container()



with header:
    st.markdown('## ?????????????? ?????????????? (8 ????????????)')

with inputs_knit_density:
    #st.markdown('## Stitch density')
    with st.expander("1. ?????????????????? ???????????? ?? ??????????"):
        #in_col, out_col = st.columns(2)
        cols = st.columns(5)
        L_measured = cols[0].number_input('???????????? ?????????????? [????]', value=10)
        N_measured = cols[0].number_input('??????-???? ????????????', value = 11.5)
        st_density = stitch_density(L_measured, N_measured)
        st_density_opt = cols[0].number_input('?????????????????? ???????????? [????/????] ',value=st_density)
        H_measured = cols[1].number_input('???????????? ?????????????? [????]', value = 10)
        R_measured = cols[1].number_input('??????-???? ?????????? [????]', value = 15)
        r_density = row_density(H_measured, R_measured)
        r_density_opt = cols[1].number_input('?????????????????? ?????????? [????/????]',value=r_density)
        st.markdown('?????????????????????? [????/????] = **' + '{asp:.3g}'.format(asp=st_density_opt/(r_density_opt + 1e-5))+'**')

#------------------------- RAGLAN START ------------------------------

with inputs_reglan_start:
    with st.expander("2. ???????????? ??????????????"):
        cols = st.columns(5)
        L_neck = cols[0].number_input('?????????? ?????????????????? [????]', value = 56)
        N_regl = cols[1].selectbox('??????-???? ???????????? ?? ????????. ??????????', (1, 2, 3, 4, 5, 6), index = 2)

       # N_regl = cols[1].number_input('# of stitches per regl. line')
        N_neck_sleeve, N_neck_front, N_neck_back, R_rostok, L_rostok, N_turns = 0,0,0, 0, 0, 0
       # if cols[3].button('Calc # of stitches for front, back and sleeve'):
        N_neck_sleeve, N_neck_front, N_neck_back, R_rostok, L_rostok, N_turns = reglan_start(st_density, r_density, L_neck, N_regl)

        output_relgan_start = cols[0].container()
        output_relgan_start.markdown("??????-???? ???????????? ?????????? = **" + str(N_neck_front) + '**')
        output_relgan_start.markdown("??????-???? ???????????? ?????????? =**" + str(N_neck_back)+ '**')
        output_relgan_start.markdown("??????-???? ???????????? ?????????? = **" + str(N_neck_sleeve)+ '**')
        
        output_rostok = cols[1].container()
        output_rostok.markdown('?????????? ?????????????????? (?? ????????????) = **' + str(N_turns) + '**')
        output_rostok.markdown('???????????? ?? ?????????? = **' + str(R_rostok) + '**')
        output_rostok.markdown('???????????? ?? ???? = **' + str(L_rostok) + '**')

#------------------------- Podrez ------------------------------
with inputs_podrez:
    with st.expander("3. ???????????? ?? ???????????? ??????????????"):
        cols = st.columns(5)
        L_arm_interface = cols[0].number_input('???????????????????? ???????? [????]', value = 15)
        
        Coeff_podrez = cols[0].selectbox('??????????. ??????????????', (0.1, 0.2, 0.3, 0.4, 0.5), index = 1)

        N_podrez = calc_podrez(st_density, L_arm_interface, coeff = Coeff_podrez)
        N_podrez_opt = cols[0].number_input('???????????? [????]', value = N_podrez)
        H_regl = cols[1].number_input('???????????? ?????????????? [????]', value = 28)
        R_regl = cm_to_rows(r_density, H_regl)
        cols[1].markdown('???????????? ?????????????? **{r_regl:.2g}** ??????????'.format(r_regl=R_regl))

#------------------------- FRONT ------------------------------
with inputs_front:
    with st.expander("4. ?????????????? ????????????????- ?????????? (??????????)"):
        cols = st.columns(5)
        #L_arm_interface = cols[0].number_input('Prileganie ruki, cm', value = 15)
        
        Circ_breast = cols[0].number_input('?????????? ?????????? [????]',value = 104) #obhavt grudi
        Circ_additional = cols[0].number_input('?????????????? ?????????????????? [????]', value=2*15) # svoboda oblegania vokrug
 
        f_rate = front_increase_rate(Circ_breast, Circ_additional, N_podrez, R_regl, N_neck_front)
        str = '???????????? ???????????? (??????????) = {f_width:.3g} [????]'.format(f_width= (Circ_breast + Circ_additional)/2)
        cols[0].markdown(str)
               
        str = ' ??????????: ???????????????? ?? ???????????? {dec_rate:.2f} ????????'.format(dec_rate = 1/f_rate)
        cols[1].markdown('#### '+ str )
        
        f_rate_opt = cols[1].number_input('?????????????? ???????????????? ', value = 1/f_rate)
        Circ_updated_N, Circ_updated_L = inc_rate_to_width(f_rate_opt, R_regl, N_top = N_neck_front, N_podrez = N_podrez_opt, st_density=st_density_opt)
        
        str = '?? ??. ???????????????? {rate_opt:.3g} ???????????? ???????????? (??????????) = {circ:.3g} [????]'.format(rate_opt = f_rate_opt, circ_st = Circ_updated_N, circ = Circ_updated_L)
        cols[1].markdown(str)
        
#------------------------- SLEEVE ------------------------------
with inputs_sleeve:
    with st.expander("5. ?????????????? ???????????????? - ??????????"):
        cols = st.columns(5)
        Circ_arm = cols[0].number_input('?????????? ????????', value = 34) #cm
        Circ_arm_addl = cols[0].number_input('?????????????? ?????????????????? [????] ', value = 4) #cm 4#0*6 #cm -- svoboda prileganija rukava
        #here remeber that 1/rate ~2.666 is best to come from 2 2 4
        str = '???????????? ???????????? = {s_width:.3g} [????]'.format(s_width= Circ_arm + Circ_arm_addl)
        cols[0].markdown(str)
        
        
        sl_rate = sleeve_increase_rate(st_density, Circ_arm, Circ_arm_addl, N_neck_sleeve)
        
        str = '??????????: ???????????????? ?? ???????????? {dec_rate:.2f} ????????'.format(dec_rate = 1/sl_rate)#'????????????' + 
        cols[1].markdown('#### '+ str)
        sl_rate_opt = cols[1].number_input('?????????????? ???????????????? (???????????? 2.66 ???????? 2-2-4)', value = 1/sl_rate)
        Circ_updated_N_sl, Circ_updated_L_sl = inc_rate_to_width(sl_rate_opt, R_regl, N_top = N_neck_sleeve, N_podrez = N_podrez_opt, st_density=st_density_opt)
        
        str = '?? ??. ???????????????? {sl_rate_opt:.3g} ???????????? {circ:.3g} cm '.format(sl_rate_opt = sl_rate_opt, circ_st = Circ_updated_N_sl, circ = Circ_updated_L_sl)
        cols[1].markdown(str)
        
# -------------------- DRAW -----------------------------        
        
L_top_front = r_st_to_cm(st_density_opt, N_neck_front)
print('\n L_top_front', L_top_front, 'W_breast = ', Circ_updated_L)
L_podrez = r_st_to_cm(st_density_opt, N_podrez_opt)

L_regl = (Circ_updated_L - L_podrez -L_top_front)/2


cols = st.columns(2)

cols[0].markdown('## <h3 align="center"> ?????????? </h3>', unsafe_allow_html=True)
cols[1].markdown('## <h3 align="center"> ?????????? </h3>', unsafe_allow_html=True)
H = cols[0].number_input('?????????? ???????????? (??????????) ', value = 70)
H_sl = cols[1].number_input('?????????? ????????????', value = 70)


reflect = np.array([-1,1])

N = 8

# ---- Front
points = np.zeros((2,N))

points[:,0] = [- L_top_front/2,0] #A
points[:,1] = points[:,0] + [-L_regl,-H_regl] #H
points[:,2] = points[:,1] + [-L_podrez/2,0] #G
points[:,3] = points[:,2] + [0,-(H-H_regl)] #F
points[:,4] = reflect*points[:,3] #E = -F
points[:,5] = reflect*points[:,2] # D = -G
points[:,6] = reflect*points[:,1] # C = -H
points[:,7] = reflect*points[:,0] # B = -A



# ---- Sleeve
points_sl = np.zeros((2,N))

L_top_sl = r_st_to_cm(st_density_opt, N_neck_sleeve)
L_regl_sl = 0.5*(Circ_updated_L_sl - L_podrez - L_top_sl)
points_sl[:,0] = [- L_top_sl/2,0] #A
points_sl[:,1] = points_sl[:,0] + [-L_regl_sl,-H_regl] #H
points_sl[:,2] = points_sl[:,1] + [-L_podrez/2, 0] #G
points_sl[:,3] = points_sl[:,2] + [0,-(H_sl-H_regl)] #F
points_sl[:,4] = reflect*points_sl[:,3] #E = -F
points_sl[:,5] = reflect*points_sl[:,2] # D = -G
points_sl[:,6] = reflect*points_sl[:,1] # C = -H
points_sl[:,7] = reflect*points_sl[:,0] # B = -A

#

import plotly.express as px
import plotly.graph_objects as go

W_half = 1.1*Circ_updated_L/2
xlimits = [-W_half, W_half]

max_y = np.max([H,H_sl])

ylimits = [-max_y*1.1, max_y*0.1]


fig = go.Figure(go.Scatter(x=points[0,:], y=points[1,:], fill="toself"), 
                layout_yaxis_range = ylimits, 
                layout_xaxis_range = xlimits)
fig_sl = go.Figure(go.Scatter(x=points_sl[0,:], y=points_sl[1,:], fill="toself"), 
                   layout_yaxis_range = ylimits, 
                   layout_xaxis_range = xlimits)

fig.update_yaxes(
    scaleanchor = "x",
    scaleratio = 1,
  )
fig_sl.update_yaxes(
    scaleanchor = "x",
    scaleratio = 1,
  )

cols[0].write(fig)

cols[1].write(fig_sl)