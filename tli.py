import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from scipy.integrate import solve_ivp
from matplotlib.widgets import Button

# Constantes e parâmetros
G = 6.67430e-11         # m^3/(kg*s^2)
mTerra = 5.9723e24      # kg
mu = G * mTerra         # parâmetro gravitacional da Terra

# Parâmetros da transferência de Hohmann para a Lua:
r1 = 7000e3             # órbita inicial (7.000 km do centro da Terra)
r2 = 384400e3           # órbita alvo (distância média da Lua)

v_circ1 = np.sqrt(mu / r1)  # velocidade circular na órbita inicial
v_circ2 = np.sqrt(mu / r2)  # velocidade circular "na órbita" alvo (em torno da Terra)

# Cálculo dos deltas-v para a transferência:
delta_v1 = v_circ1 * (np.sqrt(2 * r2 / (r1 + r2)) - 1)
delta_v2 = v_circ2 * (1 - np.sqrt(2 * r1 / (r1 + r2)))

# Variáveis globais de controle da transferência:
burn_stage = 0  # 0: sem queima, 1: primeira queima realizada, 2: transferência completa
state = np.array([r1, 0, 0, v_circ1])  # Estado inicial: [x, y, vx, vy]
t_current = 0
dt_base = 10  # passo de tempo (s)

# Listas para armazenar a trajetória da nave
traj_x = []
traj_y = []

# ----------------------------------------------------------------------------
# Configuração da figura e elementos gráficos
# ----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 10))
plt.subplots_adjust(bottom=0.3)

# Ajusta os limites para abranger desde a Terra até além da órbita lunar
lim = 1.2 * r2
ax.set_aspect('equal')
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)
ax.set_xlabel('x (m)')
ax.set_ylabel('y (m)')
ax.set_title('Transferência de Hohmann para a Lua')

# Desenha a Terra (supondo raio de 6371 km)
earth = plt.Circle((0, 0), 6371e3, color='blue', alpha=0.5)
ax.add_artist(earth)

# Desenha a órbita alvo (a órbita lunar em torno da Terra) – círculo vermelho tracejado
theta = np.linspace(0, 2*np.pi, 200)
orbit_lunar_x = r2 * np.cos(theta)
orbit_lunar_y = r2 * np.sin(theta)
ax.plot(orbit_lunar_x, orbit_lunar_y, 'r--', label='Órbita Lunar')

# Elementos gráficos para a nave e sua trajetória
scat_ship = ax.scatter([], [], color='green', s=20, label='Nave')
line_traj, = ax.plot([], [], 'k-', lw=1, label='Trajetória')

# Texto para indicar o estágio da transferência
burn_text = ax.text(0.02, 0.95, 'Burn Stage: 0', transform=ax.transAxes,
                    fontsize=12, color='black')

# ----------------------------------------------------------------------------
# Equações do movimento: corpo pontual sob a gravidade da Terra
# ----------------------------------------------------------------------------
def dynamics(t, y):
    x, y_pos, vx, vy = y
    r = np.sqrt(x**2 + y_pos**2)
    # Acelerações (direcionadas para o centro da Terra)
    ax_acc = -mu * x / r**3
    ay_acc = -mu * y_pos / r**3
    return [vx, vy, ax_acc, ay_acc]

# ----------------------------------------------------------------------------
# Função de atualização da animação
# ----------------------------------------------------------------------------
def update(frame):
    global state, t_current, burn_stage

    dt_eff = dt_base  # passo de integração
    sol = solve_ivp(dynamics, [t_current, t_current + dt_eff], state,
                    rtol=1e-9, atol=1e-12)
    state = sol.y[:, -1]
    t_current += dt_eff

    # Armazena a posição para traçar a trajetória
    traj_x.append(state[0])
    traj_y.append(state[1])

    # Calcula a distância atual da nave em relação à Terra
    r = np.sqrt(state[0]**2 + state[1]**2)
    # Se já foi aplicada a primeira queima e a nave se aproxima do apogeu (próximo a r2)
    if burn_stage == 1 and abs(r - r2) < 50e3:  # tolerância de 50 km
        # Aplica a segunda queima para circularizar (ou melhor, para ajustar a velocidade)
        # O impulso é aplicado na direção tangencial: vetor tangente = (-y, x)/r
        tangent = np.array([-state[1], state[0]]) / r
        state[2] += delta_v2 * tangent[0]
        state[3] += delta_v2 * tangent[1]
        burn_stage = 2
        print("Segunda queima realizada: inserção na órbita lunar (simulada).")

    # Atualiza os elementos gráficos
    scat_ship.set_offsets([state[0], state[1]])
    line_traj.set_data(traj_x, traj_y)
    burn_text.set_text(f'Burn Stage: {burn_stage}')
    return scat_ship, line_traj, burn_text

ani = animation.FuncAnimation(fig, update, frames=range(1000), interval=30, blit=True)

# ----------------------------------------------------------------------------
# Botão para iniciar a transferência (primeira queima)
# ----------------------------------------------------------------------------
ax_button_transfer = plt.axes([0.3, 0.1, 0.4, 0.075])
button_transfer = Button(ax_button_transfer, 'Iniciar Transferência')

def initiate_transfer(event):
    global state, burn_stage
    if burn_stage == 0:
        # Aplica a primeira queima (delta_v1) na direção tangencial.
        # Em órbita circular, a direção tangencial pode ser obtida por (-y, x)/r.
        r = np.sqrt(state[0]**2 + state[1]**2)
        tangent = np.array([-state[1], state[0]]) / r
        state[2] += delta_v1 * tangent[0]
        state[3] += delta_v1 * tangent[1]
        burn_stage = 1
        print("Primeira queima realizada: transferência iniciada.")

button_transfer.on_clicked(initiate_transfer)

ax.legend()
plt.show()
