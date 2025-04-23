import streamlit as st
import pandas as pd
from io import BytesIO

def configurar_estilo():
    """Configura o estilo da página."""
    st.set_page_config(page_title="Avaliador de Prospect", layout="centered")
    st.markdown(
        """
        <style>
            /* Configuração geral */
            body {
                background-color: #333;
                color: #f5f5f5;
                font-family: 'Arial', sans-serif;
            }
            .stApp {
                background-color: #333;
            }

            /* Títulos */
            h1, h2, h3, h4, h5, h6 {
                color: #222;
                font-weight: bold;
            }

            /* Botões */
            .stButton>button {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 0.5em 1em;
                font-size: 1em;
                transition: background-color 0.3s ease;
            }
            .stButton>button:hover {
                background-color: #0056b3;
            }

            /* Campos de entrada */
            .stTextInput input, .stNumberInput input, .stSelectbox select {
                background-color: #fff;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 0.5em;
                font-size: 1em;
            }

            /* Mensagens de alerta */
            .stAlert {
                border-radius: 5px;
                padding: 1em;
                font-size: 1em;
            }
            .stAlert.success {
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .stAlert.info {
                background-color: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
            }
            .stAlert.warning {
                background-color: #fff3cd;
                color: #856404;
                border: 1px solid #ffeeba;
            }
            .stAlert.error {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }

            /* Tabelas */
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 1em 0;
                font-size: 1em;
                color: #333;
            }
            table th, table td {
                border: 1px solid #ddd;
                padding: 0.5em;
                text-align: left;
            }
            table th {
                background-color: #f2f2f2;
                font-weight: bold;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

def calcular_pontuacao(respostas, peso_padrao=10):
    """Calcula a pontuação com base nas respostas fornecidas."""
    pontuacao = 0
    lojas = respostas.get("Quantas lojas?", 0)

    for pergunta, resposta in respostas.items():
        if pergunta == "Quantas lojas?":
            if resposta == 1:
                pontuacao += 2
            elif 2 <= resposta <= 5:
                pontuacao += 4
            elif resposta > 5:
                pontuacao += 5
        elif pergunta == "Quantas máquinas?":
            if 1 <= resposta <= 3:
                pontuacao += 1
            elif 4 <= resposta <= 7:
                pontuacao += 3
            elif 8 <= resposta <= 16:
                pontuacao += 4
            elif 17 <= resposta <= 100:
                pontuacao += 5
        elif pergunta == "Infraestrutura adequada? (Parque das máquinas)":
            pontuacao += 1
        elif pergunta == "Replicação?":
            if resposta == "Sim":
                pontuacao += 3 if lojas <= 2 else 4
            else:
                pontuacao += 1
        elif pergunta == "Enquadramento, Lucro Real ou Presumido?":
            pontuacao += 3 if resposta == "Sim" else 1
        elif pergunta == "Venda para fora da UF em grande volume?":
            pontuacao += 5 if resposta == "Sim" else 0
        elif pergunta == "Financeiro Plus?":
            pontuacao += 4 if resposta == "Sim" else 0
        elif pergunta == "Atualmente possui um E-Commerce?":
            venda_uf = respostas.get("Venda para fora da UF em grande volume?", "Não")
            if resposta == "Sim":
                pontuacao += 5 if venda_uf == "Sim" else 3
            else:
                pontuacao += 1
        elif pergunta == "Loja Nova ou Importação?":
            pontuacao += 3 if resposta == "Importação" else 2 if resposta == "Nova Loja" else 0
        elif pergunta == "Motivo da troca de sistema?":
            if resposta == "Preço":
                pontuacao += 3
            elif resposta == "Sistema mais fácil de utilizar":
                pontuacao += 2
            elif resposta == "Sistema mais complexo com mais recursos":
                pontuacao += 3
            elif resposta == "Suporte":
                pontuacao += 4
            elif resposta == "Desentendimento com sistema anterior":
                pontuacao += 4
        elif pergunta == "Mais de uma loja com bancos diferentes?":
            if resposta == "Sim":
                pontuacao += 4
            elif lojas > 1:
                pontuacao += 3
            else:
                pontuacao += 1
        elif pergunta == "O projeto possui um responsável por parte da farmácia, engajado e ciente que sua participação será necessária para o sucesso do projeto?":
            pontuacao += 1 if resposta == "Sim" else 4
        elif pergunta == "Alguma particularidade que considere incomum?":
            texto, peso = resposta
            pontuacao += peso
        elif pergunta == "Qual sistema do cliente a ser migrado?":
            if resposta == "Trier":
                pontuacao += 3
            elif resposta == "Digifarma":
                pontuacao += 2
            elif resposta == "Inovafarma":
                pontuacao += 3
            elif resposta == "BIG":
                pontuacao += 3
            elif resposta == "Softpharma":
                pontuacao += 4
            elif resposta == "Automatiza":
                pontuacao += 4
            elif resposta == "Alpha7":
                pontuacao += 4
        elif isinstance(resposta, int) or isinstance(resposta, float):
            if resposta > 0:
                pontuacao += peso_padrao
        elif resposta == "Sim":
            pontuacao += peso_padrao

    return pontuacao

def exibir_resultado(pontuacao, respostas):
    """Exibe o resultado da avaliação e permite download do Excel."""
    st.subheader("Resultado da Avaliação")
    st.write(f"Pontuação Total: **{pontuacao}**")

    if pontuacao >= 40:
        classificacao = "Rank S"
        st.success(f"Classificação: {classificacao}")
    elif pontuacao >= 30:
        classificacao = "Rank A"
        st.success(f"Classificação: {classificacao}")
    elif pontuacao >= 20:
        classificacao = "Rank B"
        st.info(f"Classificação: {classificacao}")
    elif pontuacao >= 10:
        classificacao = "Rank C"
        st.warning(f"Classificação: {classificacao}")
    else:
        classificacao = "Rank D"
        st.error(f"Classificação: {classificacao}")

    # Corrigindo o erro ao acessar os valores de respostas
    peso_total = sum([peso for resposta in respostas.values() if isinstance(resposta, tuple) and isinstance(resposta[1], int) for _, peso in [resposta]])
    pontuacao_ajustada = pontuacao + peso_total

    st.write(f"Pontuação Ajustada: **{pontuacao_ajustada}**")

    # Ajustando o cálculo do rank para considerar a proximidade com os valores de cada rank
    rank_valores = {"Rank D": 1, "Rank C": 2, "Rank B": 3, "Rank A": 4, "Rank S": 5}
    rank_proximidade = {rank: abs(pontuacao - valor) for rank, valor in rank_valores.items()}
    classificacao = min(rank_proximidade, key=rank_proximidade.get)

    st.write(f"Classificação Final: **{classificacao}**")

    resultado_df = pd.DataFrame({"Pergunta": list(respostas.keys()), "Resposta": [str(r) for r in respostas.values()]})
    resultado_df.loc[len(resultado_df.index)] = ["Pontuação Total", pontuacao]
    resultado_df.loc[len(resultado_df.index)] = ["Classificação", classificacao]

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        resultado_df.to_excel(writer, index=False, sheet_name="Resultado")
        writer.close()  # Removendo o uso do método 'save', pois não é necessário.
        st.download_button(
            label="⬇️ Baixar Resultado em Excel",
            data=buffer,
            file_name="resultado_prospect.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Código principal
configurar_estilo()
st.title("Análise de Prospect Comercial")
st.markdown("Preencha as informações abaixo para avaliar o prospect.")

perguntas = [
    "Quantas lojas?",
    "Quantas máquinas?",
    "Infraestrutura adequada? (Parque das máquinas)",
    "Replicação?",
    "Enquadramento, Lucro Real ou Presumido?",
    "Venda para fora da UF em grande volume?",
    "Financeiro Plus?",
    "Atualmente possui um E-Commerce?",
    "Loja Nova ou Importação?",
    "Se importação, temos importador?",
    "Mais de uma loja com bancos diferentes?",
    "Motivo da troca de sistema?",
    "O projeto possui um responsável por parte da farmácia, engajado e ciente que sua participação será necessária para o sucesso do projeto?",
    "Alguma particularidade que considere incomum?",
    "Qual sistema do cliente a ser migrado?"
]

respostas = {}

with st.form("form_prospect"):
    for pergunta in perguntas:
        if pergunta in ["Quantas lojas?", "Quantas máquinas?"]:
            resposta = st.number_input(pergunta, min_value=0, step=1, key=pergunta)
        elif pergunta == "Alguma particularidade que considere incomum?":
            col1, col2 = st.columns([3, 1])
            with col1:
                texto = st.text_input("Descreva:", key="descricao_particularidade")
            with col2:
                peso = st.slider("Peso (1 a 5):", 1, 5, key="peso_particularidade")
            resposta = (texto, peso)
        elif pergunta == "Motivo da troca de sistema?":
            resposta = st.selectbox(pergunta, ["", "Preço", "Sistema mais fácil de utilizar", "Sistema mais complexo com mais recursos", "Suporte", "Desentendimento com sistema anterior"], key=pergunta)
        elif pergunta == "Loja Nova ou Importação?":
            resposta = st.selectbox(pergunta, ["", "Importação", "Nova Loja"], key=pergunta)
            if resposta == "Importação":
                st.warning("Não Importa! Contas a Pagar, Movimentação, P344 (Controlados) e Produtos do Crediário")
        elif pergunta == "Qual sistema do cliente a ser migrado?":
            resposta = st.selectbox(pergunta, ["", "Trier", "Digifarma", "Inovafarma", "BIG", "Softpharma", "Automatiza", "Alpha7"], key=pergunta)
        else:
            resposta = st.selectbox(pergunta, ["", "Sim", "Não"], key=pergunta)
        respostas[pergunta] = resposta
    enviado = st.form_submit_button("Avaliar Prospect")

if enviado:
    pontuacao = calcular_pontuacao(respostas)
    exibir_resultado(pontuacao, respostas)
