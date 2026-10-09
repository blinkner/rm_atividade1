import pandas as pd
import matplotlib.pyplot as plt

def plotar_trajetoria(caminho_csv='dados.csv'):
    # 1. Carregar os dados definindo os nomes das colunas
    colunas = ['tempo', 'p_x', 'p_y', 'p_yaw', 'goal_x', 'goal_y', 'log_state']
    
    try:
        df = pd.read_csv(caminho_csv, names=colunas, header=None)
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_csv}' não foi encontrado.")
        return

    # 2. Configurar o gráfico
    plt.figure(figsize=(10, 8))
    
    # Plota a trajetória percorrida pelo robô (Linha contínua)
    plt.plot(df['p_x'], df['p_y'], color='blue', linewidth=2, label='Trajetória do Robô')
    
    # Plota o ponto de partida (Início)
    plt.scatter(df['p_x'].iloc[0], df['p_y'].iloc[0], color='green', marker='o', s=100, label='Início', zorder=5)
    
    # Plota a posição final registrada do robô
    plt.scatter(df['p_x'].iloc[-1], df['p_y'].iloc[-1], color='purple', marker='X', s=100, label='Posição Final', zorder=5)
    
    # Plota a posição do objetivo (Goal)
    # Pega a última coordenada registrada para o goal
    goal_x = df['goal_x'].iloc[-1]
    goal_y = df['goal_y'].iloc[-1]
    plt.scatter(goal_x, goal_y, color='red', marker='*', s=200, label='Objetivo (Goal)', zorder=5)

    # 3. Personalização do gráfico
    plt.title('Trajetória Percorrida pelo Robô na Simulação', fontsize=14)
    plt.xlabel('Posição X (m)', fontsize=12)
    plt.ylabel('Posição Y (m)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.axis('equal')  # Mantém a proporção real dos eixos X e Y
    plt.legend(loc='best')
    
    # Exibir o gráfico
    plt.tight_layout()
    plt.show()

# Executar a função
if __name__ == "__main__":
    plotar_trajetoria()