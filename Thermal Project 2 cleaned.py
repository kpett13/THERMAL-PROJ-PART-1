# -*- coding: utf-8 -*-
"""
Created on Sat Nov  3 12:11:13 2018

@author: kpett
"""
import matplotlib.pyplot as plt
import cantera as ct

def rev_irrev(hin, hout, sin, sout, Tin, Qin, Qout, mdotratio):
    To = 300
    irrev = mdotratio*(Qout+To*(sout-sin))
    rev = ((hin-hout)-To*(sin-sout))*mdotratio+Qin*(1-(To/Tin))*mdotratio
    return rev, irrev
  
def h_OutPump(n_pump, h_OutIs, h_In):
    h_OutAct = ((h_OutIs - h_In)/n_pump)+h_In
    return h_OutAct

def h_OutCompressor(n_compressor, h_OutIs, h_In):
    h_OutAct = ((h_OutIs - h_In)/n_compressor)+h_In
    return h_OutAct

def h_OutTurbine(n_turb, h_OutIs, h_In):
    h_OutAct = -(n_turb)*(h_In-h_OutIs)+h_In
    return h_OutAct

#Define Arrays
aPressureRatios = []    
aMDotRatios = []
aCycleEfficiency = []
aNetPower = []
aQin=[]
aQout =[]

#Define Fluid States
air5 = ct.Solution('air.cti')
air6 = ct.Solution('air.cti')
air7 = ct.Solution('air.cti')
air8 = ct.Solution('air.cti')
air9 = ct.Solution('air.cti')
water1 = ct.Water()
water2 = ct.Water()
water3 = ct.Water()
water4 = ct.Water()

#Define Efficiencies
n_compressor = 0.8
n_turbineAir = 0.85
e_HRSG = 0.86
n_pump = 0.9
n_turb_w = 0.9

for pr in range(3,21):
    
    "State 5 - AIR - Inlet to Compressor"
    P5 = 101325
    T5 = 300             
    air5.TP = T5, P5    
    s5 = air5.s
    h5 = air5.h
    
    "State 6 - AIR - Outlet of Compressor/Inlet to Combustion Chamber"
    P6 = 101325*pr
    s6_is = s5
    air6.SP = s6_is, P6
    h6_is= air6.h
    h6 = h_OutCompressor(n_compressor, h6_is, h5)
    air6.HP = h6,P6
    s6 = air6.s
    
    "State 7 - AIR - Outlet of Combustion Chamber/Inlet to Turbine"    
    P7 = P6
    T7 = 1400
    air7.TP = T7,P7
    s7 = air7.s
    h7 = air7.h
     
    "State 8 - AIR - Outlet of Turbine/Inlet to HRSG"
    P8 = P5
    s8_is = s7
    air8.SP = s8_is, P8
    h8_is = air8.h
    h8 = h_OutTurbine(n_turbineAir, h8_is, h7)
    air8.HP = h8,P8
    T8 = air8.T
    
    "State 9 - AIR - Outlet of HRSG"
    T9 = 450
    P9 = P8
    air9.TP = T9, P9
    h9 = air9.h
        
    "State 1 - WATER - Outlet of Condenser/Inlet to pump"
    P1 = 5*10**3
    water1.PX = P1, 0
    h1 = water1.h
    s1 = water1.s
    
    "State 2 - WATER - Outlet of Pump/Inlet to HRSG"
    P2 = 7*10**6
    s2_is = s1
    water2.SP = s2_is, P2
    h2_is = water2.h
    h2 = h_OutPump(n_pump, h2_is, h1)
    water2.HP = h2,P2
    T2 = water2.T
    
    "State 3 - WATER - Outlet of HRSG/Inlet to Turbine"
    P3 = P2
    T3Perf = T8
    water3.TP = T3Perf,P3
    h3Perf = water3.h
    h3 = e_HRSG*(h3Perf-h2)+h2     
    water3.HP = h3, P3               #h3-h2/h3perf-h2 = effectiveness
    mDotRatio = (h8-h9)/(h3-h2)
    s3 = water3.s
    water3()
    
    "State 4 -WATER - Outlet of Turbine/Inlet to Condenser"
    P4 = P1
    s4_is =  s3
    water4.SP = s4_is,P4
    h4_is = water4.h
    h4 = h_OutTurbine(n_turb_w, h4_is, h3)
    water4.HP = h4, P4
    water4()
    
    #Remaining Variables
    T1 = water1.T
    T3 = water3.T
    T4 = water4.T
    T6 = air6.T
    s2 = water2.s
    s3 = water3.s
    s4 = water4.s
    s6 = air6.s
    s8 = air8.s
    s9 = air9.s
    
    #Works and Heats
    Win56 = h5-h6
    Wout78 = h7-h8
    Win12 = mDotRatio*(h1-h2)
    Wout34 = mDotRatio*(h3-h4)
    Wtot = Win56+Wout78+Win12+Wout34
    
    Qin67 = h7-h6
    Qout41 = h1-h4
    n_tot = Wtot/Qin67
    
    #Reversible work and irreversibility
    Wrev56, i56 = rev_irrev(h5, h6, s5, s6, T5, 0, 0, 1)
    Wrev67, i67 = rev_irrev(h6, h7, s6, s7, T6, Qin67, 0, 1)
    Wrev78, i78 = rev_irrev(h7, h8, s7, s8, T7, 0, 0, 1)
    Wrev89, i89 = rev_irrev(h8, h9, s8, s9, T8, 0, (h8-h9), 1)
    
    Wrev12, i12 = rev_irrev(h1, h2, s1, s2, T1, 0, 0, mDotRatio)
    Wrev23, i23 = rev_irrev(h2, h3, s2, s3, T2, (h3-h2), 0, mDotRatio)
    Wrev34, i34 = rev_irrev(h3, h4, s3, s4, T3, 0, 0, mDotRatio)
    Wrev41, i41 = rev_irrev(h4, h1, s4, s1, T4, 0, -Qout41, mDotRatio)
    
    W12a = Wrev12-i12   #Right
    W34a = Wrev34-i34   #Right
    W41a = Wrev41-i41   #Right
    W56a = Wrev56-i56   #Right
    W78a = Wrev78-i78   #Right
    W89a = Wrev89-i89   #Right
    Wtota = W12a + W34a + W41a + W56a + W78a + W89a
    
    nII12 = Wrev12/Win12
    nII34 = Wout34/Wrev34
    nII56 = Wrev56/Win56
    nII78 = Wout78/Wrev78
    
    #Arrays for plots
    aPressureRatios.append(pr)    
    aMDotRatios.append(mDotRatio)
    aCycleEfficiency.append(n_tot)
    aNetPower.append(Wtot)
    aQin.append(Qin67)
    aQout.append(Qout41)
    
    
fig = plt.figure(figsize=(10, 10))
sub1 = fig.add_subplot(221) # instead of plt.subplot(2, 2, 1)
sub1.set_title('CoGen Cycle Efficiency') # non OOP: plt.title('The function f')
sub1.plot(aPressureRatios, aCycleEfficiency)
sub2 = fig.add_subplot(222)
sub2.set_title('Mass Flow Ratios')
sub2.plot(aPressureRatios, aMDotRatios)
sub3 = fig.add_subplot(223)
sub3.set_title('Net Output')
sub3.plot(aPressureRatios, aNetPower)
sub4 = fig.add_subplot(224)
sub4.set_title('Qin')
sub4.plot(aPressureRatios, aQin)
plt.tight_layout()
plt.show()
