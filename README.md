# `rm_atividade1` --- Robótica Móvel com ROS 2

**Desenvolvido por:** Marcelo Alves Batista e Gabriel Marlon Viana

Workspace ROS 2 desenvolvido para a atividade de percepção e navegação
autônoma do robô móvel `rm_bot`. O sistema utiliza dados do LiDAR e da
odometria para acompanhar objetivos e realizar desvios reativos de
obstáculos durante a simulação no Gazebo.

## Requisitos

-   Ubuntu com **ROS 2 Jazzy** instalado.
-   `colcon` e as dependências necessárias dos pacotes do workspace.
-   Gazebo e os pacotes de simulação do `rm_bot` disponíveis no ambiente
    ROS 2.

> Os comandos abaixo consideram que o diretório `rm_atividade1` está no
> diretório atual do terminal.

## Estrutura do projeto

``` text
rm_atividade1/
├── dados.csv                         # Dados registrados durante a execução
├── plot_graficos.py                  # Geração dos gráficos a partir do CSV
├── src/
│   ├── rm_atividade1/
│   │   ├── config/navigation.yaml    # Parâmetros de navegação
│   │   ├── launch/atividade1.launch.py
│   │   ├── rviz/                     # Configuração do RViz
│   │   ├── worlds/                   # Mundos da simulação
│   │   └── rm_atividade1/            # Nós e lógica de controle
│   ├── rm_bot/
│   ├── rm_bot_description/
│   └── rm_bot_sim/
└── ...
```

## Compilar o workspace

Abra um terminal e execute os comandos a seguir, na ordem indicada:

``` bash
cd rm_atividade1
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
```

O comando `colcon build` compila os pacotes localizados em `src/`. A
opção `--symlink-install` utiliza links simbólicos para os arquivos
compatíveis, facilitando o desenvolvimento. A opção
`-DBUILD_TESTING=OFF` desativa a configuração dos testes durante a
compilação.

Sempre que abrir um novo terminal para trabalhar com o workspace,
carregue os ambientes ROS 2 e do projeto:

``` bash
source /opt/ros/jazzy/setup.bash
cd rm_atividade1
source install/setup.bash
```

Se houver alterações nos arquivos que exijam uma nova compilação,
execute novamente o comando `colcon build` e depois carregue o ambiente
com `source install/setup.bash`.

## Executar a simulação

Com o workspace compilado e o ambiente carregado, execute:

``` bash
ros2 launch rm_atividade1 atividade1.launch.py mode:=auto
```

O argumento `mode:=auto` inicia o sistema em modo automático, incluindo
o nó de navegação. O arquivo de lançamento também declara os argumentos
`headless` e `rviz`, que permitem configurar a execução sem interface
gráfica e a inicialização do RViz, respectivamente.

## Escolher o mundo da simulação

Há dois mundos disponíveis no pacote `rm_atividade1`:

-   `world_without_obs.sdf` --- cenário sem obstáculos.
-   `world_with_obs.sdf` --- cenário com obstáculos.

Para selecionar o cenário, abra:

``` text
src/rm_atividade1/launch/atividade1.launch.py
```

No arquivo de lançamento, localize a configuração do argumento `world`
dentro da inclusão da simulação. Altere o nome do arquivo na linha
correspondente, substituindo `world_without_obs.sdf` por
`world_with_obs.sdf`, ou vice-versa.

Por exemplo, para utilizar o mundo com obstáculos, a configuração deve
apontar para:

``` python
'world': PathJoinSubstitution([share, 'worlds', 'world_with_obs.sdf']),
```

Salve o arquivo antes de iniciar a simulação novamente. Se o arquivo de
lançamento estiver instalado por cópia em vez de link simbólico, pode
ser necessário recompilar o workspace para que a alteração seja
refletida na instalação.

## Monitorar a classificação dos setores do LiDAR

Durante a execução, o nó de navegação publica o estado da classificação
por setores no tópico `/sector_state`, usando mensagens do tipo
`std_msgs/msg/String`.

Para acompanhar as mensagens em tempo real, abra outro terminal,
carregue os ambientes ROS 2 e do workspace e execute:

``` bash
cd rm_atividade1
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 topic echo /sector_state
```

O tópico informa a classificação dos setores do LiDAR. Para consultar o
tipo da mensagem publicada, utilize:

``` bash
ros2 topic info /sector_state
```

## Registro dos dados e geração dos gráficos

Durante a execução do nó de navegação, os dados da simulação são
registrados no arquivo `dados.csv`, localizado na raiz do workspace:

``` text
rm_atividade1/dados.csv
```

O arquivo registra informações usadas para analisar a trajetória e o
estado da navegação, incluindo tempo, posição e orientação do robô,
objetivo atual e estado registrado pelo sistema. **A inicialização do nó
de navegação limpa o conteúdo anterior de `dados.csv`**, portanto salve
ou copie os dados de uma execução antes de iniciar outra caso queira
preservá-los.

Após a simulação, gere os gráficos executando o script na raiz do
projeto:

``` bash
cd rm_atividade1
python3 plot_graficos.py
```

Execute o script no ambiente Python que possua as bibliotecas utilizadas
por ele instaladas. Os gráficos são gerados a partir dos dados
disponíveis em `dados.csv`.

## Tópicos principais

  -----------------------------------------------------------------------------
  Tópico                  Tipo de mensagem              Finalidade
  ----------------------- ----------------------------- -----------------------
  `/scan`                 `sensor_msgs/msg/LaserScan`   Leituras do sensor
                                                        LiDAR.

  `/odom`                 `nav_msgs/msg/Odometry`       Estimativa de posição e
                                                        orientação do robô.

  `/cmd_vel_auto`         `geometry_msgs/msg/Twist`     Comandos de velocidade
                                                        gerados pela navegação
                                                        automática.

  `/cmd_vel`              `geometry_msgs/msg/Twist`     Tópico de comando de
                                                        velocidade usado pelo
                                                        controle do robô.

  `/navigation_state`     `std_msgs/msg/String`         Estado da navegação.

  `/sector_state`         `std_msgs/msg/String`         Classificação dos
                                                        setores do LiDAR.
  -----------------------------------------------------------------------------

Para listar os tópicos ativos durante a simulação:

``` bash
ros2 topic list
```

## Parâmetros e comportamento da navegação

A navegação acompanha sequencialmente os destinos definidos no código:
`P1 = (1, 0)`, `P2 = (3, 0)` e `P3 = (3, 2)`. O controlador utiliza a
odometria para estimar a posição do robô e o LiDAR para avaliar a
presença de obstáculos.

Entre os parâmetros configuráveis em
`src/rm_atividade1/config/navigation.yaml` estão os limites de
velocidade, a tolerância de chegada, a margem de segurança e os limites
de atualização dos dados. Consulte esse arquivo antes de alterar o
comportamento do controlador.

## Solução de problemas

-   **`ros2 launch` não encontra o pacote:** confirme que a compilação
    terminou sem erros e que executou `source install/setup.bash` no
    terminal atual.
-   **O comando `colcon` não é encontrado:** verifique a instalação das
    ferramentas de desenvolvimento do ROS 2.
-   **O mundo não mudou:** confira o nome do arquivo em
    `atividade1.launch.py` e, se necessário, compile novamente o
    workspace.
-   **Não aparecem mensagens em `/sector_state`:** confirme que a
    simulação está ativa, que o nó de navegação foi iniciado em modo
    automático e que o tópico existe com `ros2 topic list`.
-   **O CSV não contém os dados esperados:** verifique se a navegação
    foi iniciada e se o arquivo `dados.csv` está sendo criado na raiz do
    projeto.

------------------------------------------------------------------------
