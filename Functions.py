import math
import pandas as pd

# Ppc
def Ppc_(gas_SG, corr):
	if corr == "Sutton":
		return 756.8 - 131.07*gas_SG - 3.6*(gas_SG**2)

	elif corr == "Misc Standing":
		return 677 + 15*gas_SG - 37.5*(gas_SG**2)

	elif corr == "Condensate Standing":
		return 706 - 51.7*gas_SG - 11.1*(gas_SG**2)

# Tpc
def Tpc_(gas_SG, corr):
	if corr == "Sutton":
		return 169.2 + 349.5*gas_SG - 74*(gas_SG**2)

	elif corr == "Misc Standing":
		return 168 + 325*gas_SG - 12.5*(gas_SG**2)

	elif corr == "Condensate Standing":
		return 187 + 330*gas_SG - 71.5*(gas_SG**2)

# Corrected
def Tpc_corr_(Tpc, H2S, CO2, N2):
	return Tpc - 80*CO2 + 130*H2S - 250*N2

def Ppc_corr_(Ppc, H2S, CO2, N2):
	return Ppc + 440*CO2 + 600*H2S - 170*N2

# Ppr
def Ppr_(P, Ppc):
	return P/Ppc

# Tpr
def Tpr_(T_rankine, Tpc):
	return T_rankine/Tpc

# Z-Dranchuk Abou Kassem
def DranchukAbouKassem_(Ppr, Tpr):
    A1 = 0.3265
    A2 = -1.07
    A3 = -0.5339
    A4 = 0.01569
    A5 = -0.05165
    A6 = 0.5475
    A7 = -0.7361
    A8 = 0.1844
    A9 = 0.1056
    A10 = 0.6134
    A11 = 0.7210

    R1 = A1 + A2/Tpr + A3/(Tpr**3) + A4/(Tpr**4) + A5/(Tpr**5)
    R2 = 0.27*Ppr/Tpr
    R3 = A6 + A7/Tpr + A8/(Tpr**2)
    R4 = A9*(A7/Tpr + A8/Tpr**2)
    R5 = A10/(Tpr**3)

    # estimate rho_r thru iteration, find root of f(rho_r), dapet rho_r, masuk ke rho_r = 0.27 Ppr/zTpr
    # define the Dranchuk Abuo Kassem function for root-finding
    # rho_r := x
    f = lambda y: 1 + R1*y - R2/y + R3*y**2 - R4*y**5 + (R5*y**2 * (1 + A11*y**2) * math.exp(-A11*y**2))
    y0 = R1 * R4
    # y0 = 5
    # find the root
    rho_r = newton_raphson(f, y0)

    Z = 0.27 * Ppr / (rho_r * Tpr)

    return Z

# newton raphson
def newton_raphson(f, x):
	tolerance = 1e-12
	'''
	xi+1 = xi - f(xi)/f'(xi)
	iterate until
	abs(f(xi)) < tolerance 
	'''
	f_prime = (f(x+1e-6)-f(x))/1e-6
	x = x - f(x)/f_prime

	if abs(f(x)) < tolerance:
		return x
	else:
		return newton_raphson(f,x)

# oil SG
def oil_SG_(oil_API):
	return 141.5/(oil_API + 131.5) 

# Ygs (Yg at 100 psig Separator Pressure)
def Ygs_(gas_SG, oil_API, Tsep, Psep): # Tsep: fahrenheit
    return gas_SG * (1 + (5.912 * (10 ** -5) * oil_API * (Tsep) * math.log10(Psep / 114.7))) 

# Rs
def Rso_(p, oil_API, T, psep, Ygs, Pb): # T: fahreneheit
    if oil_API <= 30:
        c1 = 0.362
        c2 = 1.0937
        c3 = 25.7240
    else:
        c1 = 0.0178
        c2 = 1.1870
        c3 = 23.9310

    if p <= Pb: # saturated
        return c1*Ygs*(p**c2)*math.exp(c3*(oil_API/(T+460))) # in scf/STB
    else: # undersaturater, P <= Pb
        return c1*Ygs*(Pb**c2)*math.exp(c3*(oil_API/(T+460)))

# Bo
def oilfvf_(oil_API, T_rankine, Rs, Ygs, P, Pb, Co):
    if P <= Pb: # saturated
        if oil_API <= 30:
            A1 = 4.677*10**(-4)
            A2 = 1.751*10**(-5)
            A3 = -1.811*10**(-8)

        else:
            A1 = 4.670*10**(-4)
            A2 = 1.100*10**(-5)
            A3 = 1.337*10**(-9)

        Bo = 1 + A1 * Rs + (T_rankine - 520) * (oil_API / Ygs) * (A2 + A3*Rs)
        return Bo

    else: # undersaturated, P > Pb
    	# Bob
        if oil_API <= 30:
            A1 = 4.677*10**(-4)
            A2 = 1.751*10**(-5)
            A3 = -1.811*10**(-8)

        else:
            A1 = 4.670*10**(-4)
            A2 = 1.100*10**(-5)
            A3 = 1.337*10**(-9)

        Bob = 1 + A1 * Rs + (T_rankine - 520) * (oil_API / Ygs) * (A2 + A3*Rs)
        Boo = Bob*math.exp(Co*(Pb - P))
        return Boo

def Bg_(Z,T_rankine,P, Psc):
    Bg = 0.0052*(Z*T_rankine)/P # in bbl/scf
    return Bg

# gas_density
def gas_density_(P,yg,Z,T): # T fahrenheit
    T=T+459.67
    return (28.967*P*yg)/(10.731*Z*T)

# gas viscosity
def gas_viscosity_(gas_density,T,Ma):
    T=T+459.67
    K=((9.4+0.02*Ma)*(T**1.5))/(209 + T + 19*Ma)
    X=3.5+986/T+0.01*Ma
    Y=2.4-0.2*X
    
    mu = 0.0001*K*math.exp(X*((gas_density/62.4)**Y))
    return mu

# Ma / Mg
def Mg_(gas_SG):
    return 28.967*gas_SG 

# oil_density
def oil_density_(oil_SG, gas_SG, Rs, T_rankine): # T rankine
    return (62.4 * oil_SG + 0.0136 * Rs * gas_SG) / (0.972 + 0.000147 * (Rs * ((gas_SG / oil_SG) ** 0.5) + 1.25 * (T_rankine-460))**1.175)

# Bw
def Bw_(p, t):
  c1 = -1.95301
  c2 = 1.72834
  c3 = 3.58922
  c4 = 2.25341
  d1 = -1.0001
  d2 = 1.33391
  d3 = 5.50654
  if t <= 260 and p <= 5000:
    deltavwp = c1*(10**(-9))*p*t - c2*(10**(-13))*(p**2)*t - c3*(10**(-t))*p - c4*(10**(-10))*(p**2)

    deltavwt = d1*(10**(-2)) + d2*(10**(-4))*t + d3*(10**(-t))*(t**2)

    return (1 + deltavwp)*(1 + deltavwt)
  else:
    return 0

# Rsw
def Rsw_(p, T, TDS): # McCain, T: fahrenheit, TDS: integer percent
    A = 8.15839 - 6.12265e-2*T + 1.91663e-4*(T**2) - 2.1654e-7*(T**3)
    B = 1.01021e-2 - 7.44241e-5*T + 3.05553e-7*(T**2) - 2.94883e-10*(T**3)
    C = (-9.02505 + 0.130237*T - 8.53425e-4*(T**2) + 2.34122e-6*(T**3) - 2.37049e-9*(T**4))*1e-7
    rsw_pure = (A + B*p + C*p**2) / 1000

    D = 10**(-0.0840655* TDS * (T**-0.285854))
    rsw = D * rsw_pure

    return rsw

# Cw
def Cw_(p, t):
    c1 = 3.8546-0.000134*p
    c2 = -0.01052+(4.77*10**(-7))*p
    c3 = 3.9267*10**(-5)-(8.8*10**(-10))*p
    return ((c1+c2*t+c3*t**2)*10**(-6))

# co
# 1. buat dibawah bubblepoint
# 2. buat diatas bubblepoint
def co(P, Pb, oil_API, T, gas_SG, Rso): # T fahrenheit
    if P <= Pb: # kondisi saturated
        A1 = -7.114
        A2 = -1.394
        A3 = 0.981
        A4 = 0.77
        A5 = 0.446

        cosat = math.exp(A1 + A2*math.log(P, math.e) + A3*math.log(T + 460, math.e) + A4 * math.log(oil_API, math.e) + A5 * math.log(gas_SG, math.e))

        return cosat

    else: # kondisi undersaturated, P > Pb
        return ((-1433 + 5*Rso + 17.2*(T) - 1180*gas_SG + 12.61*oil_API)/((10**5)*P))

# oil viscosity
def oil_viscosity_(T ,gas_SG, Rso, p, Pb, oil_API):
    # beggs robinson
    A = 10**(3.0324 - 0.02023*oil_API)
    mu_dead = 10 ** (A * T**-1.163) - 1

    # mu oil saturated
    a = 10.715*(Rso + 100)**(-0.515)
    b = 5.44*(Rso + 150)**(-0.338)

    mu_saturated = a*(mu_dead**b)

    # mu oil undersaturated
    n = -3.9*(10**(-5))*p - 5
    m = 2.6 * p**(1.187)*10**n

    muo = mu_saturated*(p/Pb)**m

    return muo

# brine_density
def brine_density_(TDS): # TDS int percent
    return 62.368+0.438603*TDS + 1.60074*(10**-3) *TDS**2

# brine viscosity McCain, S/TDS int percent, T fahrenheit
def brine_viscosity_(S,T):
    A = 109.574 + (-8.40564)*S + 0.313314* S**2 + 8.72213* 10**(-3) * S**3
    B = -1.12166 + 2.63951* 10**(-2) *S +(-6.79461* 10**(-4))* S**2 + (-5.47119* 10**(-5)* S**3 + 1.55586* 10**(-6) *S**4)
    return A*T**B

# gas compressibilty cg
def Cg_(Tpr,Ppr,z,Ppc):
    A1 = 0.3265
    A2 = -1.07
    A3 = -0.5339
    A4= 0.01569
    A5= -0.05165
    A6 = 0.5475
    A7 = -0.7361
    A8 = 0.1844
    A9 = 0.1056
    A10 = 0.6134
    A11 = 0.721
    
    Zc = 0.27
        
    C0 = (A7/Tpr) + (A8/Tpr**2)
    C1 = A1 + (A2/Tpr) + (A3/Tpr**3)+(A4/Tpr**4)+(A5/Tpr**5)
    C2 = A6 + C0
    C3 = A9 * C0
    
    rhoR = Zc*Ppr/(z*Tpr)
    
    zPrime = C1 + (2*C2*rhoR)-(5*C3*rhoR**4)+(2*A10*rhoR/Tpr**3)*(1+A11*rhoR**2 - (A11 * rhoR**2)**2)* math.exp(-A11 * rhoR**2)
    
    Cgpr = (1/Ppr)-(Zc/((z**2)*Tpr))*zPrime / (1 + (rhoR /z) * zPrime)
    
    return Cgpr/Ppc

def sat_condition_(P, Pb):
	if P > Pb:
		return 'Undersaturated'
	else:
		return 'Saturated'