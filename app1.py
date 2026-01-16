import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# Configuração da página
st.set_page_config(
    page_title="Tire Management - Motorsport",
    page_icon="🏁",
    layout="wide"
)

# Função para carregar dados do Excel
@st.cache_data
def load_data(file):
    df_cadastro = pd.read_excel(file, sheet_name='Cadastro de Pneus')
    df_medicoes = pd.read_excel(file, sheet_name='Medições')
    return df_cadastro, df_medicoes

# Função para salvar dados em Excel
def save_to_excel(df_cadastro, df_medicoes):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_cadastro.to_excel(writer, sheet_name='Cadastro de Pneus', index=False)
        df_medicoes.to_excel(writer, sheet_name='Medições', index=False)
    return output.getvalue()

# Inicialização dos dados na sessão
if 'df_cadastro' not in st.session_state:
    st.session_state.df_cadastro = pd.DataFrame(columns=[
        'Nome do Pneu', 'Código de Barras', 'Carro Vinculado', 'Status',
        'Quilometragem atual', 'Profundidade Inicial (mm)', 'Limite KM', 
        'Data Cadastro', 'Etapa Cadastro', 'Etapa Atual', 'Status Etapa'
    ])
    st.session_state.df_medicoes = pd.DataFrame(columns=[
        'Código do Pneu', 'Quilometragem Atual', 'Código de Barras', 'Carro',
        'Data Medição', 'Tipo Evento', 'Voltas', 'Tempo Pista (min)', 'Pista',
        'Quilometragem', 'KM TOTAL', 'Interno (mm)', 'Centro Interno (mm)',
        'Centro Externo (mm)', 'Externo (mm)', 'Profundidade Média (mm)',
        'Condição (twi)', 'Condição (km)', 'AÇÃO', 'Etapa'
    ])

# Inicializar cadastro de pistas se não existir
if 'df_pistas' not in st.session_state:
    st.session_state.df_pistas = pd.DataFrame({
        'Nome': ['Circuito dos Cristais', 'Autódromo Zilmar Beux', 'Interlagos', 
                 'Autódromo Ayrton Senna', 'Autódromo de Cuiabá', 'Velocitta',
                 'Autódromo de Chapecó', 'Autódromo Nelson Piquet', 'Velopark'],
        'KM por Volta': [3.477, 3.115, 4.309, 3.835, 3.408, 3.493, 3.762, 5.476, 3.013],
        'Localização': ['Curvelo-MG', 'Cascavel-PR', 'São Paulo-SP', 'Goiânia-GO', 
                       'Cuiabá-MT', 'Mogi Guaçu-SP', 'Chapecó-SC', 'Brasília-DF', 'Nova Santa Rita-RS']
    })

# Inicializar cadastro de carros se não existir
if 'df_carros' not in st.session_state:
    st.session_state.df_carros = pd.DataFrame({
        'Nome': ['Carro A', 'Carro B', 'Carro C'],
        'Número': ['#11', '#22', '#33'],
        'Piloto': ['Piloto 1', 'Piloto 2', 'Piloto 3'],
        'Categoria': ['Stock Car', 'Stock Car', 'Stock Car'],
        'Status': ['Ativo', 'Ativo', 'Ativo'],
        'Data Cadastro': [datetime.now().strftime('%d/%m/%Y')] * 3
    })

# Inicializar calendário Stock Car Pro Series 2026
if 'df_calendario' not in st.session_state:
    st.session_state.df_calendario = pd.DataFrame({
        'Etapa': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        'Data': ['08/03/2026', '29/03/2026', '26/04/2026', '17/05/2026', '13/06/2026',
                 '26/07/2026', '09/08/2026', '06/09/2026', '27/09/2026', '18/10/2026',
                 '15/11/2026', '13/12/2026'],
        'Local': ['Curvelo', 'Cascavel', 'Interlagos', 'Goiânia', 'Cuiabá',
                  'Velocitta', 'Cascavel', 'Chapecó', 'Brasília', 'Goiânia',
                  'Velopark', 'Interlagos'],
        'Pista': ['Circuito dos Cristais', 'Autódromo Zilmar Beux', 'Interlagos',
                  'Autódromo Ayrton Senna', 'Autódromo de Cuiabá', 'Velocitta',
                  'Autódromo Zilmar Beux', 'Autódromo de Chapecó', 'Autódromo Nelson Piquet',
                  'Autódromo Ayrton Senna', 'Velopark', 'Interlagos'],
        'Tipo': ['Abertura', 'Regular', 'Regular', 'Regular', 'Noturna',
                 'Regular', 'Regular', 'Estreia Chapecó', 'Corrida do Milhão', 'Endurance 3h',
                 'Regular', 'Super Final'],
        'Status': ['Não Iniciada'] * 12
    })

# Gerenciar etapa atual
if 'etapa_atual' not in st.session_state:
    st.session_state.etapa_atual = 1  # Primeira etapa

# Histórico de etapas
if 'historico_etapas' not in st.session_state:
    st.session_state.historico_etapas = pd.DataFrame(columns=[
        'Etapa', 'Data Inicio', 'Data Fim', 'Pneus Comprados', 'Pneus Selecionados Proxima',
        'Pneus Descartados', 'Status'
    ])

# Título principal
st.title("🏁 Tire Management - Stock Car Pro Series 2026")

# Mostrar etapa atual no topo
col_header1, col_header2, col_header3 = st.columns([2, 2, 1])
with col_header1:
    etapa_info = st.session_state.df_calendario[
        st.session_state.df_calendario['Etapa'] == st.session_state.etapa_atual
    ].iloc[0]
    st.markdown(f"### 📍 Etapa Atual: **{st.session_state.etapa_atual}** - {etapa_info['Local']}")
with col_header2:
    st.markdown(f"### 📅 Data: **{etapa_info['Data']}**")
with col_header3:
    st.markdown(f"### 🏆 **{etapa_info['Tipo']}**")

st.markdown("---")

# Sidebar para navegação
menu = st.sidebar.selectbox(
    "Menu Principal",
    ["📊 Dashboard", "🏁 Gerenciar Etapas", "🛒 Comprar Pneus", "🏎️ Gerenciar Carros", 
     "📏 Registrar Medição", "📋 Visualizar Dados", "🔧 Montagem de Sets", 
     "🏆 Gerenciar Pistas", "📜 Histórico", "📤 Importar/Exportar"]
)

# DASHBOARD
if menu == "📊 Dashboard":
    st.header("Dashboard - Visão Geral da Etapa")

    # Filtrar pneus da etapa atual
    pneus_etapa = st.session_state.df_cadastro[
        st.session_state.df_cadastro['Etapa Atual'] == st.session_state.etapa_atual
    ]

    if len(pneus_etapa) > 0:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Pneus Nesta Etapa", len(pneus_etapa))
        with col2:
            pneus_novos = len(pneus_etapa[pneus_etapa['Status'] == 'Novo'])
            st.metric("Pneus Novos", pneus_novos)
        with col3:
            pneus_usados = len(pneus_etapa[pneus_etapa['Status'] == 'Usado'])
            st.metric("Pneus Usados", pneus_usados)
        with col4:
            pneus_disponiveis = len(pneus_etapa[pneus_etapa['Status Etapa'] == 'Disponível'])
            st.metric("Disponíveis", pneus_disponiveis)

        st.markdown("---")

        # Gráficos
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Pneus por Carro")
            if len(pneus_etapa) > 0:
                fig = px.bar(
                    pneus_etapa.groupby(['Carro Vinculado', 'Status']).size().reset_index(name='Count'),
                    x='Carro Vinculado', y='Count', color='Status',
                    title="Distribuição de Pneus na Etapa"
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Status dos Pneus")
            status_count = pneus_etapa['Status Etapa'].value_counts()
            fig = px.pie(
                values=status_count.values,
                names=status_count.index,
                title="Status na Etapa"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Tabela de pneus da etapa
        st.subheader(f"📋 Pneus na Etapa {st.session_state.etapa_atual}")
        st.dataframe(pneus_etapa, use_container_width=True)

    else:
        st.info(f"📂 Nenhum pneu cadastrado para a Etapa {st.session_state.etapa_atual}. Vá para 'Comprar Pneus'.")

# GERENCIAR ETAPAS
elif menu == "🏁 Gerenciar Etapas":
    st.header("Gerenciar Etapas - Stock Car Pro Series 2026")

    tab1, tab2, tab3 = st.tabs(["📅 Calendário", "🎯 Avançar Etapa", "📜 Histórico de Etapas"])

    with tab1:
        st.subheader("Calendário Completo 2026")

        # Destacar etapa atual
        df_display = st.session_state.df_calendario.copy()

        def highlight_current(row):
            if row['Etapa'] == st.session_state.etapa_atual:
                return ['background-color: #90EE90'] * len(row)
            elif row['Status'] == 'Concluída':
                return ['background-color: #D3D3D3'] * len(row)
            else:
                return [''] * len(row)

        st.dataframe(
            df_display.style.apply(highlight_current, axis=1),
            use_container_width=True
        )

        st.info(f"🟢 Etapa atual em verde: Etapa {st.session_state.etapa_atual}")

    with tab2:
        st.subheader(f"Finalizar Etapa {st.session_state.etapa_atual} e Avançar")

        etapa_atual_info = st.session_state.df_calendario[
            st.session_state.df_calendario['Etapa'] == st.session_state.etapa_atual
        ].iloc[0]

        st.markdown(f"### Etapa {st.session_state.etapa_atual}: {etapa_atual_info['Local']} - {etapa_atual_info['Data']}")

        # Verificar se é a última etapa
        if st.session_state.etapa_atual >= 12:
            st.success("🏆 Você está na última etapa da temporada!")
            st.info("Não há próxima etapa para avançar.")
        else:
            # Mostrar próxima etapa
            proxima_etapa = st.session_state.etapa_atual + 1
            proxima_info = st.session_state.df_calendario[
                st.session_state.df_calendario['Etapa'] == proxima_etapa
            ].iloc[0]

            st.markdown("---")
            st.markdown(f"### 📍 Próxima Etapa: **{proxima_etapa}** - {proxima_info['Local']}")
            st.markdown(f"**Data:** {proxima_info['Data']} | **Tipo:** {proxima_info['Tipo']}")

            st.markdown("---")
            st.markdown("### Selecionar 4 Pneus para a Próxima Etapa")
            st.info("⚠️ Regulamento: Você deve selecionar exatamente 4 pneus para levar à próxima etapa.")

            # Filtrar pneus disponíveis na etapa atual
            pneus_disponiveis = st.session_state.df_cadastro[
                (st.session_state.df_cadastro['Etapa Atual'] == st.session_state.etapa_atual) &
                (st.session_state.df_cadastro['Status Etapa'].isin(['Disponível', 'Em uso']))
            ]

            if len(pneus_disponiveis) >= 4:
                pneus_selecionados = st.multiselect(
                    "Selecione 4 pneus para a próxima etapa:",
                    options=pneus_disponiveis['Nome do Pneu'].tolist(),
                    help="Escolha exatamente 4 pneus"
                )

                if len(pneus_selecionados) > 0:
                    st.markdown(f"**Pneus selecionados: {len(pneus_selecionados)}/4**")

                    # Mostrar detalhes dos pneus selecionados
                    df_selecionados = pneus_disponiveis[
                        pneus_disponiveis['Nome do Pneu'].isin(pneus_selecionados)
                    ]
                    st.dataframe(df_selecionados[['Nome do Pneu', 'Carro Vinculado', 'Quilometragem atual', 'Status']], 
                                use_container_width=True)

                st.markdown("---")

                if len(pneus_selecionados) == 4:
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.success("✅ 4 pneus selecionados! Você pode avançar para a próxima etapa.")

                    with col2:
                        if st.button("🏁 AVANÇAR PARA PRÓXIMA ETAPA", type="primary", use_container_width=True):
                            # Registrar no histórico
                            pneus_nao_selecionados = pneus_disponiveis[
                                ~pneus_disponiveis['Nome do Pneu'].isin(pneus_selecionados)
                            ]

                            novo_historico = pd.DataFrame([{
                                'Etapa': st.session_state.etapa_atual,
                                'Data Inicio': etapa_atual_info['Data'],
                                'Data Fim': datetime.now().strftime('%d/%m/%Y'),
                                'Pneus Comprados': len(st.session_state.df_cadastro[
                                    st.session_state.df_cadastro['Etapa Cadastro'] == st.session_state.etapa_atual
                                ]),
                                'Pneus Selecionados Proxima': ', '.join(pneus_selecionados),
                                'Pneus Descartados': len(pneus_nao_selecionados),
                                'Status': 'Concluída'
                            }])

                            st.session_state.historico_etapas = pd.concat(
                                [st.session_state.historico_etapas, novo_historico],
                                ignore_index=True
                            )

                            # Atualizar status dos pneus selecionados
                            st.session_state.df_cadastro.loc[
                                st.session_state.df_cadastro['Nome do Pneu'].isin(pneus_selecionados),
                                ['Etapa Atual', 'Status Etapa', 'Status']
                            ] = [proxima_etapa, 'Disponível', 'Usado']

                            # Marcar pneus não selecionados como descartados
                            st.session_state.df_cadastro.loc[
                                (~st.session_state.df_cadastro['Nome do Pneu'].isin(pneus_selecionados)) &
                                (st.session_state.df_cadastro['Etapa Atual'] == st.session_state.etapa_atual),
                                'Status Etapa'
                            ] = 'Descartado'

                            # Atualizar status da etapa no calendário
                            st.session_state.df_calendario.loc[
                                st.session_state.df_calendario['Etapa'] == st.session_state.etapa_atual,
                                'Status'
                            ] = 'Concluída'

                            # Avançar etapa
                            st.session_state.etapa_atual = proxima_etapa

                            st.success(f"✅ Avançado para Etapa {proxima_etapa}!")
                            st.balloons()
                            st.rerun()
                else:
                    st.warning(f"⚠️ Selecione exatamente 4 pneus. Você selecionou {len(pneus_selecionados)}.")
            else:
                st.error(f"⚠️ Pneus insuficientes! Você tem {len(pneus_disponiveis)} pneu(s) disponível(is). Necessário: 4 pneus.")

    with tab3:
        st.subheader("Histórico de Etapas Concluídas")

        if len(st.session_state.historico_etapas) > 0:
            st.dataframe(st.session_state.historico_etapas, use_container_width=True)

            # Detalhes de cada etapa
            st.markdown("### Detalhes por Etapa")
            for idx, etapa_hist in st.session_state.historico_etapas.iterrows():
                with st.expander(f"Etapa {etapa_hist['Etapa']} - {etapa_hist['Data Inicio']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Pneus Comprados", etapa_hist['Pneus Comprados'])
                    with col2:
                        st.metric("Pneus Descartados", etapa_hist['Pneus Descartados'])
                    with col3:
                        st.metric("Status", etapa_hist['Status'])

                    st.markdown("**Pneus Selecionados para Próxima Etapa:**")
                    st.info(etapa_hist['Pneus Selecionados Proxima'])
        else:
            st.info("Nenhuma etapa concluída ainda.")

# COMPRAR PNEUS
elif menu == "🛒 Comprar Pneus":
    st.header("Comprar Pneus para a Etapa")

    etapa_info = st.session_state.df_calendario[
        st.session_state.df_calendario['Etapa'] == st.session_state.etapa_atual
    ].iloc[0]

    st.markdown(f"### Etapa {st.session_state.etapa_atual}: {etapa_info['Local']} - {etapa_info['Data']}")

    # Determinar limite de compra
    if st.session_state.etapa_atual == 1:
        limite_compra = 16
        st.info("🎯 **Primeira Etapa**: Você pode comprar até **16 pneus**")
    else:
        limite_compra = 8
        st.info("🎯 **Etapas seguintes**: Você pode comprar até **8 pneus novos**")

    # Contar pneus já comprados nesta etapa
    pneus_comprados_etapa = len(st.session_state.df_cadastro[
        st.session_state.df_cadastro['Etapa Cadastro'] == st.session_state.etapa_atual
    ])

    # Contar pneus vindos da etapa anterior
    pneus_anteriores = len(st.session_state.df_cadastro[
        (st.session_state.df_cadastro['Etapa Atual'] == st.session_state.etapa_atual) &
        (st.session_state.df_cadastro['Etapa Cadastro'] != st.session_state.etapa_atual)
    ])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Pneus já comprados nesta etapa", pneus_comprados_etapa)
    with col2:
        st.metric("Pneus da etapa anterior", pneus_anteriores)
    with col3:
        restante = limite_compra - pneus_comprados_etapa
        st.metric("Pneus disponíveis para compra", restante)

    st.markdown("---")

    if pneus_comprados_etapa >= limite_compra:
        st.warning(f"⚠️ Você já atingiu o limite de {limite_compra} pneus para esta etapa!")
    else:
        st.subheader("Cadastrar Novos Pneus")

        # Quantos pneus cadastrar
        qtd_pneus = st.number_input(
            f"Quantos pneus deseja cadastrar? (Máximo: {limite_compra - pneus_comprados_etapa})",
            min_value=1,
            max_value=limite_compra - pneus_comprados_etapa,
            value=1
        )

        with st.form("comprar_pneus_form"):
            st.markdown(f"### Cadastrar {qtd_pneus} pneu(s)")

            # Selecionar carro
            if len(st.session_state.df_carros) == 0:
                st.error("⚠️ Cadastre carros antes de comprar pneus!")
                st.stop()

            carro_selecionado = st.selectbox(
                "Carro Vinculado",
                options=st.session_state.df_carros[st.session_state.df_carros['Status'] == 'Ativo']['Nome'].tolist()
            )

            col1, col2 = st.columns(2)
            with col1:
                prefixo = st.text_input("Prefixo dos Pneus", value=f"P{st.session_state.etapa_atual}")
                prof_inicial = st.number_input("Profundidade Inicial (mm)", min_value=0.0, value=8.0, step=0.1)

            with col2:
                inicio_numeracao = st.number_input("Número Inicial", min_value=1, value=1)
                limite_km = st.number_input("Limite KM", min_value=0, value=1000)

            submitted = st.form_submit_button(f"✅ Comprar {qtd_pneus} Pneus", use_container_width=True)

            if submitted:
                novos_pneus = []
                data_cadastro = datetime.now().strftime('%d/%m/%Y')

                for i in range(qtd_pneus):
                    nome_pneu = f"{prefixo}{inicio_numeracao + i:03d}"
                    codigo_barras = int(f"{st.session_state.etapa_atual}{inicio_numeracao + i:05d}")

                    novo_pneu = {
                        'Nome do Pneu': nome_pneu,
                        'Código de Barras': codigo_barras,
                        'Carro Vinculado': carro_selecionado,
                        'Status': 'Novo',
                        'Quilometragem atual': 0,
                        'Profundidade Inicial (mm)': prof_inicial,
                        'Limite KM': limite_km,
                        'Data Cadastro': data_cadastro,
                        'Etapa Cadastro': st.session_state.etapa_atual,
                        'Etapa Atual': st.session_state.etapa_atual,
                        'Status Etapa': 'Disponível'
                    }
                    novos_pneus.append(novo_pneu)

                df_novos = pd.DataFrame(novos_pneus)
                st.session_state.df_cadastro = pd.concat(
                    [st.session_state.df_cadastro, df_novos],
                    ignore_index=True
                )

                st.success(f"✅ {qtd_pneus} pneu(s) comprado(s) com sucesso!")
                st.balloons()
                st.rerun()

# GERENCIAR CARROS
elif menu == "🏎️ Gerenciar Carros":
    st.header("Gerenciar Carros")

    tab1, tab2 = st.tabs(["📋 Carros Cadastrados", "➕ Adicionar Novo Carro"])

    with tab1:
        st.subheader("Carros Cadastrados")

        if len(st.session_state.df_carros) > 0:
            st.dataframe(st.session_state.df_carros, use_container_width=True)

            st.markdown("---")
            st.markdown("### Editar ou Remover Carro")

            carro_selecionado = st.selectbox(
                "Selecionar Carro",
                options=st.session_state.df_carros['Nome'].tolist()
            )

            if carro_selecionado:
                carro_info = st.session_state.df_carros[
                    st.session_state.df_carros['Nome'] == carro_selecionado
                ].iloc[0]

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### Informações Atuais")
                    st.info(f"**Nome:** {carro_info['Nome']}")
                    st.info(f"**Número:** {carro_info['Número']}")
                    st.info(f"**Piloto:** {carro_info['Piloto']}")
                    st.info(f"**Categoria:** {carro_info['Categoria']}")
                    st.info(f"**Status:** {carro_info['Status']}")

                with col2:
                    st.markdown("#### Editar")
                    with st.form("editar_carro"):
                        novo_numero = st.text_input("Número do Carro", value=carro_info['Número'])
                        novo_piloto = st.text_input("Nome do Piloto", value=carro_info['Piloto'])
                        nova_categoria = st.selectbox(
                            "Categoria",
                            options=["Stock Car", "Stock Car Pro", "Stock Series", "Turismo", "Outro"],
                            index=["Stock Car", "Stock Car Pro", "Stock Series", "Turismo", "Outro"].index(carro_info['Categoria']) if carro_info['Categoria'] in ["Stock Car", "Stock Car Pro", "Stock Series", "Turismo", "Outro"] else 0
                        )
                        novo_status = st.selectbox(
                            "Status",
                            options=["Ativo", "Inativo", "Manutenção"],
                            index=["Ativo", "Inativo", "Manutenção"].index(carro_info['Status']) if carro_info['Status'] in ["Ativo", "Inativo", "Manutenção"] else 0
                        )

                        col_a, col_b = st.columns(2)
                        with col_a:
                            atualizar = st.form_submit_button("✅ Atualizar", use_container_width=True)
                        with col_b:
                            remover = st.form_submit_button("🗑️ Remover", type="secondary", use_container_width=True)

                        if atualizar:
                            st.session_state.df_carros.loc[
                                st.session_state.df_carros['Nome'] == carro_selecionado,
                                ['Número', 'Piloto', 'Categoria', 'Status']
                            ] = [novo_numero, novo_piloto, nova_categoria, novo_status]
                            st.success("Carro atualizado!")
                            st.rerun()

                        if remover:
                            pneus_vinculados = st.session_state.df_cadastro[
                                st.session_state.df_cadastro['Carro Vinculado'] == carro_selecionado
                            ]

                            if len(pneus_vinculados) > 0:
                                st.error(f"⚠️ Não é possível remover! Existem {len(pneus_vinculados)} pneu(s) vinculado(s) a este carro.")
                            else:
                                st.session_state.df_carros = st.session_state.df_carros[
                                    st.session_state.df_carros['Nome'] != carro_selecionado
                                ]
                                st.success("Carro removido!")
                                st.rerun()
        else:
            st.info("Nenhum carro cadastrado.")

    with tab2:
        st.subheader("Adicionar Novo Carro")

        with st.form("novo_carro"):
            col1, col2 = st.columns(2)

            with col1:
                nome_carro = st.text_input("Nome/Identificação do Carro", placeholder="Ex: Carro #11 - Equipe X")
                numero_carro = st.text_input("Número do Carro", placeholder="Ex: #11")
                piloto_carro = st.text_input("Nome do Piloto", placeholder="Ex: João Silva")

            with col2:
                categoria_carro = st.selectbox(
                    "Categoria",
                    options=["Stock Car", "Stock Car Pro", "Stock Series", "Turismo", "Outro"]
                )
                status_carro = st.selectbox(
                    "Status",
                    options=["Ativo", "Inativo", "Manutenção"]
                )

            submitted = st.form_submit_button("✅ Adicionar Carro", use_container_width=True)

            if submitted:
                if nome_carro and numero_carro and piloto_carro:
                    if nome_carro in st.session_state.df_carros['Nome'].values:
                        st.error("⚠️ Já existe um carro com este nome!")
                    else:
                        novo_carro = pd.DataFrame([{
                            'Nome': nome_carro,
                            'Número': numero_carro,
                            'Piloto': piloto_carro,
                            'Categoria': categoria_carro,
                            'Status': status_carro,
                            'Data Cadastro': datetime.now().strftime('%d/%m/%Y')
                        }])

                        st.session_state.df_carros = pd.concat(
                            [st.session_state.df_carros, novo_carro],
                            ignore_index=True
                        )
                        st.success(f"✅ Carro {nome_carro} adicionado!")
                        st.rerun()
                else:
                    st.error("⚠️ Preencha todos os campos obrigatórios!")

# REGISTRAR MEDIÇÃO
elif menu == "📏 Registrar Medição":
    st.header("Registrar Nova Medição")

    # Filtrar apenas pneus da etapa atual
    pneus_etapa_atual = st.session_state.df_cadastro[
        (st.session_state.df_cadastro['Etapa Atual'] == st.session_state.etapa_atual) &
        (st.session_state.df_cadastro['Status Etapa'] != 'Descartado')
    ]

    if len(pneus_etapa_atual) > 0:
        with st.form("medicao_form"):
            col1, col2 = st.columns(2)

            with col1:
                pneu_selecionado = st.selectbox(
                    "Código do Pneu",
                    pneus_etapa_atual['Nome do Pneu'].tolist()
                )

                pneu_info = st.session_state.df_cadastro[
                    st.session_state.df_cadastro['Nome do Pneu'] == pneu_selecionado
                ].iloc[0]

                carro = st.text_input("Carro", value=pneu_info['Carro Vinculado'], disabled=True)
                data_medicao = st.date_input("Data da Medição", value=datetime.now())

                tipo_evento = st.selectbox(
                    "Tipo de Evento", 
                    ["Treino 1", "Treino 2", "Treino 3", "Warm-up", 
                     "Q1", "Q2", "Q3", "Corrida 1", "Corrida 2"]
                )

                # Pista da etapa atual
                etapa_info = st.session_state.df_calendario[
                    st.session_state.df_calendario['Etapa'] == st.session_state.etapa_atual
                ].iloc[0]

                pista_nome = st.text_input("Pista", value=etapa_info['Pista'], disabled=True)

                if pista_nome in st.session_state.df_pistas['Nome'].values:
                    pista_info = st.session_state.df_pistas[
                        st.session_state.df_pistas['Nome'] == pista_nome
                    ].iloc[0]

                    st.info(f"📍 {pista_info['Localização']} | 🏁 {pista_info['KM por Volta']:.3f} km/volta")

                    voltas = st.number_input("Número de Voltas", min_value=0, value=0)
                    km_percorrido = voltas * pista_info['KM por Volta']
                    st.markdown(f"**Quilometragem Calculada:** {km_percorrido:.3f} km")
                else:
                    voltas = 0
                    km_percorrido = 0.0

                tempo_pista = st.number_input("Tempo na Pista (min)", min_value=0, value=0)

            with col2:
                st.subheader("Medições de Profundidade")
                interno = st.number_input("Interno (mm)", min_value=0.0, value=8.0, step=0.1)
                centro_interno = st.number_input("Centro Interno (mm)", min_value=0.0, value=8.0, step=0.1)
                centro_externo = st.number_input("Centro Externo (mm)", min_value=0.0, value=8.0, step=0.1)
                externo = st.number_input("Externo (mm)", min_value=0.0, value=8.0, step=0.1)

            submitted = st.form_submit_button("✅ Registrar Medição")

            if submitted:
                if voltas == 0:
                    st.error("⚠️ Informe o número de voltas!")
                else:
                    prof_media = (interno + centro_interno + centro_externo + externo) / 4
                    km_total = pneu_info['Quilometragem atual'] + km_percorrido

                    if prof_media >= 6:
                        condicao_twi = "Bom"
                    elif prof_media >= 3:
                        condicao_twi = "ok"
                    else:
                        condicao_twi = "Crítico"

                    if km_total < pneu_info['Limite KM'] * 0.5:
                        condicao_km = "Bom"
                    else:
                        condicao_km = "Desgastado"

                    if condicao_twi == "Crítico" or km_total >= pneu_info['Limite KM']:
                        acao = "DESCARTAR PNEU"
                    elif condicao_twi == "ok" or km_total >= pneu_info['Limite KM'] * 0.7:
                        acao = "MÉDIO DESGASTE"
                    else:
                        acao = "PRÓXIMA ETAPA"

                    nova_medicao = pd.DataFrame([{
                        'Código do Pneu': pneu_selecionado,
                        'Quilometragem Atual': pneu_info['Quilometragem atual'],
                        'Código de Barras': pneu_info['Código de Barras'],
                        'Carro': carro,
                        'Data Medição': data_medicao.strftime('%d/%m/%Y'),
                        'Tipo Evento': tipo_evento,
                        'Voltas': voltas,
                        'Tempo Pista (min)': tempo_pista,
                        'Pista': pista_nome,
                        'Quilometragem': km_percorrido,
                        'KM TOTAL': km_total,
                        'Interno (mm)': interno,
                        'Centro Interno (mm)': centro_interno,
                        'Centro Externo (mm)': centro_externo,
                        'Externo (mm)': externo,
                        'Profundidade Média (mm)': prof_media,
                        'Condição (twi)': condicao_twi,
                        'Condição (km)': condicao_km,
                        'AÇÃO': acao,
                        'Etapa': st.session_state.etapa_atual
                    }])

                    st.session_state.df_medicoes = pd.concat(
                        [st.session_state.df_medicoes, nova_medicao], 
                        ignore_index=True
                    )

                    st.session_state.df_cadastro.loc[
                        st.session_state.df_cadastro['Nome do Pneu'] == pneu_selecionado,
                        'Quilometragem atual'
                    ] = km_total

                    # Atualizar status do pneu
                    st.session_state.df_cadastro.loc[
                        st.session_state.df_cadastro['Nome do Pneu'] == pneu_selecionado,
                        'Status Etapa'
                    ] = 'Em uso'

                    st.success(f"✅ Medição registrada! Status: {acao}")
                    st.info(f"Profundidade Média: {prof_media:.2f}mm | KM Total: {km_total:.2f}km | KM Percorrido: {km_percorrido:.3f}km")
                    st.rerun()
    else:
        st.warning("⚠️ Nenhum pneu disponível nesta etapa!")

# Continua nas próximas mensagens devido ao tamanho...

# VISUALIZAR DADOS
elif menu == "📋 Visualizar Dados":
    st.header("Visualizar Dados")

    tab1, tab2 = st.tabs(["Cadastro de Pneus", "Medições"])

    with tab1:
        st.subheader("Cadastro de Pneus")

        # Filtro por etapa
        col1, col2 = st.columns(2)
        with col1:
            etapas_filtro = st.multiselect(
                "Filtrar por Etapa",
                options=sorted(st.session_state.df_cadastro['Etapa Atual'].unique()) if len(st.session_state.df_cadastro) > 0 else []
            )
        with col2:
            status_filtro = st.multiselect(
                "Filtrar por Status Etapa",
                options=st.session_state.df_cadastro['Status Etapa'].unique() if len(st.session_state.df_cadastro) > 0 else []
            )

        df_filtrado = st.session_state.df_cadastro.copy()
        if etapas_filtro:
            df_filtrado = df_filtrado[df_filtrado['Etapa Atual'].isin(etapas_filtro)]
        if status_filtro:
            df_filtrado = df_filtrado[df_filtrado['Status Etapa'].isin(status_filtro)]

        if len(df_filtrado) > 0:
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.info("Nenhum pneu encontrado com os filtros selecionados.")

    with tab2:
        st.subheader("Histórico de Medições")
        if len(st.session_state.df_medicoes) > 0:
            st.dataframe(st.session_state.df_medicoes, use_container_width=True)
        else:
            st.info("Nenhuma medição registrada ainda.")

# MONTAGEM DE SETS
elif menu == "🔧 Montagem de Sets":
    st.header("Gerenciar Montagem de Sets de Pneus")

    # Inicializar dataframe de sets se não existir
    if 'df_sets' not in st.session_state:
        st.session_state.df_sets = pd.DataFrame(columns=[
            'ID Set', 'Nome do Set', 'Carro', 'Data Montagem', 'Status', 'Etapa',
            'Pneu Dianteiro Esquerdo', 'Pneu Dianteiro Direito',
            'Pneu Traseiro Esquerdo', 'Pneu Traseiro Direito'
        ])

    tab1, tab2, tab3 = st.tabs(["🔧 Montar Novo Set", "📋 Sets Ativos", "📜 Histórico de Sets"])

    with tab1:
        st.subheader("Montar Novo Set de Pneus")

        pneus_etapa = st.session_state.df_cadastro[
            (st.session_state.df_cadastro['Etapa Atual'] == st.session_state.etapa_atual) &
            (st.session_state.df_cadastro['Status Etapa'] == 'Disponível')
        ]

        if len(pneus_etapa) >= 4:
            with st.form("montar_set_form"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    nome_set = st.text_input(
                        "Nome do Set",
                        placeholder=f"Ex: Set Etapa {st.session_state.etapa_atual} - Corrida"
                    )

                    carros_disponiveis = pneus_etapa['Carro Vinculado'].unique()
                    carro_set = st.selectbox("Carro", options=carros_disponiveis)

                with col2:
                    data_montagem = st.date_input("Data de Montagem", value=datetime.now())

                st.markdown("---")
                st.markdown("### Seleção de Pneus por Posição")

                # Filtrar por carro
                pneus_carro = pneus_etapa[pneus_etapa['Carro Vinculado'] == carro_set]['Nome do Pneu'].tolist()

                # Filtrar pneus já montados
                sets_ativos = st.session_state.df_sets[
                    (st.session_state.df_sets['Status'] == 'Ativo') &
                    (st.session_state.df_sets['Etapa'] == st.session_state.etapa_atual)
                ]

                pneus_montados = []
                if len(sets_ativos) > 0:
                    for col in ['Pneu Dianteiro Esquerdo', 'Pneu Dianteiro Direito',
                               'Pneu Traseiro Esquerdo', 'Pneu Traseiro Direito']:
                        pneus_montados.extend(sets_ativos[col].dropna().tolist())

                pneus_disponiveis = [p for p in pneus_carro if p not in pneus_montados]

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### Dianteiros")
                    pneu_de = st.selectbox("🔹 Dianteiro Esquerdo", options=[''] + pneus_disponiveis, key="pneu_de")
                    pneus_disp_dd = [p for p in pneus_disponiveis if p != pneu_de]
                    pneu_dd = st.selectbox("🔹 Dianteiro Direito", options=[''] + pneus_disp_dd, key="pneu_dd")

                with col2:
                    st.markdown("#### Traseiros")
                    pneus_disp_te = [p for p in pneus_disponiveis if p not in [pneu_de, pneu_dd]]
                    pneu_te = st.selectbox("🔹 Traseiro Esquerdo", options=[''] + pneus_disp_te, key="pneu_te")
                    pneus_disp_td = [p for p in pneus_disponiveis if p not in [pneu_de, pneu_dd, pneu_te]]
                    pneu_td = st.selectbox("🔹 Traseiro Direito", options=[''] + pneus_disp_td, key="pneu_td")

                submitted = st.form_submit_button("✅ Montar Set", use_container_width=True)

                if submitted:
                    pneus_selecionados = [pneu_de, pneu_dd, pneu_te, pneu_td]
                    pneus_validos = [p for p in pneus_selecionados if p != '']

                    if not nome_set:
                        st.error("⚠️ Digite um nome para o set!")
                    elif len(pneus_validos) != 4:
                        st.error("⚠️ Selecione os 4 pneus para montar o set!")
                    else:
                        if len(st.session_state.df_sets) > 0:
                            novo_id = st.session_state.df_sets['ID Set'].max() + 1
                        else:
                            novo_id = 1

                        novo_set = pd.DataFrame([{
                            'ID Set': novo_id,
                            'Nome do Set': nome_set,
                            'Carro': carro_set,
                            'Data Montagem': data_montagem.strftime('%d/%m/%Y'),
                            'Status': 'Ativo',
                            'Etapa': st.session_state.etapa_atual,
                            'Pneu Dianteiro Esquerdo': pneu_de,
                            'Pneu Dianteiro Direito': pneu_dd,
                            'Pneu Traseiro Esquerdo': pneu_te,
                            'Pneu Traseiro Direito': pneu_td
                        }])

                        st.session_state.df_sets = pd.concat(
                            [st.session_state.df_sets, novo_set],
                            ignore_index=True
                        )

                        # Atualizar status dos pneus
                        for pneu in pneus_validos:
                            st.session_state.df_cadastro.loc[
                                st.session_state.df_cadastro['Nome do Pneu'] == pneu,
                                'Status Etapa'
                            ] = 'Montado'

                        st.success(f"✅ Set '{nome_set}' montado com sucesso!")
                        st.balloons()
                        st.rerun()
        else:
            st.warning(f"⚠️ Pneus insuficientes! Necessário: 4 pneus disponíveis.")

    with tab2:
        st.subheader("Sets Atualmente Montados")

        sets_ativos = st.session_state.df_sets[
            (st.session_state.df_sets['Status'] == 'Ativo') &
            (st.session_state.df_sets['Etapa'] == st.session_state.etapa_atual)
        ]

        if len(sets_ativos) > 0:
            for idx, set_row in sets_ativos.iterrows():
                with st.expander(f"🔧 {set_row['Nome do Set']} - {set_row['Carro']}", expanded=False):
                    col1, col2, col3 = st.columns([2, 2, 1])

                    with col1:
                        st.markdown(f"**ID:** {set_row['ID Set']}")
                        st.markdown(f"**Data Montagem:** {set_row['Data Montagem']}")

                    with col2:
                        st.markdown(f"**Carro:** {set_row['Carro']}")
                        st.markdown(f"**Etapa:** {set_row['Etapa']}")

                    with col3:
                        if st.button("🔓 Desmontar", key=f"desmontar_{set_row['ID Set']}"):
                            st.session_state.df_sets.loc[
                                st.session_state.df_sets['ID Set'] == set_row['ID Set'],
                                'Status'
                            ] = 'Desmontado'

                            # Liberar pneus
                            for col in ['Pneu Dianteiro Esquerdo', 'Pneu Dianteiro Direito',
                                       'Pneu Traseiro Esquerdo', 'Pneu Traseiro Direito']:
                                pneu = set_row[col]
                                st.session_state.df_cadastro.loc[
                                    st.session_state.df_cadastro['Nome do Pneu'] == pneu,
                                    'Status Etapa'
                                ] = 'Disponível'

                            st.success("Set desmontado!")
                            st.rerun()

                    st.markdown("---")

                    col_de, col_dd = st.columns(2)
                    with col_de:
                        st.markdown("**Dianteiro Esquerdo**")
                        st.info(set_row['Pneu Dianteiro Esquerdo'])
                    with col_dd:
                        st.markdown("**Dianteiro Direito**")
                        st.info(set_row['Pneu Dianteiro Direito'])

                    col_te, col_td = st.columns(2)
                    with col_te:
                        st.markdown("**Traseiro Esquerdo**")
                        st.info(set_row['Pneu Traseiro Esquerdo'])
                    with col_td:
                        st.markdown("**Traseiro Direito**")
                        st.info(set_row['Pneu Traseiro Direito'])
        else:
            st.info("Nenhum set montado no momento.")

    with tab3:
        st.subheader("Histórico de Sets")

        sets_desmontados = st.session_state.df_sets[
            st.session_state.df_sets['Status'] == 'Desmontado'
        ]

        if len(sets_desmontados) > 0:
            st.dataframe(sets_desmontados, use_container_width=True)
        else:
            st.info("Nenhum set desmontado ainda.")

# GERENCIAR PISTAS
elif menu == "🏆 Gerenciar Pistas":
    st.header("Gerenciar Pistas")

    tab1, tab2 = st.tabs(["📋 Pistas Cadastradas", "➕ Adicionar Nova Pista"])

    with tab1:
        st.subheader("Pistas Cadastradas")

        if len(st.session_state.df_pistas) > 0:
            st.dataframe(st.session_state.df_pistas, use_container_width=True)

            st.markdown("---")
            st.markdown("### Editar ou Remover Pista")

            pista_selecionada = st.selectbox(
                "Selecionar Pista",
                options=st.session_state.df_pistas['Nome'].tolist()
            )

            if pista_selecionada:
                pista_info = st.session_state.df_pistas[
                    st.session_state.df_pistas['Nome'] == pista_selecionada
                ].iloc[0]

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### Informações Atuais")
                    st.info(f"**Nome:** {pista_info['Nome']}")
                    st.info(f"**KM por Volta:** {pista_info['KM por Volta']:.3f} km")
                    st.info(f"**Localização:** {pista_info['Localização']}")

                with col2:
                    st.markdown("#### Editar")
                    with st.form("editar_pista"):
                        novo_km = st.number_input(
                            "Novo KM por Volta",
                            min_value=0.0,
                            value=float(pista_info['KM por Volta']),
                            step=0.001,
                            format="%.3f"
                        )
                        nova_localizacao = st.text_input(
                            "Nova Localização",
                            value=pista_info['Localização']
                        )

                        col_a, col_b = st.columns(2)
                        with col_a:
                            atualizar = st.form_submit_button("✅ Atualizar", use_container_width=True)
                        with col_b:
                            remover = st.form_submit_button("🗑️ Remover", type="secondary", use_container_width=True)

                        if atualizar:
                            st.session_state.df_pistas.loc[
                                st.session_state.df_pistas['Nome'] == pista_selecionada,
                                ['KM por Volta', 'Localização']
                            ] = [novo_km, nova_localizacao]
                            st.success("Pista atualizada!")
                            st.rerun()

                        if remover:
                            st.session_state.df_pistas = st.session_state.df_pistas[
                                st.session_state.df_pistas['Nome'] != pista_selecionada
                            ]
                            st.success("Pista removida!")
                            st.rerun()
        else:
            st.info("Nenhuma pista cadastrada.")

    with tab2:
        st.subheader("Adicionar Nova Pista")

        with st.form("nova_pista"):
            nome_pista = st.text_input("Nome da Pista", placeholder="Ex: Interlagos")
            km_volta = st.number_input(
                "KM por Volta",
                min_value=0.0,
                value=0.0,
                step=0.001,
                format="%.3f"
            )
            localizacao = st.text_input("Localização", placeholder="Ex: São Paulo-SP")

            submitted = st.form_submit_button("✅ Adicionar Pista", use_container_width=True)

            if submitted:
                if nome_pista and km_volta > 0 and localizacao:
                    if nome_pista in st.session_state.df_pistas['Nome'].values:
                        st.error("⚠️ Já existe uma pista com este nome!")
                    else:
                        nova_pista = pd.DataFrame([{
                            'Nome': nome_pista,
                            'KM por Volta': km_volta,
                            'Localização': localizacao
                        }])

                        st.session_state.df_pistas = pd.concat(
                            [st.session_state.df_pistas, nova_pista],
                            ignore_index=True
                        )
                        st.success(f"✅ Pista {nome_pista} adicionada!")
                        st.rerun()
                else:
                    st.error("⚠️ Preencha todos os campos!")

# HISTÓRICO
elif menu == "📜 Histórico":
    st.header("Histórico Completo")

    tab1, tab2, tab3 = st.tabs(["📊 Histórico por Pneu", "🏁 Histórico por Etapa", "📈 Análises"])

    with tab1:
        st.subheader("Histórico Completo de Pneus")

        if len(st.session_state.df_cadastro) > 0:
            pneu_selecionado = st.selectbox(
                "Selecionar Pneu",
                options=st.session_state.df_cadastro['Nome do Pneu'].tolist()
            )

            if pneu_selecionado:
                pneu_info = st.session_state.df_cadastro[
                    st.session_state.df_cadastro['Nome do Pneu'] == pneu_selecionado
                ].iloc[0]

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Etapa Cadastro", pneu_info['Etapa Cadastro'])
                with col2:
                    st.metric("Etapa Atual", pneu_info['Etapa Atual'])
                with col3:
                    st.metric("Status", pneu_info['Status Etapa'])

                st.markdown("---")

                # Histórico de medições
                medicoes_pneu = st.session_state.df_medicoes[
                    st.session_state.df_medicoes['Código do Pneu'] == pneu_selecionado
                ]

                if len(medicoes_pneu) > 0:
                    st.markdown("### Histórico de Medições")
                    st.dataframe(medicoes_pneu, use_container_width=True)

                    # Gráfico de evolução
                    st.markdown("### Evolução da Profundidade")
                    medicoes_pneu_sorted = medicoes_pneu.sort_values('Data Medição')

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=list(range(1, len(medicoes_pneu_sorted) + 1)),
                        y=medicoes_pneu_sorted['Profundidade Média (mm)'],
                        mode='lines+markers',
                        name='Profundidade Média',
                        line=dict(width=3)
                    ))

                    fig.update_layout(
                        title=f"Evolução - {pneu_selecionado}",
                        xaxis_title="Número da Medição",
                        yaxis_title="Profundidade (mm)",
                        height=400
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Nenhuma medição registrada para este pneu.")
        else:
            st.info("Nenhum pneu cadastrado.")

    with tab2:
        st.subheader("Resumo por Etapa")

        if len(st.session_state.historico_etapas) > 0:
            st.dataframe(st.session_state.historico_etapas, use_container_width=True)
        else:
            st.info("Nenhuma etapa concluída ainda.")

    with tab3:
        st.subheader("Análises e Estatísticas")

        if len(st.session_state.df_cadastro) > 0:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Pneus por Etapa de Origem")
                origem_count = st.session_state.df_cadastro['Etapa Cadastro'].value_counts().sort_index()
                fig = px.bar(
                    x=origem_count.index,
                    y=origem_count.values,
                    labels={'x': 'Etapa', 'y': 'Quantidade'},
                    title="Pneus Comprados por Etapa"
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("### Status dos Pneus")
                status_count = st.session_state.df_cadastro['Status Etapa'].value_counts()
                fig = px.pie(
                    values=status_count.values,
                    names=status_count.index,
                    title="Distribuição de Status"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem dados para análise.")

# IMPORTAR/EXPORTAR
elif menu == "📤 Importar/Exportar":
    st.header("Importar/Exportar Dados")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📥 Importar")
        st.info("Use o upload na sidebar para importar um arquivo Excel existente.")

    with col2:
        st.subheader("📤 Exportar")
        if len(st.session_state.df_cadastro) > 0 or len(st.session_state.df_medicoes) > 0:
            excel_data = save_to_excel(
                st.session_state.df_cadastro,
                st.session_state.df_medicoes
            )

            st.download_button(
                label="⬇️ Download Excel",
                data=excel_data,
                file_name=f"Tire_Management_Etapa_{st.session_state.etapa_atual}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Nenhum dado para exportar.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏁 Tire Management System")
st.sidebar.markdown(f"**Temporada:** 2026")
st.sidebar.markdown(f"**Etapa Atual:** {st.session_state.etapa_atual}/12")
st.sidebar.caption("Desenvolvido para Stock Car Pro Series")