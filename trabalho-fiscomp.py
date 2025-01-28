import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from scipy import integrate



# Constante gravitacional
G = 6.67430 * 10**(-11) # m^3/(kg*s^2)

# Massas
mSol   = 1.9884 * 10**30 # kg
mTerra = 5.9723 * 10**24 # kg
mLua   = 7.349  * 10**22 # kg
mNave= 8000 #kg

# Distâncias (média)
rSolTerra = 1.4960 * 10**11 # m
rTerraLua = 3.850  * 10**8  # m

# Velocidades (média)
vTerra = 29780 # m/s (Trajetória em torno do sol)
vLua   = 1022  # m/s (Trajetório em torno da terra)

m1=mNave
m2=mTerra

def f(t,r):
    #índice 1 é da Nave
    #índice 2 é da Terra
    r1 = r[0:3] 
    r2 = r[3:6]
    v1 = r[6:9]
    v2 = r[9:12]
    r12 = np.linalg.norm(r1 - r2)
    eqr = G*np.array([
        (m2/r12**3)*(r2-r1),
        (m1/r12**3)*(r1-r2)
        ])
    return np.concatenate([r[6:12], eqr.flatten()])

rOrbit = 4.2164 * 10**7 # m (distância a partir do centro da Terra)
vOrbit = 1000 # m/s

# Nave
r10 = np.array([0,rOrbit, 0])
v10 = np.array([vOrbit, 0, 0])

# Terra
r20 = np.array([0, 0, 0])
v20 = np.array([0, 0, 0])

r0 = np.concatenate([r10, r20, v10, v20])

ti = 0
tf = 60*60*24*0.85 # segundos
solution = integrate.solve_ivp(f, [ti, tf], r0, method = 'RK45', t_eval = np.linspace(ti,tf,100001), rtol = 1e-9, atol = 1e-12)

fig = plt.figure(figsize=(10,10))
ax  = fig.add_subplot(1,1,1)
ax.set_aspect(1)
ax.set_xlim(-2e7,2e7)
ax.set_ylim(-2e7,5e7)
plt.gca().set_xlabel('x da Nave em relação à Terra', labelpad=20)
plt.ylabel('y da Nave em relação à Terra')

# Substituindo o plot por scatter
scat_nave = ax.scatter(solution.y[0][0], solution.y[1][0], color='blue', s=10)  # Nave
scat_terra = ax.scatter(solution.y[2][0], solution.y[3][0], color='red', s=100)  # Terra


def update(frame):
    # Atualiza a posição da nave e da Terra a cada frame
    x_nave = solution.y[0][frame]
    y_nave = solution.y[1][frame]
    x_terra = solution.y[2][frame]
    y_terra = solution.y[3][frame]
    
    # Atualiza a posição da nave e da Terra
    scat_nave.set_offsets([x_nave, y_nave])
    scat_terra.set_offsets([x_terra, y_terra])
    
    return scat_nave, scat_terra


ani = animation.FuncAnimation(fig=fig, func=update, frames=range(0, len(solution.t), 100), interval=30)

plt.show()
print('Fim da sim')