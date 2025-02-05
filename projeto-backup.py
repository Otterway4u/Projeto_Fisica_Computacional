import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from scipy.integrate import solve_ivp
from matplotlib.widgets import Button  # Importação do botão

# Constante gravitacional
G = 6.67430e-11  # m^3/(kg*s^2)

# Massas
mTerra = 5.9723e24  # kg
mLua   = 7.349e22   # kg
mNave  = 8000       # kg

# Distâncias (média)
rTerraLua = 3.850e8  # m

# Velocidades (média)
vLua = 1022  # m/s

# Estado do thrust (inicialmente desligado)
# 0 -> Sem thrust, 1 -> Thrust positivo, -1 -> Thrust negativo
thrust_sign = 0

def f(t, r):
    """
    r: array de 18 elementos:
        r[0:3]   -> posição (x, y, z) da Nave
        r[3:6]   -> posição (x, y, z) da Terra
        r[6:9]   -> posição (x, y, z) da Lua
        r[9:12]  -> velocidade (vx, vy, vz) da Nave
        r[12:15] -> velocidade (vx, vy, vz) da Terra
        r[15:18] -> velocidade (vx, vy, vz) da Lua
    """
    global thrust_sign

    # Extração das posições e velocidades
    r_nave   = r[0:3]
    r_terra  = r[3:6]
    r_lua    = r[6:9]
    v_nave   = r[9:12]
    v_terra  = r[12:15]
    v_lua    = r[15:18]

    # Cálculo das distâncias
    d_terra_nave = np.linalg.norm(r_nave - r_terra)
    d_lua_nave   = np.linalg.norm(r_nave - r_lua)
    d_terra_lua  = np.linalg.norm(r_terra - r_lua)

    # Acelerações gravitacionais
    acel_nave = G * ((mTerra * (r_terra - r_nave) / d_terra_nave**3) +
                     (mLua   * (r_lua   - r_nave) / d_lua_nave**3))
    acel_terra = G * ((mNave  * (r_nave  - r_terra) / d_terra_nave**3) +
                      (mLua   * (r_lua   - r_terra) / d_terra_lua**3))
    acel_lua = G * ((mNave  * (r_nave  - r_lua)   / d_lua_nave**3) +
                    (mTerra * (r_terra - r_lua)   / d_terra_lua**3))

    # Aplicação do thrust, se ativado (para a nave)
    if thrust_sign != 0:
        thrust_const = 1e-3 * thrust_sign  # valor do thrust ajustado
        norm_v_nave = np.linalg.norm(v_nave)
        if norm_v_nave > 1e-10:
            direcao = v_nave / norm_v_nave
            acel_nave += thrust_const * direcao

    # Retorna as derivadas: velocidades e acelerações
    derivadas = np.concatenate([v_nave, v_terra, v_lua, acel_nave, acel_terra, acel_lua])
    return derivadas

# ----------------------------------------------------------------------------
# CONDIÇÕES INICIAIS
# ----------------------------------------------------------------------------
rOrbit = 4.1e8  # m (distância a partir do centro da Terra)
vOrbit = np.sqrt(G * mLua / (rOrbit - rTerraLua)) + vLua  # m/s

# Posições e velocidades iniciais
r_nave0  = np.array([rOrbit, 0, 0])
v_nave0  = np.array([0, vOrbit, 0])
r_terra0 = np.array([0, 0, 0])
v_terra0 = np.array([0, 0, 0])
r_lua0   = np.array([rTerraLua, 0, 0])
v_lua0   = np.array([0, vLua, 0])

# Vetor de estado inicial
r0 = np.concatenate([r_nave0, r_terra0, r_lua0, v_nave0, v_terra0, v_lua0])

# Intervalo e passo de simulação
ti = 0
dt = 1000  # s

# Listas para armazenar a trajetória histórica da nave
trajetoria_x = []
trajetoria_y = []

# ----------------------------------------------------------------------------
# CONFIGURAÇÃO DA FIGURA E INTERFACE
# ----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10,10))
plt.subplots_adjust(bottom=0.3)  # Espaço para os botões

ax.set_aspect('equal')
ax.set_xlim(-5e8, 5e8)
ax.set_ylim(-5e8, 5e8)
ax.set_xlabel('x (m)', labelpad=10)
ax.set_ylabel('y (m)')
ax.set_title('Nave escapando gradualmente da gravidade da Lua')

# Criação dos scatter plots para os corpos
scat_nave  = ax.scatter([], [], color='blue', s=10, label="Nave")
scat_terra = ax.scatter([], [], color='green', s=100, label="Terra")
scat_lua   = ax.scatter([], [], color='black', s=50, label="Lua")

# Linha para a trajetória histórica (azul)
linha_trajetoria, = ax.plot([], [], 'b', alpha=0.5, lw=1, label="Histórico")

# Linha para a trajetória futura (vermelha)
linha_trajetoria_fut, = ax.plot([], [], 'r', alpha=0.7, lw=1, label="Projeção Futura")

# Texto para indicar o estado do thrust
thrust_text = ax.text(0.02, 0.95, 'Thrust: OFF', transform=ax.transAxes,
                      fontsize=12, fontweight='bold', color='red',
                      bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

# ----------------------------------------------------------------------------
# SIMULAÇÃO PASSO A PASSO
# ----------------------------------------------------------------------------
t_atual = ti
r_atual = r0.copy()

# Parâmetros para a projeção futura
num_steps_fut = 100       # Número de pontos da projeção
horizonte = 50 * dt       # Horizonte de tempo para a projeção

def update(frame):
    global r_atual, t_atual, thrust_sign

    # Integração para o próximo passo da simulação
    sol = solve_ivp(f, [t_atual, t_atual + dt], r_atual, method='RK45', rtol=1e-9, atol=1e-12)
    r_atual = sol.y[:, -1]
    t_atual += dt

    # Extração das posições (apenas x e y)
    x_nave, y_nave = r_atual[0], r_atual[1]
    x_terra, y_terra = r_atual[3], r_atual[4]
    x_lua, y_lua = r_atual[6], r_atual[7]

    # Atualiza os scatter plots
    scat_nave.set_offsets([x_nave, y_nave])
    scat_terra.set_offsets([x_terra, y_terra])
    scat_lua.set_offsets([x_lua, y_lua])

    # Atualiza a trajetória histórica da nave
    trajetoria_x.append(x_nave)
    trajetoria_y.append(y_nave)
    linha_trajetoria.set_data(trajetoria_x, trajetoria_y)

    # Atualiza a projeção futura: simula a partir do estado atual
    t_fut = np.linspace(t_atual, t_atual + horizonte, num_steps_fut)
    sol_fut = solve_ivp(f, [t_atual, t_atual + horizonte], r_atual,
                        t_eval=t_fut, method='RK45', rtol=1e-9, atol=1e-12)
    x_fut = sol_fut.y[0]
    y_fut = sol_fut.y[1]
    linha_trajetoria_fut.set_data(x_fut, y_fut)

    # Atualiza o texto de status do thrust
    if thrust_sign == 1:
        thrust_text.set_text('Thrust: +')
    elif thrust_sign == -1:
        thrust_text.set_text('Thrust: -')
    else:
        thrust_text.set_text('Thrust: OFF')

    return scat_nave, scat_terra, scat_lua, linha_trajetoria, linha_trajetoria_fut, thrust_text

# Cria a animação
ani = animation.FuncAnimation(
    fig, update, frames=range(100), interval=30, blit=True
)

# ----------------------------------------------------------------------------
# BOTÕES PARA ATIVAR/DESATIVAR O THRUST
# ----------------------------------------------------------------------------
ax_button_plus = plt.axes([0.2, 0.05, 0.15, 0.075])
ax_button_minus = plt.axes([0.4, 0.05, 0.15, 0.075])
ax_button_off = plt.axes([0.6, 0.05, 0.15, 0.075])

button_plus = Button(ax_button_plus, 'Thrust +')
button_minus = Button(ax_button_minus, 'Thrust -')
button_off = Button(ax_button_off, 'Thrust OFF')

def thrust_plus(event):
    global thrust_sign
    thrust_sign = 1
    print("Thrust positivo ativado!")

def thrust_minus(event):
    global thrust_sign
    thrust_sign = -1
    print("Thrust negativo ativado!")

def thrust_off(event):
    global thrust_sign
    thrust_sign = 0
    print("Thrust desligado!")

button_plus.on_clicked(thrust_plus)
button_minus.on_clicked(thrust_minus)
button_off.on_clicked(thrust_off)

plt.legend()
plt.show()