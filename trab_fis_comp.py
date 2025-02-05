import pygame
import numpy as np
import math

# Inicializa o Pygame
pygame.init()
width, height = 1200, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Simulação com Thrust, Tempo 1x/10x/50x e Trajetória Futura")

# Cores
WHITE  = (255, 255, 255)
BLUE   = (0, 0, 255)       # Terra
GRAY   = (128, 128, 128)   # Lua
RED    = (255, 0, 0)       # Nave
BLACK  = (0, 0, 0)
GREEN  = (0, 255, 0)       # Botões selecionados
PURPLE = (128, 0, 128)     # Trajetória futura

# Fonte para textos
font = pygame.font.SysFont(None, 24)

# --- CONSTANTES FÍSICAS ---
G = 6.67430e-11    # m³/(kg·s²)
mEarth = 5.9723e24
mMoon  = 7.349e22
mShip  = 8000

# --- PARÂMETROS DO IMPULSO ---
thrust_const = 1.0

# Modo de thrust: opções: "Progressiva", "Retrógrado", "Radial", "Anti Radial"
thrust_mode = "Progressiva"

# Botões para seleção do modo de thrust
button_options = [
    {"label": "Progressiva", "rect": pygame.Rect(20, 200, 150, 30)},
    {"label": "Retrógrado",   "rect": pygame.Rect(20, 240, 150, 30)},
    {"label": "Radial",       "rect": pygame.Rect(20, 280, 150, 30)},
    {"label": "Anti Radial",  "rect": pygame.Rect(20, 320, 150, 30)}
]

# Botão para fator de tempo: cicla entre 1x, 10x e 50x
time_button = {"label": "Tempo", "rect": pygame.Rect(20, 360, 150, 30)}
time_factors = [1, 10, 50]
time_factor_index = 0
time_factor = time_factors[time_factor_index]

# Botão para exibir a trajetória futura
future_button = {"label": "Traj. Futura", "rect": pygame.Rect(20, 400, 150, 30)}
show_future_trajectory = False

# --- FUNÇÃO DE RESET DA SIMULAÇÃO ---
def reset_simulation():
    global r_earth, v_earth, r_ship, v_ship, r_moon, v_moon
    global traj_ship, traj_earth, traj_moon, thrust_mode, time_factor, time_factor_index, show_future_trajectory
    # Terra fixa no centro
    r_earth = np.array([0.0, 0.0])
    v_earth = np.array([0.0, 0.0])
    # Nave em órbita baixa (LEO) com raio 7000 km
    rOrbit = 7000e3
    vOrbit = np.sqrt(G * mEarth / rOrbit)
    r_ship = np.array([rOrbit, 0.0])
    v_ship = np.array([0.0, vOrbit])
    # Lua: posição média (~384400 km da Terra) e velocidade aproximada
    r_moon = np.array([384400e3, 0.0])
    v_moon = np.array([0.0, 1022.0])
    traj_ship = []
    traj_earth = []
    traj_moon = []
    thrust_mode = "Progressiva"
    time_factor_index = 0
    time_factor = time_factors[time_factor_index]
    show_future_trajectory = False
    return traj_ship, traj_earth, traj_moon, thrust_mode, time_factor, time_factor_index, show_future_trajectory

traj_ship, traj_earth, traj_moon, thrust_mode, time_factor, time_factor_index, show_future_trajectory = reset_simulation()

# --- CONTROLE DO TEMPO ---
dt = 10  # passo de tempo base (s)

# --- FATOR DE ESCALA ---
scale = 1e-6  # converte metros para pixels
center = np.array([width // 2, height // 2])

clock = pygame.time.Clock()
running = True
thrust_on = False

# Função para computar a trajetória futura com subdivisão de passos
def compute_future_trajectory(r_ship, v_ship, r_earth, v_earth, r_moon, v_moon, dt_eff, steps=500, skip=1, substeps=1):
    future_positions = []
    # Cópias locais dos estados
    local_r_ship = r_ship.copy()
    local_v_ship = v_ship.copy()
    local_r_earth = r_earth.copy()
    local_v_earth = v_earth.copy()
    local_r_moon  = r_moon.copy()
    local_v_moon  = v_moon.copy()
    
    dt_sub = dt_eff / substeps
    for i in range(steps):
        for _ in range(substeps):
            diff_earth = local_r_earth - local_r_ship
            diff_moon  = local_r_moon - local_r_ship
            a_ship = (G * mEarth * diff_earth / np.linalg.norm(diff_earth)**3 +
                      G * mMoon  * diff_moon  / np.linalg.norm(diff_moon)**3)
            local_v_ship += a_ship * dt_sub
            local_r_ship += local_v_ship * dt_sub

            diff_ship_earth = local_r_ship - local_r_earth
            diff_moon_earth = local_r_moon - local_r_earth
            a_earth = (G * mShip * diff_ship_earth / np.linalg.norm(diff_ship_earth)**3 +
                       G * mMoon * diff_moon_earth / np.linalg.norm(diff_moon_earth)**3)
            local_v_earth += a_earth * dt_sub
            local_r_earth += local_v_earth * dt_sub

            diff_ship_moon = local_r_ship - local_r_moon
            diff_earth_moon = local_r_earth - local_r_moon
            a_moon = (G * mShip * diff_ship_moon / np.linalg.norm(diff_ship_moon)**3 +
                      G * mEarth * diff_earth_moon / np.linalg.norm(diff_earth_moon)**3)
            local_v_moon += a_moon * dt_sub
            local_r_moon += local_v_moon * dt_sub
        
        if i % skip == 0:
            future_positions.append(local_r_ship.copy())
    return future_positions

while running:
    # Processa eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Ativa/desativa o impulso com SPACE e reinicia com R
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                thrust_on = True
                print("Impulso ativado")
            if event.key == pygame.K_r:
                traj_ship, traj_earth, traj_moon, thrust_mode, time_factor, time_factor_index, show_future_trajectory = reset_simulation()
                print("Simulação reiniciada")
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                thrust_on = False
                print("Impulso desativado")
        
        # Verifica cliques do mouse para os botões
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # Botões de modo de thrust
            for button in button_options:
                if button["rect"].collidepoint(mouse_pos):
                    thrust_mode = button["label"]
                    print("Modo de thrust selecionado:", thrust_mode)
            # Botão de fator de tempo: cicla entre 1x, 10x e 50x
            if time_button["rect"].collidepoint(mouse_pos):
                time_factor_index = (time_factor_index + 1) % len(time_factors)
                time_factor = time_factors[time_factor_index]
                print("Fator de tempo alterado para:", time_factor, "x")
            # Botão de trajetória futura
            if future_button["rect"].collidepoint(mouse_pos):
                show_future_trajectory = not show_future_trajectory
                print("Exibir trajetória futura:", show_future_trajectory)
    
    # Calcula o ângulo do thrust conforme o modo selecionado
    if thrust_mode == "Progressiva":
        thrust_angle = math.atan2(v_ship[1], v_ship[0])
    elif thrust_mode == "Retrógrado":
        thrust_angle = math.atan2(v_ship[1], v_ship[0]) + math.pi
    elif thrust_mode == "Radial":
        thrust_angle = math.atan2(r_ship[1] - r_earth[1], r_ship[0] - r_earth[0])
    elif thrust_mode == "Anti Radial":
        thrust_angle = math.atan2(r_earth[1] - r_ship[1], r_earth[0] - r_ship[0])
    else:
        thrust_angle = math.atan2(v_ship[1], v_ship[0])
    
    # Integração com subdivisão para evitar saltos muito grandes
    dt_effective = dt * time_factor
    substeps = 10 if time_factor == 50 else 1
    dt_sub = dt_effective / substeps
    
    for _ in range(substeps):
        # Recalcula acelerações para cada subpasso
        r_earth_to_ship = r_earth - r_ship
        r_moon_to_ship  = r_moon - r_ship
        a_ship = (G * mEarth * r_earth_to_ship / np.linalg.norm(r_earth_to_ship)**3 +
                  G * mMoon  * r_moon_to_ship  / np.linalg.norm(r_moon_to_ship)**3)
        r_ship_to_earth = r_ship - r_earth
        r_moon_to_earth = r_moon - r_earth
        a_earth = (G * mShip * r_ship_to_earth / np.linalg.norm(r_ship_to_earth)**3 +
                   G * mMoon * r_moon_to_earth / np.linalg.norm(r_moon_to_earth)**3)
        r_ship_to_moon = r_ship - r_moon
        r_earth_to_moon = r_earth - r_moon
        a_moon = (G * mShip * r_ship_to_moon / np.linalg.norm(r_ship_to_moon)**3 +
                  G * mEarth * r_earth_to_moon / np.linalg.norm(r_earth_to_moon)**3)
        
        v_ship += a_ship * dt_sub
        v_earth += a_earth * dt_sub
        v_moon  += a_moon * dt_sub
        
        if thrust_on:
            direction = np.array([math.cos(thrust_angle), math.sin(thrust_angle)])
            v_ship += thrust_const * direction * dt_sub
        
        r_ship += v_ship * dt_sub
        r_earth += v_earth * dt_sub
        r_moon  += v_moon * dt_sub
    
    traj_ship.append(r_ship.copy())
    traj_earth.append(r_earth.copy())
    traj_moon.append(r_moon.copy())
    
    # Renderização
    screen.fill(WHITE)
    
    pos_earth = center + r_earth * scale
    pos_moon  = center + r_moon * scale
    pos_ship  = center + r_ship * scale
    
    pygame.draw.circle(screen, BLUE, (int(pos_earth[0]), int(pos_earth[1])), 20)
    pygame.draw.circle(screen, GRAY, (int(pos_moon[0]), int(pos_moon[1])), 10)
    pygame.draw.circle(screen, RED, (int(pos_ship[0]), int(pos_ship[1])), 5)
    
    if len(traj_ship) > 1:
        points = [(int(center[0] + p[0]*scale), int(center[1] + p[1]*scale)) for p in traj_ship]
        pygame.draw.lines(screen, RED, False, points, 1)
    if len(traj_moon) > 1:
        points = [(int(center[0] + p[0]*scale), int(center[1] + p[1]*scale)) for p in traj_moon]
        pygame.draw.lines(screen, GRAY, False, points, 1)
    if len(traj_earth) > 1:
        points = [(int(center[0] + p[0]*scale), int(center[1] + p[1]*scale)) for p in traj_earth]
        pygame.draw.lines(screen, BLUE, False, points, 1)
    
    # Desenha a trajetória futura, se ativada
    if show_future_trajectory:
        skip_value = 5 if time_factor == 50 else 1
        substeps_value = 10 if time_factor == 50 else 1
        future_positions = compute_future_trajectory(r_ship, v_ship, r_earth, v_earth, r_moon, v_moon,
                                                     dt_effective, steps=500, skip=skip_value, substeps=substeps_value)
        if future_positions:
            future_points = [(int(center[0] + p[0]*scale), int(center[1] + p[1]*scale)) for p in future_positions]
            pygame.draw.lines(screen, PURPLE, False, future_points, 2)
    
    # Instruções e status
    instructions = [
        "SPACE: Manter para ativar impulso",
        "R: Reiniciar simulação",
        f"Thrust: {'Ativado' if thrust_on else 'Desativado'}",
        f"Modo de Thrust: {thrust_mode}",
        f"Velocidade: {np.linalg.norm(v_ship):.2f} m/s",
        f"Aceleração do Thrust: {thrust_const:.1f} m/s²",
        f"Fator de Tempo: {time_factor}x"
    ]
    for i, line in enumerate(instructions):
        txt = font.render(line, True, BLACK)
        screen.blit(txt, (20, 20 + i * 25))
    
    # Desenha os botões
    for button in button_options:
        color = GREEN if button["label"] == thrust_mode else BLACK
        pygame.draw.rect(screen, color, button["rect"], 2)
        txt = font.render(button["label"], True, BLACK)
        txt_rect = txt.get_rect(center=button["rect"].center)
        screen.blit(txt, txt_rect)
    
    time_text = f"Tempo: {time_factor}x"
    time_color = GREEN if time_factor > 1 else BLACK
    pygame.draw.rect(screen, time_color, time_button["rect"], 2)
    txt = font.render(time_text, True, BLACK)
    txt_rect = txt.get_rect(center=time_button["rect"].center)
    screen.blit(txt, txt_rect)
    
    future_color = GREEN if show_future_trajectory else BLACK
    pygame.draw.rect(screen, future_color, future_button["rect"], 2)
    txt = font.render(future_button["label"], True, BLACK)
    txt_rect = txt.get_rect(center=future_button["rect"].center)
    screen.blit(txt, txt_rect)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
