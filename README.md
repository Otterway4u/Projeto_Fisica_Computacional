# Simulação do Sistema Terra, Nave e Lua

Este repositório contém um código em Python que simula o movimento gravitacional de três corpos principais (Terra, Lua e Nave) e permite controlar a nave em tempo real. A simulação é feita com a biblioteca [Pygame](https://www.pygame.org/news) para visualização gráfica.

## Características Principais

- **Visualização em Tempo Real**: A Terra, Lua e Nave são desenhadas em uma janela, com trajetória atualizada a cada iteração.
- **Integração Numérica**: São consideradas as forças gravitacionais entre os corpos, atualizando as posições e velocidades a cada passo de tempo.
- **Impulso (Thrust) Direcional**: Mantendo a tecla `SPACE` pressionada, é aplicada uma aceleração extra à Nave, em diferentes modos (Progressivo, Retrógrado, Radial ou Anti Radial).
- **Controle de Tempo**: A simulação pode ser acelerada para `10x` ou `50x` do passo de tempo base, mas com subdivisões para evitar erros significativos.
- **Trajetória Futura**: Uma função auxiliar exibe uma projeção aproximada da posição futura da nave, desenhada na cor roxa.

---

## Requisitos

- **Python 3.x**  
- **Bibliotecas**:
  - [numpy](https://numpy.org/)
  - [pygame](https://www.pygame.org/news)
  - [math] (já incluso na biblioteca padrão do Python)

Você pode instalar as bibliotecas necessárias com:
```bash
pip install numpy pygame
```
