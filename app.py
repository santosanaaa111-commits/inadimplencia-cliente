# Importa a biblioteca streamlit para criar a interface web
import streamlit as st
# Importa a biblioteca pandas para manipulação de dados
import pandas as pd
# Importa a biblioteca os para verificar a existência de arquivos
import os
# Importa o RandomForestClassifier da biblioteca scikit-learn para treinar o modelo
from sklearn.ensemble import RandomForestClassifier
# Importa o codificador LabelEncoder para transformar as variáveis de texto em numéricas
from sklearn.preprocessing import LabelEncoder

# Define o título principal da aplicação na página web
st.title("Previsão de Inadimplência de Clientes")

# Cria uma função cacheada para carregar e preparar os dados de forma rápida
@st.cache_data
def carregar_e_preparar_dados():
    # Define o nome relativo do arquivo com a base de dados
    caminho = 'Inadimplência de Clientes.xlsx'
    # Verifica se o arquivo não existe localmente e tenta o nome alternativo em minúsculo
    if not os.path.exists(caminho):
        # Altera o caminho para a versão alternativa do nome da planilha
        caminho = 'inadimplencia-clientes.xlsx'
    # Carrega a planilha Excel utilizando a biblioteca pandas
    df = pd.read_excel(caminho)
    # Remove linhas que possuem valores nulos para evitar erros no modelo
    df = df.dropna()
    # Retorna o DataFrame limpo para processamento
    return df

# Chama a função para obter o conjunto de dados carregado
dados = carregar_e_preparar_dados()

# Cria um dicionário vazio para armazenar os codificadores de categorias
codificadores = {}

# Cria uma lista com o nome de todas as colunas que possuem dados em formato de texto
colunas_texto = ['Escolaridade', 'Vínculo Empregatício', 'Imóvel Próprio', 'Situação']

# Passa por cada coluna de texto para converter as categorias em números
for coluna in colunas_texto:
    # Inicializa um novo transformador LabelEncoder para a coluna atual
    codificadores[coluna] = LabelEncoder()
    # Ajusta o codificador e substitui a coluna original pelos valores numéricos gerados
    dados[coluna] = codificadores[coluna].fit_transform(dados[coluna])

# Define as colunas de entrada (recursos) para o treinamento do modelo
recursos_entrada = ['Idade', 'Escolaridade', 'Vínculo Empregatício', 'Renda Mensal (R$)', 'Valor do Empréstimo (R$)', 'Prazo (meses)', 'Valor da Parcela (R$)', 'Atrasos Anteriores', 'Tempo de Relacionamento (anos)', 'Imóvel Próprio']

# Separa os dados das variáveis preditoras e armazena na variável X
X = dados[recursos_entrada]

# Separa a variável dependente de interesse (Situação de inadimplência) na variável y
y = dados['Situação']

# Cria uma função cacheada para treinar e manter o modelo na memória do servidor
@st.cache_resource
def treinar_modelo_rf(X_dados, y_dados):
    # Inicializa o classificador Random Forest com parâmetros definidos para reprodutibilidade
    clf = RandomForestClassifier(random_state=42)
    # Treina o algoritmo de floresta aleatória com os dados históricos
    clf.fit(X_dados, y_dados)
    # Retorna o modelo treinado para previsões
    return clf

# Chama a função otimizada para obter o classificador treinado
modelo = treinar_modelo_rf(X, y)

# Cria um cabeçalho na barra lateral do Streamlit para agrupar as opções de entrada
st.sidebar.header("Dados do Novo Cliente")

# Cria um controle deslizante numérico para a idade do cliente
idade = st.sidebar.slider("Idade", int(X['Idade'].min()), int(X['Idade'].max()), 30)

# Cria um seletor para a escolaridade obtendo as opções diretamente do codificador correspondente
escolaridade_opcao = st.sidebar.selectbox("Escolaridade", codificadores['Escolaridade'].classes_)

# Converte a opção selecionada de escolaridade para o seu respectivo valor numérico
escolaridade = codificadores['Escolaridade'].transform([escolaridade_opcao])[0]

# Cria um seletor para o tipo de vínculo de emprego do cliente
vinculo_opcao = st.sidebar.selectbox("Vínculo Empregatício", codificadores['Vínculo Empregatício'].classes_)

# Converte a opção selecionada de vínculo empregatício para o respectivo valor numérico
vinculo = codificadores['Vínculo Empregatício'].transform([vinculo_opcao])[0]

# Cria um campo para digitação numérica da renda mensal do cliente
renda = st.sidebar.number_input("Renda Mensal (R$)", float(X['Renda Mensal (R$)'].min()), float(X['Renda Mensal (R$)'].max()), 5000.0)

# Cria um campo para digitar o valor total do empréstimo desejado
emprestimo = st.sidebar.number_input("Valor do Empréstimo (R$)", float(X['Valor do Empréstimo (R$)'].min()), float(X['Valor do Empréstimo (R$)'].max()), 15000.0)

# Cria um campo para inserir a quantidade de meses solicitada para pagamento
prazo = st.sidebar.number_input("Prazo (meses)", int(X['Prazo (meses)'].min()), int(X['Prazo (meses)'].max()), 36)

# Cria um campo para digitar o valor de cada parcela mensal
parcela = st.sidebar.number_input("Valor da Parcela (R$)", float(X['Valor da Parcela (R$)'].min()), float(X['Valor da Parcela (R$)'].max()), 500.0)

# Cria um seletor numérico para indicar a quantidade de atrasos de pagamento anteriores
atrasos = st.sidebar.slider("Atrasos Anteriores", int(X['Atrasos Anteriores'].min()), int(X['Atrasos Anteriores'].max()), 0)

# Cria um controle deslizante para o tempo em anos de relacionamento com o banco
relacionamento = st.sidebar.slider("Tempo de Relacionamento (anos)", float(X['Tempo de Relacionamento (anos)'].min()), float(X['Tempo de Relacionamento (anos)'].max()), 3.0)

# Cria um seletor para indicar se o cliente possui imóvel próprio cadastrado
imovel_opcao = st.sidebar.selectbox("Imóvel Próprio", codificadores['Imóvel Próprio'].classes_)

# Converte a resposta sobre o imóvel próprio para o formato numérico esperado
imovel = codificadores['Imóvel Próprio'].transform([imovel_opcao])[0]

# Cria um dicionário estruturado para armazenar todas as respostas inseridas
novos_dados = {
    'Idade': [idade],
    'Escolaridade': [escolaridade],
    'Vínculo Empregatício': [vinculo],
    'Renda Mensal (R$)': [renda],
    'Valor do Empréstimo (R$)': [emprestimo],
    'Prazo (meses)': [prazo],
    'Valor da Parcela (R$)': [parcela],
    'Atrasos Anteriores': [atrasos],
    'Tempo de Relacionamento (anos)': [relacionamento],
    'Imóvel Próprio': [imovel]
}

# Converte o dicionário de respostas em um DataFrame do pandas de apenas uma linha
df_cliente = pd.DataFrame(novos_dados)

# Cria um botão de ação para realizar o diagnóstico de inadimplência na tela principal
se_clicado = st.button("Avaliar Inadimplência")

# Executa o bloco de previsão caso o usuário decida clicar no botão
if se_clicado:
    # Utiliza o modelo treinado para prever a classe do novo cliente inserido
    previsao = modelo.predict(df_cliente)[0]
    # Recupera o texto original correspondente à situação numérica prevista
    resultado_texto = codificadores['Situação'].inverse_transform([previsao])[0]
    # Verifica se o resultado indica que o cliente corre risco de inadimplência
    if resultado_texto == 'Inadimplente':
        # Exibe um aviso em destaque vermelho sinalizando o alto risco do cliente
        st.error("Atenção: O modelo prevê alta chance de INADIMPLÊNCIA para este cliente.")
    # Executa esta ação caso o resultado da previsão seja de adimplência
    else:
        # Exibe uma mensagem de sucesso verde indicando baixo risco de inadimplência
        st.success("Sucesso: O modelo prevê que o cliente será ADIMPLENTE.")
