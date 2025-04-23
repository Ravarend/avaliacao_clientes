import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF

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

def calcular_pontuacao(respostas, peso_padrao=3):
    """Calcula a pontuação com base nas respostas fornecidas."""
    pontuacao = 0
    lojas = respostas.get("Quantas lojas?", 0)

    for pergunta, resposta in respostas.items():
        if pergunta == "Quantas lojas?":
            if resposta == 1:
                pontuacao += 1
            elif 2 <= resposta <= 5:
                pontuacao += 4
            elif resposta > 5:
                pontuacao += 5
        elif pergunta == "Quantas máquinas?":
            if 1 <= resposta <= 3:
                pontuacao += 1
            elif 4 <= resposta <= 7:
                pontuacao += 2
            elif 8 <= resposta <= 16:
                pontuacao += 4
            elif 17 <= resposta <= 100:
                pontuacao += 5
        elif pergunta == "Replicação?":
            if resposta == "Sim":
                pontuacao += 3 if lojas <= 2 else 4
            else:
                pontuacao += 1
        elif pergunta == "Qual o enquadramento tributário?":
            if resposta == "Simples Nacional":
                pontuacao += 1
            elif resposta == "Lucro Real ou Presumido":
                pontuacao += 3
            else:
                continue  # Garantir que a lógica não tente incrementar pontuação sem resposta válida
        elif pergunta == "Venda para fora da UF em grande volume?":
            if resposta == "Sim":
                pontuacao += 5
        elif pergunta == "O prospect, já utiliza efetivamente em seu sistema atual, rotinas financeiras? (Conferência de caixa, consiliações bancárias, DRE, etc..)":
            pontuacao += 4 if resposta == "Sim" else 1
        elif pergunta == "Atualmente possui um E-Commerce?":
            if resposta == "Sim":
                venda_uf = respostas.get("Venda para fora da UF em grande volume?", "Não")
                pontuacao += 5 if venda_uf == "Sim" else 3
        elif pergunta == "Loja Nova ou Importação?":
            if resposta == "Importação":
                pontuacao += 3
            elif resposta == "Nova Loja":
                pontuacao += 1
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
        elif pergunta == "O projeto possui um responsável por parte da farmácia, engajado e ciente que sua participação será necessária para o sucesso do projeto?":
            pontuacao += 1 if resposta == "Sim" else 4
        elif pergunta == "Alguma particularidade que considere incomum e impeditiva para o sucesso do projeto?":
            if isinstance(resposta, tuple):
                texto, peso = resposta
                pontuacao += peso if 1 <= peso <= 5 else 0
        elif pergunta == "Qual o sistema atual do cliente a ser migrado?":
            if resposta == "Magno System":
                pontuacao += 2
            elif resposta == "Trier":
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
        elif pergunta == "Possui manipulação?":
            if resposta == "Sim":
                if respostas.get("Quantas lojas?", 0) == 1:
                    if respostas.get("Loja Nova ou Importação?") == "Nova Loja":
                        pontuacao += 3
                    elif respostas.get("Loja Nova ou Importação?") == "Importação":
                        pontuacao += 4
                elif respostas.get("Quantas lojas?", 0) >= 2:
                    pontuacao += 5
        elif isinstance(resposta, int) or isinstance(resposta, float):
            if resposta > 0:
                pontuacao += peso_padrao
        elif resposta == "Sim":
            pontuacao += peso_padrao

    return pontuacao

def exibir_resultado(pontuacao, respostas):
    """Exibe o resultado da avaliação e permite download do PDF."""
    st.subheader("Resultado da Avaliação")

    # Calcular a classificação com base na pontuação média
    perguntas_respondidas = len([resposta for resposta in respostas.values() if resposta not in ["", "Não"]])
    media_pontuacao = pontuacao / perguntas_respondidas if perguntas_respondidas > 0 else 0

    if media_pontuacao >= 4.5:
        classificacao = "Rank S"
    elif media_pontuacao >= 3.5:
        classificacao = "Rank A"
    elif media_pontuacao >= 2.5:
        classificacao = "Rank B"
    elif media_pontuacao >= 1.5:
        classificacao = "Rank C"
    else:
        classificacao = "Rank D"

    st.write(f"Classificação Final: **{classificacao}**")

    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'Resultado da Avaliação de Prospect', 0, 1, 'C')

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    # Classificação Final com fonte 20 e cor centralizada no início do PDF
    pdf.set_font('Arial', 'B', 20)
    if classificacao == "Rank S":
        pdf.set_text_color(128, 0, 128)  # Roxo
    elif classificacao == "Rank A":
        pdf.set_text_color(255, 0, 0)  # Vermelho
    elif classificacao == "Rank B":
        pdf.set_text_color(0, 0, 255)  # Azul
    elif classificacao == "Rank C":
        pdf.set_text_color(255, 255, 0)  # Amarelo
    elif classificacao == "Rank D":
        pdf.set_text_color(0, 255, 0)  # Verde

    pdf.cell(0, 20, f'Classificação Final: {classificacao}', 0, 1, 'C')  # Centralizar o texto
    pdf.set_text_color(0, 0, 0)  # Resetar a cor do texto para preto

    # Adicionar o título e as perguntas após a classificação final
    pdf.cell(0, 10, '', 0, 1)  # Linha em branco
    pdf.set_font('Arial', 'B', 16)  # Aumentar a fonte para 16
    pdf.cell(0, 10, 'Cuidados em relação ao Prospect:', 0, 1)

    pdf.set_font('Arial', '', 12)  # Redefinir a fonte para o conteúdo

    # Adicionar perguntas em negrito e mensagens numeradas ao PDF
    numero = 1
    if respostas.get("Replicação?") == "Sim":
        pdf.set_font('Arial', 'B', 12)  # Pergunta em negrito
        pdf.multi_cell(0, 10, f"{numero}. Replicação?")
        pdf.set_font('Arial', '', 12)  # Mensagem normal
        pdf.multi_cell(0, 10, "No HOS, as operações serão centralizadas na Matriz. As filiais ficarão responsáveis apenas pelo cadastro de clientes, enquanto as demais atividades (como cadastro de produtos, entrada de notas, etc.) serão realizadas exclusivamente pela Matriz.")
        numero += 1

    if respostas.get("Qual o enquadramento tributário?") == "Lucro Real ou Presumido" and respostas.get("Loja Nova ou Importação?") == "Importação":
        pdf.set_font('Arial', 'B', 12)
        pdf.multi_cell(0, 10, f"{numero}. Qual o enquadramento tributário?")
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, "Como o cliente gera o SPED, será necessário que a contabilidade do cliente consolide os arquivos, ou que a virada para o novo sistema ocorra no dia 1º de um mês.")
        numero += 1

    if respostas.get("Venda para fora da UF em grande volume?") == "Sim":
        pdf.set_font('Arial', 'B', 12)
        pdf.multi_cell(0, 10, f"{numero}. Venda para fora da UF em grande volume?")
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, "A questão da configuração de tributação torna-se complexa.")
        numero += 1

    if respostas.get("Atualmente possui um E-Commerce?") == "Sim":
        pdf.set_font('Arial', 'B', 12)
        pdf.multi_cell(0, 10, f"{numero}. Atualmente possui um E-Commerce?")
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, "Caso deseje integrar com nossa API, será necessário que o fornecedor atual do e-commerce realize o desenvolvimento, ou que o cliente opte por adquirir o nosso E-Commerce.")
        numero += 1

    if respostas.get("Loja Nova ou Importação?") == "Loja Nova":
        pdf.set_font('Arial', 'B', 12)
        pdf.multi_cell(0, 10, f"{numero}. Loja Nova ou Importação?")
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, "O cliente deve estar ciente de que haverá uma carga significativa de trabalho envolvida por parte dele.")
        numero += 1
    elif respostas.get("Loja Nova ou Importação?") == "Importação":
        if respostas.get("Quantas lojas?") > 1:
            pdf.set_font('Arial', 'B', 12)
            pdf.multi_cell(0, 10, f"{numero}. Loja Nova ou Importação?")
            pdf.set_font('Arial', '', 12)
            pdf.multi_cell(0, 10, "Trata-se de um processo delicado, que exige homologação. Isso pode levar tempo e deve ser feito com cautela, sem pressa. Importante, só será realizada importação de um BD, necessário escolher qual a loja que terá os dados importados, as outras lojas não será importado nenhuma informação.")
        else:
            pdf.set_font('Arial', 'B', 12)
            pdf.multi_cell(0, 10, f"{numero}. Loja Nova ou Importação?")
            pdf.set_font('Arial', '', 12)
            pdf.multi_cell(0, 10, "Trata-se de um processo delicado, que exige homologação. Isso pode levar tempo e deve ser feito com cautela, sem pressa.")
        numero += 1

    pdf.set_font('Arial', 'B', 12)
    pdf.multi_cell(0, 10, f"{numero}. O projeto possui um responsável por parte da farmácia, engajado e ciente que sua participação será necessária para o sucesso do projeto?")
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, "Essa qualificadora é fundamental para o sucesso do projeto. A presença de sócios ocultos, stakeholders desinteressados ou distantes da operação aumenta significativamente o risco de falhas na implantação.")

    pdf_output = BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin1'))  # Gerar o PDF como string codificada em latin1
    pdf_output.seek(0)

    return pdf_output

# Código principal
configurar_estilo()
st.title("Análise de Prospect Comercial")
st.markdown("Preencha as informações abaixo para avaliar o prospect.")

# Removendo a pergunta "Mais de uma loja com bancos diferentes?"
# Removendo a pergunta "Se importação, temos importador?"
perguntas = [
    "Quantas lojas?",
    "Quantas máquinas?",
    "Replicação?",
    "Qual o enquadramento tributário?",
    "Loja Nova ou Importação?",
    "Qual o sistema atual do cliente a ser migrado?",
    "O prospect, já utiliza efetivamente em seu sistema atual, rotinas financeiras? (Conferência de caixa, consiliações bancárias, DRE, etc..)",
    "Venda para fora da UF em grande volume?",
    "Atualmente possui um E-Commerce?",
    "Motivo da troca de sistema?",
    "O projeto possui um responsável por parte da farmácia, engajado e ciente que sua participação será necessária para o sucesso do projeto?",
    "Alguma particularidade que considere incomum e impeditiva para o sucesso do projeto?",
    "Possui manipulação?",
]

respostas = {}

with st.form("form_prospect"):
    pontuacao = 0  # Inicialização da variável
    for pergunta in perguntas:
        if pergunta in ["Quantas lojas?", "Quantas máquinas?"]:
            resposta = st.number_input(pergunta, min_value=0, step=1, key=pergunta)
        elif pergunta == "Alguma particularidade que considere incomum e impeditiva para o sucesso do projeto?":
            col1, col2 = st.columns([3, 1])
            with col1:
                texto = st.text_input("Alguma particularidade que considere incomum e impeditiva para o sucesso do projeto?", key="descricao_particularidade")
            with col2:
                peso = st.selectbox("Peso (1 a 5) ou Nenhum:", ["Nenhum", 1, 2, 3, 4, 5], key="peso_particularidade")
            resposta = (texto, peso)

            # Adicionando a resposta ao dicionário mesmo que "Nenhum" seja selecionado
            respostas[pergunta] = resposta

            # Ignorar a pergunta no cálculo se "Nenhum" for selecionado
            if peso == "Nenhum":
                respostas[pergunta] = None
                continue
        elif pergunta == "Motivo da troca de sistema?":
            resposta = st.selectbox(pergunta, ["", "Preço", "Sistema mais fácil de utilizar", "Sistema mais complexo com mais recursos", "Suporte", "Desentendimento com sistema anterior"], key=pergunta)
        elif pergunta == "Loja Nova ou Importação?":
            resposta = st.selectbox(pergunta, ["", "Importação", "Nova Loja"], key=pergunta)
            if resposta == "Importação":
                st.warning("Não Importa! Contas a Pagar, Movimentação, P344 (Controlados) e Produtos do Crediário")
        elif pergunta == "Qual o sistema atual do cliente a ser migrado?":
            resposta = st.selectbox(pergunta, ["", "Magno System", "Trier", "Digifarma", "Inovafarma", "BIG", "Softpharma", "Automatiza", "Alpha7"], key=pergunta)
        elif pergunta == "Qual o enquadramento tributário?":
            resposta = st.selectbox(pergunta, ["", "Simples Nacional", "Lucro Real ou Presumido"], key=pergunta)
            if resposta == "Simples Nacional":
                pontuacao += 1
            elif resposta == "Lucro Real ou Presumido":
                pontuacao += 3
            else:
                continue  # Garantir que a lógica não tente incrementar pontuação sem resposta válida
        else:
            resposta = st.selectbox(pergunta, ["", "Sim", "Não"], key=pergunta)

        if resposta == "" and pergunta not in ["Alguma particularidade que considere incomum e impeditiva para o sucesso do projeto?"]:
            continue  # Removendo a mensagem de erro, mas mantendo a obrigatoriedade

        respostas[pergunta] = resposta
    enviado = st.form_submit_button("Enviar")

if enviado:
    pontuacao = calcular_pontuacao(respostas)
    pdf_output = exibir_resultado(pontuacao, respostas)

    # Adicionar o botão de download fora do formulário e garantir que ele permaneça visível
    if pdf_output:
        st.download_button(
            label="⬇️ Baixar Resultado em PDF",
            data=pdf_output,
            file_name="resultado_prospect.pdf",
            mime="application/pdf",
            key="download_pdf"
        )

    # Remover o uso de st.experimental_rerun e ajustar a lógica para limpar os campos
    if enviado:
        respostas.clear()  # Limpar o dicionário de respostas diretamente
        st.success("Formulário enviado com sucesso! Você pode preencher novamente se desejar.")
