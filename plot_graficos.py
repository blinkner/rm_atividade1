import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches  # Adicionado para desenhar os obstáculos
import math

def mapear_descricao_cenario(row):
    """Mapeia o estado e as coordenadas do objetivo para uma explicação clara."""
    state = str(row['log_state'])
    gx, gy = row['goal_x'], row['goal_y']
    
    # Identifica qual é o ponto de destino ativo
    if abs(gx - 1.0) < 0.1 and abs(gy - 0.0) < 0.1:
        ponto = "P1 (1.0, 0.0)"
    elif abs(gx - 3.0) < 0.1 and abs(gy - 0.0) < 0.1:
        ponto = "P2 (3.0, 0.0)"
    elif abs(gx - 3.0) < 0.1 and abs(gy - 2.0) < 0.1:
        ponto = "P3 (3.0, 2.0)"
    else:
        ponto = f"({gx:.1f}, {gy:.1f})"

    # Mapeamento para estados de chegada específicos
    if state.startswith('CHEGOU_P'):
        p_nome = state.replace('CHEGOU_', '')
        return f"Robô alcançou o destino {p_nome} dentro da tolerância exigida"
    elif state == 'INDO_AO_PONTO':
        return f"Robô navegando em linha reta em direção ao ponto {ponto}"
    elif state == 'DESVIANDO':
        return f"Robô executando manobra de desvio de obstáculo rumo ao ponto {ponto}"
    elif state == 'MISSAO_CONCLUIDA':
        return "Missão finalizada com sucesso em P3 (robô parado)"
    elif state == 'AGUARDANDO_OBJETIVO':
        return "Sistema aguardando definição de objetivo"
    elif state == 'SEM_DADOS_ATUAIS':
        return "Movimento interrompido por ausência de dados atualizados (LiDAR/Odom)"
    elif state == 'BLOQUEADO':
        return f"Caminho totalmente obstruído sem passagem livre rumo a {ponto}"
    elif state == 'SCAN_INVALIDO':
        return "Parada de segurança devido à cobertura insuficiente do sensor"
    elif state == 'SEM_PROGRESSO_REENVIE_OBJETIVO':
        return f"Tempo limite de progresso excedido sem aproximação de {ponto}"
    else:
        return f"Estado {state} ativo rumo ao ponto {ponto}"

def gerar_tabela_estados(df):
    """Agrupa intervalos contínuos de estados iguais e gera a tabela explicativa."""
    df = df.copy()
    df["tempo_norm"] = df["tempo"] - df["tempo"].iloc[0]

    # Identifica trocas de blocos contínuos de 'log_state' ou de 'goal_x/goal_y'
    troca_estado = (df['log_state'] != df['log_state'].shift(1)) | \
                   (df['goal_x'] != df['goal_x'].shift(1)) | \
                   (df['goal_y'] != df['goal_y'].shift(1))
    
    df['bloco_id'] = troca_estado.cumsum()

    blocos = []
    for bloco_id, group in df.groupby('bloco_id'):
        t_inicio = group['tempo_norm'].iloc[0]
        t_fim = group['tempo_norm'].iloc[-1]
        estado = group['log_state'].iloc[0]
        goal_x = group['goal_x'].iloc[0]
        goal_y = group['goal_y'].iloc[0]
        
        row_rep = {'log_state': estado, 'goal_x': goal_x, 'goal_y': goal_y}
        descricao = mapear_descricao_cenario(row_rep)
        
        intervalo_str = f"[{t_inicio:.1f}s - {t_fim:.1f}s]"
        duracao = t_fim - t_inicio
        
        # Garante que estados instantâneos de chegada (CHEGOU_Px) entrem na tabela
        if duracao >= 0.1 or str(estado).startswith('CHEGOU_P') or estado in ['CHEGOU', 'MISSAO_CONCLUIDA']:
            blocos.append({
                'Intervalo de Tempo': intervalo_str,
                'Estado (log_state)': estado,
                'Explicação do Cenário': descricao
            })

    df_tabela = pd.DataFrame(blocos)
    return df_tabela

def plotar_trajetoria(caminho_csv='/home/batista/rm_atividade1/dados.csv'):
    colunas = ['tempo', 'p_x', 'p_y', 'p_yaw', 'goal_x', 'goal_y', 'log_state']
    
    try:
        df = pd.read_csv(caminho_csv, names=colunas, header=None)
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_csv}' não foi encontrado.")
        return

    # Normalização do tempo
    df["tempo_norm"] = df["tempo"] - df["tempo"].iloc[0]

    # 1. Gerar e exibir a Tabela de Histórico de Estados
    tabela = gerar_tabela_estados(df)
    print("\n" + "="*85)
    print("                      TABELA DE HISTÓRICO DE ESTADOS DA MISSÃO")
    print("="*85)
    print(tabela.to_string(index=False))
    print("="*85 + "\n")

    # Salva a tabela formatada em CSV
    tabela.to_csv('tabela_estados_relatorio.csv', index=False)

    # 2. Configurar o gráfico de trajetória
    fig, ax = plt.subplots(figsize=(10, 8))
    
    ax.plot(df['p_x'], df['p_y'], color='blue', linewidth=2, label='Trajetória do Robô')
    ax.scatter(df['p_x'].iloc[0], df['p_y'].iloc[0], color='green', marker='o', s=100, label='Início S(0,0)', zorder=5)
    ax.scatter(df['p_x'].iloc[-1], df['p_y'].iloc[-1], color='purple', marker='X', s=100, label='Posição Final', zorder=5)
    
    # -------------------------------------------------------------------------
    # Inserção dos Obstáculos no Gráfico
    # -------------------------------------------------------------------------
    obstaculos = [(2.0, 0.0), (3.0, 1.0)]
    largura, altura = 0.40, 0.40

    for i, (obs_x, obs_y) in enumerate(obstaculos):
        # Calcula o canto inferior esquerdo a partir do ponto central
        canto_x = obs_x - (largura / 2.0)
        canto_y = obs_y - (altura / 2.0)
        
        # Cria a forma retangular do obstáculo
        retangulo = patches.Rectangle(
            (canto_x, canto_y), largura, altura,
            linewidth=1.5, edgecolor='black', facecolor='gray',
            hatch='//', alpha=0.75, zorder=4,
            label='Obstáculo' if i == 0 else "" # Adiciona à legenda apenas no primeiro obstáculo
        )
        ax.add_patch(retangulo)
    # -------------------------------------------------------------------------

    # Destinos de referência teóricos
    waypoints = {'P1': (1.0, 0.0), 'P2': (3.0, 0.0), 'P3': (3.0, 2.0)}
    
    # Busca na tabela os instantes de chegada para calcular o erro exato
    for nome, (wx, wy) in waypoints.items():
        ax.scatter(wx, wy, color='red', marker='*', s=180, zorder=5)
        
        # Filtra a linha exata onde o robô registrou a chegada no ponto
        df_chegada = df[df['log_state'] == f'CHEGOU_{nome}']
        
        if not df_chegada.empty:
            px = df_chegada['p_x'].iloc[0]
            py = df_chegada['p_y'].iloc[0]
            
            # Cálculo do erro euclidiano e_k = sqrt((x_k - x)^2 + (y_k - y)^2)
            erro_abs = math.hypot(wx - px, wy - py)
            
            # Formatação do texto: Nome do Ponto + Erro Euclidiano + Coordenadas
            texto_anotacao = f"{nome}\nErro: {erro_abs:.3f} m\n({wx:.1f}, {wy:.1f})"
        else:
            texto_anotacao = f"{nome}\n({wx:.1f}, {wy:.1f})"
            
        # Insere a anotação gráfica logo acima/ao lado de cada waypoint
        ax.annotate(
            texto_anotacao, 
            (wx + 0.12, wy - 0.08), 
            fontsize=9, 
            fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="red", lw=1, alpha=0.8)
        )

    plt.title('Trajetória Percorrida pelo Robô com Erros de Chegada', fontsize=14)
    plt.xlabel('Posição X (m)', fontsize=12)
    plt.ylabel('Posição Y (m)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.axis('equal')
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plotar_trajetoria()