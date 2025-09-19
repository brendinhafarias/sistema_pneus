import sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
from typing import Optional, List, Dict, Tuple
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página Streamlit
st.set_page_config(
    page_title="🏁 Motorsport Tire Control",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado melhorado para mobile
st.markdown("""
<style>
    .main > div {
        padding: 1rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        height: 3rem;
    }
    .status-green {
        background-color: #28a745;
        color: white;
        padding: 8px 15px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin: 5px 0;
    }
    .status-yellow {
        background-color: #ffc107;
        color: black;
        padding: 8px 15px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin: 5px 0;
    }
    .status-red {
        background-color: #dc3545;
        color: white;
        padding: 8px 15px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin: 5px 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #dee2e6;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .pneu-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        margin: 8px 0;
        text-align: center;
    }
    .pneu-card-green {
        background-color: #d4edda;
        border-color: #28a745;
    }
    .pneu-card-yellow {
        background-color: #fff3cd;
        border-color: #ffc107;
    }
    .pneu-card-red {
        background-color: #f8d7da;
        border-color: #dc3545;
    }
    .alert-success {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin: 10px 0;
    }
    .alert-warning {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ffeaa7;
        margin: 10px 0;
    }
    .alert-danger {
        background-color: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #f5c6cb;
        margin: 10px 0;
    }
    .home-section {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #e9ecef;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .main > div {
            padding: 0.5rem;
        }
        .stButton > button {
            height: 2.5rem;
            font-size: 14px;
        }
        .home-section {
            padding: 15px;
            margin: 10px 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# Função para conversão segura de tipos
def safe_float(value, default=0.0):
    """Converte valor para float de forma segura"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    """Converte valor para int de forma segura"""
    if value is None:
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

# Função para criar conexão com o banco (CORRIGIDA)
def get_database_connection():
    """Retorna uma nova conexão com o banco de dados"""
    return sqlite3.connect('motorsport_tires.db', check_same_thread=False)

# Função para verificar e corrigir estrutura do banco
def verificar_e_corrigir_banco():
    """Verifica e corrige problemas na estrutura do banco"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se coluna observacoes existe na tabela sets
        cursor.execute("PRAGMA table_info(sets)")
        colunas_sets = [row[1] for row in cursor.fetchall()]
        
        if 'observacoes' not in colunas_sets:
            cursor.execute("ALTER TABLE sets ADD COLUMN observacoes TEXT")
            conn.commit()
        
        # Verificar se coluna tempo_sessao existe na tabela outings
        cursor.execute("PRAGMA table_info(outings)")
        colunas_outings = [row[1] for row in cursor.fetchall()]
        
        if 'tempo_sessao' not in colunas_outings:
            cursor.execute("ALTER TABLE outings ADD COLUMN tempo_sessao INTEGER")
            conn.commit()
            
        return True
            
    except Exception as e:
        return False
    finally:
        conn.close()

# Inicialização do banco de dados (CORRIGIDA)
def init_database():
    """Cria as tabelas do banco de dados se não existirem"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Tabela de pneus individuais (SIMPLIFICADA)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pneus (
            id TEXT PRIMARY KEY,
            tipo TEXT NOT NULL,
            data_cadastro DATE,
            limite_km INTEGER,
            km_atual REAL DEFAULT 0,
            status TEXT DEFAULT 'disponivel',
            observacoes TEXT
        )
    ''')
    
    # Tabela de pistas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pistas (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            comprimento REAL NOT NULL,
            tipo TEXT DEFAULT 'road',
            sentido TEXT DEFAULT 'horario',
            caracteristicas TEXT,
            desgaste_de TEXT DEFAULT 'medio',
            desgaste_dd TEXT DEFAULT 'medio', 
            desgaste_te TEXT DEFAULT 'medio',
            desgaste_td TEXT DEFAULT 'medio'
        )
    ''')
    
    # Tabela de sets
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sets (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL,
            data_montagem DATE,
            status TEXT DEFAULT 'ativo',
            pneu_de TEXT,
            pneu_dd TEXT,
            pneu_te TEXT,
            pneu_td TEXT,
            observacoes TEXT,
            FOREIGN KEY (pneu_de) REFERENCES pneus (id),
            FOREIGN KEY (pneu_dd) REFERENCES pneus (id),
            FOREIGN KEY (pneu_te) REFERENCES pneus (id),
            FOREIGN KEY (pneu_td) REFERENCES pneus (id)
        )
    ''')
    
    # Tabela de outings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS outings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE NOT NULL,
            pista_id TEXT NOT NULL,
            set_id TEXT NOT NULL,
            tipo_sessao TEXT,
            condicao TEXT,
            voltas INTEGER,
            km_calculado REAL,
            tempo_sessao INTEGER,
            observacoes TEXT,
            FOREIGN KEY (pista_id) REFERENCES pistas (id),
            FOREIGN KEY (set_id) REFERENCES sets (id)
        )
    ''')
    
    # Tabela de histórico
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_pneus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pneu_id TEXT NOT NULL,
            outing_id INTEGER NOT NULL,
            posicao TEXT NOT NULL,
            km_antes REAL DEFAULT 0,
            km_depois REAL DEFAULT 0,
            FOREIGN KEY (pneu_id) REFERENCES pneus (id),
            FOREIGN KEY (outing_id) REFERENCES outings (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Verificar e corrigir estrutura após criação
    verificar_e_corrigir_banco()
    
    return True

# Classes para gerenciamento de dados (CORRIGIDAS)
class PneuManager:
    @staticmethod
    def cadastrar_pneu(id_pneu, tipo, limite_km, observacoes=""):
        conn = get_database_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO pneus (id, tipo, data_cadastro, limite_km, observacoes)
                VALUES (?, ?, ?, ?, ?)
            ''', (id_pneu, tipo, datetime.now().date(), limite_km, observacoes))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    @staticmethod
    def listar_pneus_disponiveis(tipo=None):
        conn = get_database_connection()
        # REMOVIDO FILTRO DINÂMICO - SEMPRE MOSTRA TODOS OS PNEUS DISPONÍVEIS
        query = "SELECT * FROM pneus WHERE status = 'disponivel' ORDER BY tipo, id"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    @staticmethod
    def listar_todos_pneus():
        conn = get_database_connection()
        df = pd.read_sql_query("SELECT * FROM pneus ORDER BY id", conn)
        conn.close()
        return df
    
    @staticmethod
    def get_pneu_by_id(pneu_id):
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pneus WHERE id = ?", (pneu_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    @staticmethod
    def atualizar_km_pneu(pneu_id, novo_km):
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE pneus SET km_atual = ? WHERE id = ?", (novo_km, pneu_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def atualizar_status_pneu(pneu_id, novo_status):
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE pneus SET status = ? WHERE id = ?", (novo_status, pneu_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def calcular_status_pneu(pneu_data):
        """Calcula o status do pneu baseado na quilometragem"""
        if not pneu_data:
            return "unknown", 0
        
        # Conversão segura para float
        km_atual = safe_float(pneu_data[4], 0)  # km_atual
        limite_km = safe_float(pneu_data[3], 1000)  # limite_km
        
        if limite_km <= 0:
            limite_km = 1000
        
        percentual = (km_atual / limite_km) * 100
        
        if percentual <= 70:
            return "green", percentual
        elif percentual <= 90:
            return "yellow", percentual
        else:
            return "red", percentual

class PistaManager:
    @staticmethod
    def cadastrar_pista(id_pista, nome, comprimento, tipo="road", sentido="horario", 
                       caracteristicas="", desgaste_de="medio", desgaste_dd="medio",
                       desgaste_te="medio", desgaste_td="medio"):
        conn = get_database_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO pistas (id, nome, comprimento, tipo, sentido, caracteristicas,
                                      desgaste_de, desgaste_dd, desgaste_te, desgaste_td)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (id_pista, nome, comprimento, tipo, sentido, caracteristicas,
                  desgaste_de, desgaste_dd, desgaste_te, desgaste_td))
            
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()
    
    @staticmethod
    def listar_pistas():
        conn = get_database_connection()
        df = pd.read_sql_query("SELECT * FROM pistas ORDER BY nome", conn)
        conn.close()
        return df
    
    @staticmethod
    def get_pista_by_id(pista_id):
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pistas WHERE id = ?", (pista_id,))
        result = cursor.fetchone()
        conn.close()
        return result

class SetManager:
    @staticmethod
    def criar_set(id_set, nome, tipo, pneu_de=None, pneu_dd=None, pneu_te=None, pneu_td=None, observacoes=""):
        conn = get_database_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se a coluna observacoes existe
            cursor.execute("PRAGMA table_info(sets)")
            colunas = [row[1] for row in cursor.fetchall()]
            
            if 'observacoes' in colunas:
                # Inserir com observacoes
                cursor.execute('''
                    INSERT INTO sets (id, nome, tipo, data_montagem, pneu_de, pneu_dd, pneu_te, pneu_td, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (id_set, nome, tipo, datetime.now().date(), pneu_de, pneu_dd, pneu_te, pneu_td, observacoes))
            else:
                # Inserir sem observacoes
                cursor.execute('''
                    INSERT INTO sets (id, nome, tipo, data_montagem, pneu_de, pneu_dd, pneu_te, pneu_td)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (id_set, nome, tipo, datetime.now().date(), pneu_de, pneu_dd, pneu_te, pneu_td))
            
            # Atualizar status dos pneus para 'em_uso'
            for pneu_id in [pneu_de, pneu_dd, pneu_te, pneu_td]:
                if pneu_id:
                    cursor.execute("UPDATE pneus SET status = 'em_uso' WHERE id = ?", (pneu_id,))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    @staticmethod
    def listar_sets():
        conn = get_database_connection()
        df = pd.read_sql_query("SELECT * FROM sets ORDER BY data_montagem DESC", conn)
        conn.close()
        return df
    
    @staticmethod
    def listar_sets_ativos():
        """Lista apenas sets ativos"""
        conn = get_database_connection()
        df = pd.read_sql_query("SELECT * FROM sets WHERE status = 'ativo' ORDER BY id", conn)
        conn.close()
        return df
    
    @staticmethod
    def get_set_by_id(set_id):
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sets WHERE id = ?", (set_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    @staticmethod
    def desmontar_set(set_id):
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Buscar pneus do set
        set_data = SetManager.get_set_by_id(set_id)
        if set_data:
            pneus = [set_data[5], set_data[6], set_data[7], set_data[8]]  # pneu_de, dd, te, td
            
            # Voltar pneus para disponível
            for pneu_id in pneus:
                if pneu_id:
                    cursor.execute("UPDATE pneus SET status = 'disponivel' WHERE id = ?", (pneu_id,))
            
            # Marcar set como desmontado
            cursor.execute("UPDATE sets SET status = 'desmontado' WHERE id = ?", (set_id,))
            
            conn.commit()
        conn.close()

class OutingManager:
    @staticmethod
    def registrar_outing(data, pista_id, set_id, tipo_sessao, condicao, voltas, observacoes=""):
        """VERSÃO CORRIGIDA COM ATUALIZAÇÃO GARANTIDA DOS PNEUS"""
        conn = get_database_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Buscar comprimento da pista
            pista = PistaManager.get_pista_by_id(pista_id)
            if not pista:
                return False
            
            comprimento = safe_float(pista[2], 4.0)
            km_calculado = voltas * comprimento
            
            # 2. Buscar dados do set ANTES de inserir o outing
            set_data = SetManager.get_set_by_id(set_id)
            if not set_data:
                return False
            
            # 3. Verificar se coluna tempo_sessao existe
            cursor.execute("PRAGMA table_info(outings)")
            colunas = [row[1] for row in cursor.fetchall()]
            
            if 'tempo_sessao' in colunas:
                # Inserir com tempo_sessao (NULL)
                cursor.execute('''
                    INSERT INTO outings (data, pista_id, set_id, tipo_sessao, condicao, voltas, km_calculado, tempo_sessao, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (data, pista_id, set_id, tipo_sessao, condicao, voltas, km_calculado, None, observacoes))
            else:
                # Inserir sem tempo_sessao
                cursor.execute('''
                    INSERT INTO outings (data, pista_id, set_id, tipo_sessao, condicao, voltas, km_calculado, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (data, pista_id, set_id, tipo_sessao, condicao, voltas, km_calculado, observacoes))
            
            outing_id = cursor.lastrowid
            
            # 4. CORRIGIDO - Atualizar cada pneu do set
            pneus_info = [
                {'posicao': 'DE', 'pneu_id': set_data[5]},  # pneu_de
                {'posicao': 'DD', 'pneu_id': set_data[6]},  # pneu_dd  
                {'posicao': 'TE', 'pneu_id': set_data[7]},  # pneu_te
                {'posicao': 'TD', 'pneu_id': set_data[8]}   # pneu_td
            ]
            
            pneus_atualizados = 0
            
            for pneu_info in pneus_info:
                pneu_id = pneu_info['pneu_id']
                posicao = pneu_info['posicao']
                
                if pneu_id and pneu_id.strip():  # Verificar se o pneu_id não é vazio
                    # Buscar dados atuais do pneu
                    cursor.execute("SELECT * FROM pneus WHERE id = ?", (pneu_id,))
                    pneu_data = cursor.fetchone()
                    
                    if pneu_data:
                        km_antes = safe_float(pneu_data[4], 0)  # km_atual
                        km_depois = km_antes + km_calculado
                        
                        # Inserir histórico
                        cursor.execute('''
                            INSERT INTO historico_pneus (pneu_id, outing_id, posicao, km_antes, km_depois)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (pneu_id, outing_id, posicao, km_antes, km_depois))
                        
                        # CORRIGIDO - Atualizar km atual do pneu
                        cursor.execute("UPDATE pneus SET km_atual = ? WHERE id = ?", (km_depois, pneu_id))
                        pneus_atualizados += 1
            
            # 5. Commit explícito de todas as operações
            conn.commit()
            
            return True
            
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    @staticmethod
    def listar_outings():
        conn = get_database_connection()
        query = '''
            SELECT o.*, p.nome as pista_nome, s.nome as set_nome
            FROM outings o
            JOIN pistas p ON o.pista_id = p.id
            JOIN sets s ON o.set_id = s.id
            ORDER BY o.data DESC, o.id DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    @staticmethod
    def get_outing_by_id(outing_id):
        """Busca outing por ID"""
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM outings WHERE id = ?", (outing_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    @staticmethod
    def atualizar_outing(outing_id, data, pista_id, set_id, tipo_sessao, condicao, voltas, observacoes=""):
        """Atualiza um outing existente - VERSÃO SIMPLIFICADA"""
        conn = get_database_connection()
        cursor = conn.cursor()
        
        try:
            # Buscar comprimento da pista para recalcular km
            pista = PistaManager.get_pista_by_id(pista_id)
            if not pista:
                return False
            
            comprimento = safe_float(pista[2], 4.0)
            km_calculado = voltas * comprimento
            
            # NOTA: Para simplicidade, apenas atualiza o outing
            # NÃO recalcula o histórico de pneus (seria muito complexo)
            cursor.execute('''
                UPDATE outings 
                SET data=?, pista_id=?, set_id=?, tipo_sessao=?, condicao=?, voltas=?, km_calculado=?, observacoes=?
                WHERE id=?
            ''', (data, pista_id, set_id, tipo_sessao, condicao, voltas, km_calculado, observacoes, outing_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    @staticmethod
    def excluir_outing(outing_id):
        """Exclui um outing e seu histórico - VERSÃO SIMPLIFICADA"""
        conn = get_database_connection()
        cursor = conn.cursor()
        
        try:
            # NOTA: Para simplicidade, apenas remove o outing e histórico
            # NÃO reverte a quilometragem dos pneus (seria muito complexo)
            
            # Excluir histórico de pneus associado
            cursor.execute("DELETE FROM historico_pneus WHERE outing_id = ?", (outing_id,))
            
            # Excluir o outing
            cursor.execute("DELETE FROM outings WHERE id = ?", (outing_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    @staticmethod
    def recalcular_km_todos_pneus():
        """Função para recalcular KM de todos os pneus baseado no histórico"""
        conn = get_database_connection()
        cursor = conn.cursor()
        
        try:
            # Resetar todos os pneus para 0
            cursor.execute("UPDATE pneus SET km_atual = 0")
            
            # Buscar todo o histórico ordenado por data
            query = '''
                SELECT h.pneu_id, h.km_antes, h.km_depois, o.data
                FROM historico_pneus h
                JOIN outings o ON h.outing_id = o.id
                ORDER BY o.data ASC, o.id ASC
            '''
            historico = cursor.execute(query).fetchall()
            
            # Recalcular baseado no histórico
            pneus_km = {}
            for hist in historico:
                pneu_id = hist[0]
                km_depois = safe_float(hist[2], 0)
                pneus_km[pneu_id] = km_depois
            
            # Atualizar cada pneu com seu KM final
            for pneu_id, km_final in pneus_km.items():
                cursor.execute("UPDATE pneus SET km_atual = ? WHERE id = ?", (km_final, pneu_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()

# Funções auxiliares (CORRIGIDAS)
def format_status_html(status, percentual):
    """Formata o status com cor HTML"""
    percentual_safe = safe_float(percentual, 0)
    
    if status == "green":
        return f'<div class="status-green">🟢 OK ({percentual_safe:.0f}%)</div>'
    elif status == "yellow":
        return f'<div class="status-yellow">🟡 ATENÇÃO ({percentual_safe:.0f}%)</div>'
    elif status == "red":
        return f'<div class="status-red">🔴 TROCAR ({percentual_safe:.0f}%)</div>'
    else:
        return f'<div>❓ N/A</div>'

def gerar_proximo_id(tabela):
    """Gera o próximo ID disponível para uma tabela"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        if tabela == 'pneus':
            cursor.execute("SELECT id FROM pneus ORDER BY CAST(SUBSTR(id, 2) AS INTEGER) DESC LIMIT 1")
            result = cursor.fetchone()
            if result:
                try:
                    ultimo_num = int(result[0][1:])  # Remove 'P' e converte para int
                    return f"P{ultimo_num + 1:03d}"
                except (ValueError, IndexError):
                    pass
            return "P001"
        
        elif tabela == 'sets':
            cursor.execute("SELECT id FROM sets ORDER BY CAST(SUBSTR(id, 2) AS INTEGER) DESC LIMIT 1")
            result = cursor.fetchone()
            if result:
                try:
                    ultimo_num = int(result[0][1:])  # Remove 'S' e converte para int
                    return f"S{ultimo_num + 1:03d}"
                except (ValueError, IndexError):
                    pass
            return "S001"
        
        elif tabela == 'pistas':
            cursor.execute("SELECT COUNT(*) FROM pistas")
            count = cursor.fetchone()[0]
            return f"T{count + 1:03d}"
        
        return "P001"  # Default fallback
    except Exception:
        return "P001"  # Fallback em caso de erro
    finally:
        conn.close()

# Interface Streamlit (ATUALIZADA COM PÁGINA INICIAL)
def main():
    # Inicializar banco de dados
    init_database()
    
    # Sidebar com navegação
    st.sidebar.title("🏁 Motorsport Tire Control")
    
    menu = st.sidebar.selectbox(
        "📋 Navegação:",
        [
            "🏠 Página Inicial",
            "📈 Histórico & Análises",
            "➕ Cadastrar Pneu",
            "🏁 Cadastrar Pista", 
            "🔧 Montar Set",
            "📝 Registrar Outing",
            "⚙️ Configurações"
        ]
    )
    
    # Status da conexão
    try:
        conn = get_database_connection()
        conn.close()
        st.sidebar.success("🟢 Sistema Online")
    except Exception:
        st.sidebar.error("🔴 Erro na Conexão")
    
    # Executar função baseada no menu
    try:
        if menu == "🏠 Página Inicial":
            pagina_inicial()
        elif menu == "📈 Histórico & Análises":
            mostrar_historico()
        elif menu == "➕ Cadastrar Pneu":
            cadastrar_pneu()
        elif menu == "🏁 Cadastrar Pista":
            cadastrar_pista()
        elif menu == "🔧 Montar Set":
            montar_set()
        elif menu == "📝 Registrar Outing":
            registrar_outing()
        elif menu == "⚙️ Configurações":
            configuracoes()
    except Exception as e:
        st.error(f"❌ Erro na aplicação: {str(e)}")
        st.info("🔄 Tente recarregar a página")

def pagina_inicial():
    # Header principal
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1>🏁 Motorsport Tire Control</h1>
        <h3 style="color: #666;">Sistema de Gestão de Pneus</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas principais em cards grandes
    try:
        with get_database_connection() as conn:
            total_pneus = pd.read_sql_query("SELECT COUNT(*) as count FROM pneus", conn).iloc[0]['count']
            disponiveis = pd.read_sql_query("SELECT COUNT(*) as count FROM pneus WHERE status = 'disponivel'", conn).iloc[0]['count']
            em_uso = pd.read_sql_query("SELECT COUNT(*) as count FROM pneus WHERE status = 'em_uso'", conn).iloc[0]['count']
            sets_ativos = pd.read_sql_query("SELECT COUNT(*) as count FROM sets WHERE status = 'ativo'", conn).iloc[0]['count']
            total_outings = pd.read_sql_query("SELECT COUNT(*) as count FROM outings", conn).iloc[0]['count']
            
            # KM total rodado
            km_total = pd.read_sql_query("SELECT SUM(km_atual) as total FROM pneus", conn).iloc[0]['total']
            km_total = safe_float(km_total, 0)
        
        # Métricas em grid 3x2
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)
        
        with col1:
            st.metric("🏎️ **Total de Pneus**", f"{total_pneus}", help="Pneus cadastrados no sistema")
        with col2:
            st.metric("✅ **Disponíveis**", f"{disponiveis}", help="Pneus prontos para uso")
        with col3:
            st.metric("🔧 **Em Uso**", f"{em_uso}", help="Pneus atualmente montados")
        
        with col4:
            st.metric("📦 **Sets Ativos**", f"{sets_ativos}", help="Sets prontos para corrida")
        with col5:
            st.metric("📝 **Outings**", f"{total_outings}", help="Sessões registradas")
        with col6:
            st.metric("📏 **KM Total**", f"{km_total:.0f}", help="Quilometragem acumulada")
    
    except Exception as e:
        st.error(f"Erro ao carregar métricas: {str(e)}")
    
    st.markdown("---")
    
    # Seções principais em duas colunas
    col_left, col_right = st.columns(2)
    
    with col_left:
        # Status dos Pneus Críticos
        st.subheader("⚠️ Pneus que Precisam de Atenção")
        
        try:
            pneus_df = PneuManager.listar_todos_pneus()
            
            if not pneus_df.empty:
                pneus_criticos = []
                for _, pneu in pneus_df.iterrows():
                    pneu_data = [pneu['id'], pneu['tipo'], pneu['data_cadastro'], pneu['limite_km'], pneu['km_atual'], pneu['status']]
                    status, percentual = PneuManager.calcular_status_pneu(pneu_data)
                    
                    if status in ['yellow', 'red']:  # Apenas pneus que precisam atenção
                        pneus_criticos.append({
                            'id': pneu['id'],
                            'tipo': str(pneu['tipo']).upper(),
                            'percentual': percentual,
                            'status': status,
                            'km_atual': safe_float(pneu['km_atual'], 0),
                            'limite': safe_float(pneu['limite_km'], 1000)
                        })
                
                if pneus_criticos:
                    for pneu in pneus_criticos[:5]:  # Mostrar apenas os 5 primeiros
                        if pneu['status'] == 'red':
                            st.markdown(f"""
                            <div class="pneu-card pneu-card-red">
                                <strong>🔴 {pneu['id']} ({pneu['tipo']})</strong><br>
                                <small>{pneu['km_atual']:.0f}/{pneu['limite']:.0f}km - {pneu['percentual']:.0f}% - TROCAR AGORA</small>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="pneu-card pneu-card-yellow">
                                <strong>🟡 {pneu['id']} ({pneu['tipo']})</strong><br>
                                <small>{pneu['km_atual']:.0f}/{pneu['limite']:.0f}km - {pneu['percentual']:.0f}% - Monitorar</small>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.success("🎉 Todos os pneus estão em bom estado!")
            else:
                st.info("ℹ️ Nenhum pneu cadastrado ainda.")
                
        except Exception as e:
            st.error(f"Erro ao verificar pneus: {str(e)}")
        
       
    with col_right:
        # Últimos Outings
        st.subheader("📝 Últimos Outings")
        
        try:
            outings_df = OutingManager.listar_outings()
            
            if not outings_df.empty:
                ultimos_outings = outings_df.head(5)  # Últimos 5 outings
                
                for _, outing in ultimos_outings.iterrows():
                    data_formatada = datetime.strptime(str(outing['data']), '%Y-%m-%d').strftime('%d/%m')
                    km_outing = safe_float(outing['km_calculado'], 0)
                    
                    st.markdown(f"""
                    <div class="pneu-card">
                        <strong>🏁 {data_formatada} - {outing['pista_nome']}</strong><br>
                        <small>Set {outing['set_nome']} • {outing['voltas']} voltas • {km_outing:.1f}km • {str(outing['tipo_sessao']).upper()}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("ℹ️ Nenhum outing registrado ainda.")
                
        except Exception as e:
            st.error(f"Erro ao carregar outings: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Seção de Ações Rápidas
       
     
    
    

def cadastrar_pneu():
    st.title("➕ Cadastrar Novo Pneu")
    
    # Botão para criar pneus de teste - CORRIGIDO
    if st.button("🧪 Criar Pneus de Teste (inclui chuva)", use_container_width=True):
        try:
            # Criar alguns pneus normais e de chuva para teste
            pneus_teste = [
                ("P001", "normal", 800, "Pneu normal de teste"),
                ("P002", "normal", 800, "Pneu normal de teste"),
                ("P003", "normal", 800, "Pneu normal de teste"),
                ("P004", "normal", 800, "Pneu normal de teste"),
                ("C001", "chuva", 600, "Pneu de chuva de teste"),
                ("C002", "chuva", 600, "Pneu de chuva de teste"),
                ("C003", "chuva", 600, "Pneu de chuva de teste"),
                ("C004", "chuva", 600, "Pneu de chuva de teste"),
            ]
            
            sucessos = 0
            for id_pneu, tipo, limite, obs in pneus_teste:
                if PneuManager.cadastrar_pneu(id_pneu, tipo, limite, obs):
                    sucessos += 1
            
            st.success(f"✅ {sucessos} pneus de teste criados com sucesso!")
            st.balloons()
            st.rerun()
            
        except Exception as e:
            st.error(f"Erro ao criar pneus: {str(e)}")
    
    # Formulário SIMPLIFICADO - CORRIGIDO
    with st.form("form_cadastro_pneu", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏷️ Identificação")
            id_pneu = st.text_input("ID do Pneu", value=gerar_proximo_id('pneus'), help="ID único do pneu")
            tipo = st.selectbox("Tipo", ["normal", "chuva"], help="Tipo de pneu para condição de pista")
        
        with col2:
            st.markdown("### 📊 Controle")
            limite_km = st.number_input("Limite KM", min_value=100, max_value=5000, value=800, step=50, 
                                      help="Quilometragem máxima recomendada para este pneu")
        
        observacoes = st.text_area("💭 Observações", help="Informações adicionais sobre o pneu (opcional)")
        
        # Botão de submit - CORRIGIDO
        submitted = st.form_submit_button("🚀 Cadastrar Pneu", use_container_width=True, type="primary")
        
        if submitted:
            if not id_pneu:
                st.error("❌ ID do pneu é obrigatório!")
            else:
                with st.spinner("Cadastrando pneu..."):
                    sucesso = PneuManager.cadastrar_pneu(id_pneu, tipo, limite_km, observacoes)
                    if sucesso:
                        st.success(f"✅ Pneu {id_pneu} cadastrado com sucesso!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ Erro: Pneu {id_pneu} já existe!")
    
    # Mostrar pneus cadastrados
    st.markdown("---")
    st.subheader("🏎️ Pneus Cadastrados")
    
    try:
        pneus_df = PneuManager.listar_todos_pneus()
        if not pneus_df.empty:
            # Preparar dados para exibição com conversão segura
            pneus_display = pneus_df.copy()
            pneus_display['km_atual'] = pneus_display['km_atual'].apply(lambda x: safe_float(x, 0))
            pneus_display['limite_km'] = pneus_display['limite_km'].apply(lambda x: safe_float(x, 1000))
            pneus_display['percentual_uso'] = ((pneus_display['km_atual'] / pneus_display['limite_km']) * 100).round(1)
            
            # Selecionar colunas para exibir
            colunas_display = pneus_display[['id', 'tipo', 'km_atual', 'limite_km', 'percentual_uso', 'status']].copy()
            colunas_display.columns = ['ID', 'Tipo', 'KM Atual', 'Limite KM', 'Uso (%)', 'Status']
            
            st.dataframe(colunas_display, use_container_width=True)
            
            # Estatísticas rápidas
            col1, col2, col3 = st.columns(3)
            col1.metric("🟢 Disponíveis", len(pneus_df[pneus_df['status'] == 'disponivel']))
            col2.metric("🔧 Em Uso", len(pneus_df[pneus_df['status'] == 'em_uso']))
            col3.metric("📊 KM Total", f"{pneus_display['km_atual'].sum():.0f}")
        else:
            st.info("ℹ️ Nenhum pneu cadastrado ainda.")
    except Exception as e:
        st.error(f"Erro ao listar pneus: {str(e)}")

def cadastrar_pista():
    st.title("🏁 Cadastrar Nova Pista")
    
    # Botão para criar pista de teste - CORRIGIDO
    if st.button("🧪 Criar Pista de Teste", use_container_width=True):
        try:
            sucesso = PistaManager.cadastrar_pista(
                "INTERLAG", "Autódromo de Interlagos", 4.309, "road", "anti_horario", 
                "Pista técnica e abrasiva", "alto", "medio", "alto", "medio"
            )
            if sucesso:
                st.success("✅ Pista de teste 'Interlagos' criada com sucesso!")
                st.rerun()
            else:
                st.warning("⚠️ Pista já existe ou erro na criação")
        except Exception as e:
            st.error(f"Erro ao criar pista: {str(e)}")
    
    with st.form("form_cadastro_pista", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏁 Informações Básicas")
            nome = st.text_input("Nome da Pista", help="Nome completo da pista")
            comprimento = st.number_input("Comprimento (km)", min_value=0.5, max_value=15.0, value=4.0, step=0.1,
                                        help="Comprimento de uma volta completa")
            tipo = st.selectbox("Tipo", ["road", "oval", "misto"])
            sentido = st.selectbox("Sentido", ["horario", "anti_horario"])
            caracteristicas = st.text_input("Características", placeholder="Ex: Abrasivo, Smooth, Técnico...",
                                          help="Características que afetam o desgaste dos pneus")
        
        with col2:
            st.markdown("### 📊 Padrão de Desgaste Esperado")
            st.info("Configure o desgaste esperado para cada posição do pneu")
            desgaste_de = st.selectbox("🔵 DE (Dianteira Esquerda)", ["baixo", "medio", "alto"], index=1)
            desgaste_dd = st.selectbox("🔴 DD (Dianteira Direita)", ["baixo", "medio", "alto"], index=1)
            desgaste_te = st.selectbox("🟢 TE (Traseira Esquerda)", ["baixo", "medio", "alto"], index=1)
            desgaste_td = st.selectbox("🟡 TD (Traseira Direita)", ["baixo", "medio", "alto"], index=1)
        
        # CORRIGIDO
        submitted = st.form_submit_button("🏁 Cadastrar Pista", use_container_width=True, type="primary")
        
        if submitted:
            if not nome:
                st.error("❌ Nome da pista é obrigatório!")
            else:
                id_pista = nome.upper().replace(" ", "")[:8]
                with st.spinner("Cadastrando pista..."):
                    sucesso = PistaManager.cadastrar_pista(
                        id_pista, nome, comprimento, tipo, sentido, caracteristicas,
                        desgaste_de, desgaste_dd, desgaste_te, desgaste_td
                    )
                    if sucesso:
                        st.success(f"✅ Pista {nome} cadastrada com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao cadastrar pista!")
    
    # Mostrar pistas cadastradas
    st.markdown("---")
    st.subheader("🏁 Pistas Cadastradas")
    try:
        pistas_df = PistaManager.listar_pistas()
        if not pistas_df.empty:
            pistas_display = pistas_df[['nome', 'comprimento', 'tipo', 'sentido', 'caracteristicas']].copy()
            pistas_display.columns = ['Pista', 'Comprimento (km)', 'Tipo', 'Sentido', 'Características']
            st.dataframe(pistas_display, use_container_width=True)
        else:
            st.info("ℹ️ Nenhuma pista cadastrada ainda.")
    except Exception as e:
        st.error(f"Erro ao listar pistas: {str(e)}")

def montar_set():
    st.title("🔧 Montar Novo Set")
    
    with st.form("form_montar_set", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏷️ Identificação do Set")
            id_set = st.text_input("ID do Set", value=gerar_proximo_id('sets'))
            nome_set = st.text_input("Nome do Set", placeholder="Ex: Set Corrida Principal")
            tipo_set = st.selectbox("Tipo do Set", ["normal", "chuva"])
            observacoes_set = st.text_area("Observações", placeholder="Ex: Set para Interlagos...")
        
        with col2:
            st.markdown("### 🎯 Todos os Pneus Disponíveis")
            
            try:
                # MUDANÇA: Agora mostra TODOS os pneus disponíveis, não filtra por tipo
                pneus_disponiveis = PneuManager.listar_pneus_disponiveis()
                
                st.info(f"📦 {len(pneus_disponiveis)} pneus disponíveis para montagem")
                
                if pneus_disponiveis.empty:
                    st.warning("⚠️ Nenhum pneu disponível!")
                    st.info("💡 Use o botão 'Criar Pneus de Teste' na tela de Cadastrar Pneu")
                    st.stop()
                
                # Criar opções com TODOS os pneus disponíveis
                opcoes_pneus = [""] + [
                    f"{row['id']} - {row['tipo'].upper()} ({safe_float(row['km_atual'], 0):.0f}km)"
                    for _, row in pneus_disponiveis.iterrows()
                ]
                
                ids_pneus = [""] + pneus_disponiveis['id'].tolist()
                
                st.success(f"✅ Todos os pneus ({len(pneus_disponiveis)}) estão disponíveis para seleção")
                
            except Exception as e:
                st.error(f"Erro ao carregar pneus: {str(e)}")
                st.stop()
        
        st.markdown("### 🎯 Seleção de Pneus por Posição")
        col_de, col_dd, col_te, col_td = st.columns(4)
        
        with col_de:
            pneu_de_idx = st.selectbox("🔵 DE", range(len(opcoes_pneus)), format_func=lambda x: opcoes_pneus[x])
            pneu_de = ids_pneus[pneu_de_idx] if pneu_de_idx > 0 else None
        
        with col_dd:
            pneu_dd_idx = st.selectbox("🔴 DD", range(len(opcoes_pneus)), format_func=lambda x: opcoes_pneus[x])
            pneu_dd = ids_pneus[pneu_dd_idx] if pneu_dd_idx > 0 else None
        
        with col_te:
            pneu_te_idx = st.selectbox("🟢 TE", range(len(opcoes_pneus)), format_func=lambda x: opcoes_pneus[x])
            pneu_te = ids_pneus[pneu_te_idx] if pneu_te_idx > 0 else None
        
        with col_td:
            pneu_td_idx = st.selectbox("🟡 TD", range(len(opcoes_pneus)), format_func=lambda x: opcoes_pneus[x])
            pneu_td = ids_pneus[pneu_td_idx] if pneu_td_idx > 0 else None
        
        # CORRIGIDO
        submitted = st.form_submit_button("🔧 Montar Set", use_container_width=True, type="primary")
        
        if submitted:
            if not nome_set:
                st.error("❌ Nome do set é obrigatório!")
            elif not any([pneu_de, pneu_dd, pneu_te, pneu_td]):
                st.error("❌ Selecione pelo menos um pneu!")
            else:
                # Verificar duplicatas
                pneus_selecionados = [p for p in [pneu_de, pneu_dd, pneu_te, pneu_td] if p]
                if len(pneus_selecionados) != len(set(pneus_selecionados)):
                    st.error("❌ Não é possível usar o mesmo pneu em posições diferentes!")
                else:
                    with st.spinner("Montando set..."):
                        try:
                            sucesso = SetManager.criar_set(id_set, nome_set, tipo_set, pneu_de, pneu_dd, pneu_te, pneu_td, observacoes_set)
                            if sucesso:
                                st.success(f"✅ Set {id_set} montado com sucesso!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ Erro: ID do set já existe!")
                        except Exception as e:
                            st.error(f"❌ Erro ao montar set: {str(e)}")
    
    # Mostrar sets existentes
    st.markdown("---")
    st.subheader("🔧 Sets Existentes")
    try:
        sets_df = SetManager.listar_sets()
        if not sets_df.empty:
            for _, set_row in sets_df.iterrows():
                with st.expander(f"{set_row['id']} - {set_row['nome']} ({set_row['status']})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Tipo:** {set_row['tipo']}")
                        st.write(f"**Data:** {set_row['data_montagem']}")
                        st.write(f"**Pneus:** DE:{set_row['pneu_de']} DD:{set_row['pneu_dd']} TE:{set_row['pneu_te']} TD:{set_row['pneu_td']}")
                        if 'observacoes' in set_row and set_row['observacoes']:
                            st.write(f"**Obs:** {set_row['observacoes']}")
                    
                    with col2:
                        if set_row['status'] == 'ativo':
                            if st.button(f"🔧 Desmontar", key=f"desmontar_{set_row['id']}"):
                                SetManager.desmontar_set(set_row['id'])
                                st.success("Set desmontado!")
                                st.rerun()
        else:
            st.info("ℹ️ Nenhum set encontrado.")
    except Exception as e:
        st.error(f"Erro ao listar sets: {str(e)}")

def registrar_outing():
    st.title("📝 Registrar Outing")
    
    # Inicializar session state para controle de edição
    if 'editando_outing' not in st.session_state:
        st.session_state.editando_outing = False
        st.session_state.outing_edit_id = None
    
    # FORMULÁRIO DE REGISTRO/EDIÇÃO
    if st.session_state.editando_outing:
        st.subheader("✏️ Editando Outing")
        
        # Carregar dados do outing sendo editado
        outing_data = OutingManager.get_outing_by_id(st.session_state.outing_edit_id)
        if not outing_data:
            st.error("Outing não encontrado!")
            st.session_state.editando_outing = False
            st.rerun()
    else:
        st.subheader("➕ Novo Outing")
        outing_data = None
    
    with st.form("form_outing"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Data
            data_default = date.today() if not outing_data else datetime.strptime(str(outing_data[1]), '%Y-%m-%d').date()
            data_outing = st.date_input("📅 Data", value=data_default)
            
            # Carregar e selecionar pista
            try:
                pistas_df = PistaManager.listar_pistas()
                if pistas_df.empty:
                    st.error("❌ Nenhuma pista cadastrada!")
                    st.stop()
                
                pista_opcoes = list(pistas_df['nome'])
                pista_default_idx = 0
                
                if outing_data:
                    pista_atual = pistas_df[pistas_df['id'] == outing_data[2]]
                    if not pista_atual.empty:
                        pista_default_idx = pista_opcoes.index(pista_atual.iloc[0]['nome'])
                
                pista_selecionada = st.selectbox("🏁 Pista", pista_opcoes, index=pista_default_idx)
                pista_id = pistas_df[pistas_df['nome'] == pista_selecionada]['id'].iloc[0]
                
            except Exception as e:
                st.error(f"Erro ao carregar pistas: {str(e)}")
                st.stop()
        
        with col2:
            # Carregar e selecionar set
            try:
                sets_ativos_df = SetManager.listar_sets_ativos()
                if sets_ativos_df.empty:
                    st.error("❌ Nenhum set ativo!")
                    st.stop()
                
                set_opcoes = [f"{row['id']} - {row['nome']}" for _, row in sets_ativos_df.iterrows()]
                set_default_idx = 0
                
                if outing_data:
                    set_atual = sets_ativos_df[sets_ativos_df['id'] == outing_data[3]]
                    if not set_atual.empty:
                        set_atual_option = f"{set_atual.iloc[0]['id']} - {set_atual.iloc[0]['nome']}"
                        if set_atual_option in set_opcoes:
                            set_default_idx = set_opcoes.index(set_atual_option)
                
                set_selecionado = st.selectbox("🔧 Set", set_opcoes, index=set_default_idx)
                set_id = sets_ativos_df.iloc[set_opcoes.index(set_selecionado)]['id']
                
            except Exception as e:
                st.error(f"Erro ao carregar sets: {str(e)}")
                st.stop()
        
        # Configurações da sessão
        col3, col4 = st.columns(2)
        with col3:
            tipos = ["treino", "corrida", "classificacao", "warmup", "teste"]
            tipo_default_idx = 0 if not outing_data else tipos.index(outing_data[4]) if outing_data[4] in tipos else 0
            tipo_sessao = st.selectbox("📋 Tipo", tipos, index=tipo_default_idx)
            
            condicoes = ["seco", "molhado", "misto"]
            condicao_default_idx = 0 if not outing_data else condicoes.index(outing_data[5]) if outing_data[5] in condicoes else 0
            condicao = st.selectbox("🌤️ Condição", condicoes, index=condicao_default_idx)
        
        with col4:
            voltas_default = 20 if not outing_data else safe_int(outing_data[6], 20)
            voltas = st.number_input("🏎️ Voltas", min_value=1, max_value=300, value=voltas_default)
        
        # Observações
        obs_default = "" if not outing_data else str(outing_data[9] or "")
        observacoes = st.text_area("💭 Observações (opcional)", value=obs_default)
        
        # Botões de ação
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.session_state.editando_outing:
                submitted = st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True)
            else:
                submitted = st.form_submit_button("📝 Registrar Outing", type="primary", use_container_width=True)
        
        with col_btn2:
            if st.session_state.editando_outing:
                cancelar = st.form_submit_button("❌ Cancelar Edição", use_container_width=True)
                if cancelar:
                    st.session_state.editando_outing = False
                    st.session_state.outing_edit_id = None
                    st.rerun()
    
    # Processar formulário
    if submitted:
        # Validações básicas
        if not pista_id or not set_id or voltas <= 0:
            st.error("❌ Preencha todos os campos obrigatórios!")
        else:
            with st.spinner("⏳ Processando..."):
                try:
                    if st.session_state.editando_outing:
                        # Atualizar outing existente
                        sucesso = OutingManager.atualizar_outing(
                            st.session_state.outing_edit_id,
                            data_outing, pista_id, set_id, tipo_sessao, condicao, voltas, observacoes
                        )
                        if sucesso:
                            st.success("✅ Outing atualizado com sucesso!")
                            st.session_state.editando_outing = False
                            st.session_state.outing_edit_id = None
                            st.rerun()
                        else:
                            st.error("❌ Erro ao atualizar outing!")
                    else:
                        # Registrar novo outing
                        sucesso = OutingManager.registrar_outing(
                            data_outing, pista_id, set_id, tipo_sessao, condicao, voltas, observacoes
                        )
                        if sucesso:
                            st.success("✅ Outing registrado com sucesso!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Erro ao registrar outing!")
                            
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
    
    # TABELA DE OUTINGS EXISTENTES
    st.markdown("---")
    st.subheader("📋 Outings Registrados")
    
    try:
        outings_df = OutingManager.listar_outings()
        
        if not outings_df.empty:
            # Preparar dados para exibição
            display_df = outings_df[['id', 'data', 'pista_nome', 'set_nome', 'tipo_sessao', 'condicao', 'voltas', 'km_calculado', 'observacoes']].copy()
            display_df.columns = ['ID', 'Data', 'Pista', 'Set', 'Tipo', 'Condição', 'Voltas', 'KM', 'Observações']
            display_df['KM'] = display_df['KM'].apply(lambda x: safe_float(x, 0)).round(1)
            
            # Mostrar tabela
            st.dataframe(display_df, use_container_width=True)
            
            # Seção de ações
            st.markdown("### 🔧 Ações")
            
            col_actions1, col_actions2, col_actions3 = st.columns(3)
            
            with col_actions1:
                st.markdown("**✏️ Editar Outing**")
                outing_ids = outings_df['id'].tolist()
                outing_opcoes = [f"ID {row['id']} - {row['data']} - {row['pista_nome']}" for _, row in outings_df.iterrows()]
                
                if outing_opcoes:
                    selected_edit_idx = st.selectbox("Selecione o outing para editar:", 
                                                   range(len(outing_opcoes)), 
                                                   format_func=lambda x: outing_opcoes[x])
                    
                    if st.button("✏️ Editar Selecionado", use_container_width=True, type="secondary"):
                        st.session_state.editando_outing = True
                        st.session_state.outing_edit_id = outing_ids[selected_edit_idx]
                        st.rerun()
            
            with col_actions2:
                st.markdown("**🗑️ Excluir Outing**")
                
                if outing_opcoes:
                    selected_delete_idx = st.selectbox("Selecione o outing para excluir:", 
                                                     range(len(outing_opcoes)), 
                                                     format_func=lambda x: outing_opcoes[x],
                                                     key="delete_select")
                    
                    if st.button("🗑️ Excluir Selecionado", use_container_width=True, type="secondary"):
                        # Confirmar exclusão
                        if 'confirmar_exclusao' not in st.session_state:
                            st.session_state.confirmar_exclusao = False
                        
                        if not st.session_state.confirmar_exclusao:
                            st.session_state.confirmar_exclusao = True
                            st.session_state.outing_para_excluir = outing_ids[selected_delete_idx]
                            st.rerun()
            
            with col_actions3:
                st.markdown("**🔄 Recalcular KM**")
                st.info("Corrige KM dos pneus baseado no histórico")
                
                if st.button("🔄 Recalcular Todos", use_container_width=True, type="secondary"):
                    with st.spinner("Recalculando KM de todos os pneus..."):
                        sucesso = OutingManager.recalcular_km_todos_pneus()
                        if sucesso:
                            st.success("✅ KM de todos os pneus recalculado!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao recalcular KM!")
            
            # Modal de confirmação de exclusão
            if st.session_state.get('confirmar_exclusao', False):
                st.markdown("---")
                st.warning("⚠️ **Confirmar Exclusão**")
                outing_info = outings_df[outings_df['id'] == st.session_state.outing_para_excluir].iloc[0]
                st.write(f"Tem certeza que deseja excluir o outing:")
                st.write(f"**ID {outing_info['id']}** - {outing_info['data']} - {outing_info['pista_nome']} - {outing_info['voltas']} voltas")
                
                col_confirm1, col_confirm2 = st.columns(2)
                
                with col_confirm1:
                    if st.button("✅ Sim, Excluir", use_container_width=True, type="primary"):
                        try:
                            sucesso = OutingManager.excluir_outing(st.session_state.outing_para_excluir)
                            if sucesso:
                                st.success("✅ Outing excluído com sucesso!")
                                st.session_state.confirmar_exclusao = False
                                del st.session_state.outing_para_excluir
                                st.rerun()
                            else:
                                st.error("❌ Erro ao excluir outing!")
                        except Exception as e:
                            st.error(f"❌ Erro: {str(e)}")
                
                with col_confirm2:
                    if st.button("❌ Cancelar", use_container_width=True):
                        st.session_state.confirmar_exclusao = False
                        if 'outing_para_excluir' in st.session_state:
                            del st.session_state.outing_para_excluir
                        st.rerun()
            
            # Estatísticas rápidas
            st.markdown("### 📊 Estatísticas")
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric("Total Outings", len(outings_df))
            col2.metric("Total Voltas", safe_int(outings_df['voltas'].sum()))
            col3.metric("Total KM", f"{outings_df['km_calculado'].apply(lambda x: safe_float(x, 0)).sum():.1f}")
            col4.metric("KM Médio/Outing", f"{outings_df['km_calculado'].apply(lambda x: safe_float(x, 0)).mean():.1f}")
        else:
            st.info("ℹ️ Nenhum outing registrado ainda.")
            
    except Exception as e:
        st.error(f"Erro ao carregar outings: {str(e)}")

def mostrar_historico():
    st.title("📈 Histórico & Análises")
    
    # Estatísticas gerais no topo
    try:
        with get_database_connection() as conn:
            total_pneus = pd.read_sql_query("SELECT COUNT(*) as count FROM pneus", conn).iloc[0]['count']
            disponiveis = pd.read_sql_query("SELECT COUNT(*) as count FROM pneus WHERE status = 'disponivel'", conn).iloc[0]['count']
            em_uso = pd.read_sql_query("SELECT COUNT(*) as count FROM pneus WHERE status = 'em_uso'", conn).iloc[0]['count']
            sets_ativos = pd.read_sql_query("SELECT COUNT(*) as count FROM sets WHERE status = 'ativo'", conn).iloc[0]['count']
            total_outings = pd.read_sql_query("SELECT COUNT(*) as count FROM outings", conn).iloc[0]['count']
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("🏎️ Pneus", total_pneus)
        col2.metric("✅ Disponíveis", disponiveis)
        col3.metric("🔧 Em Uso", em_uso)
        col4.metric("📦 Sets Ativos", sets_ativos)
        col5.metric("📝 Outings", total_outings)
    except Exception as e:
        st.error(f"Erro ao carregar métricas: {str(e)}")
    
    st.markdown("---")
    
    # Duas abas: Outings e Pneus (COM análise detalhada de volta)
    tab1, tab2 = st.tabs(["📝 Outings", "🏎️ Pneus"])
    
    with tab1:
        st.subheader("📝 Histórico de Outings")
        try:
            outings_df = OutingManager.listar_outings()
            
            if not outings_df.empty:
                # Filtros
                col1, col2, col3 = st.columns(3)
                with col1:
                    filtro_pista = st.selectbox("🏁 Filtrar por Pista", 
                                              ["Todas"] + outings_df['pista_nome'].unique().tolist())
                with col2:
                    filtro_set = st.selectbox("🔧 Filtrar por Set", 
                                            ["Todos"] + outings_df['set_nome'].unique().tolist())
                with col3:
                    filtro_tipo = st.selectbox("📋 Filtrar por Tipo", 
                                             ["Todos"] + outings_df['tipo_sessao'].unique().tolist())
                
                # Aplicar filtros
                df_filtrado = outings_df.copy()
                if filtro_pista != "Todas":
                    df_filtrado = df_filtrado[df_filtrado['pista_nome'] == filtro_pista]
                if filtro_set != "Todos":
                    df_filtrado = df_filtrado[df_filtrado['set_nome'] == filtro_set]
                if filtro_tipo != "Todos":
                    df_filtrado = df_filtrado[df_filtrado['tipo_sessao'] == filtro_tipo]
                
                # Formatação das colunas com conversão segura
                if not df_filtrado.empty:
                    outings_display = df_filtrado[['data', 'pista_nome', 'set_nome', 'tipo_sessao', 'condicao', 'voltas', 'km_calculado', 'observacoes']].copy()
                    outings_display.columns = ['Data', 'Pista', 'Set', 'Tipo', 'Condição', 'Voltas', 'KM', 'Observações']
                    outings_display['KM'] = outings_display['KM'].apply(lambda x: safe_float(x, 0)).round(1)
                    
                    st.dataframe(outings_display, use_container_width=True)
                    
                    # Estatísticas dos filtros aplicados
                    st.subheader("📊 Estatísticas dos Filtros")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total Outings", len(df_filtrado))
                    col2.metric("Total Voltas", safe_int(df_filtrado['voltas'].sum()))
                    col3.metric("Total KM", f"{df_filtrado['km_calculado'].apply(lambda x: safe_float(x, 0)).sum():.1f}")
                    col4.metric("KM Médio/Outing", f"{df_filtrado['km_calculado'].apply(lambda x: safe_float(x, 0)).mean():.1f}")
                else:
                    st.info("Nenhum outing encontrado com os filtros aplicados.")
            else:
                st.info("ℹ️ Nenhum outing registrado ainda.")
        except Exception as e:
            st.error(f"Erro ao carregar outings: {str(e)}")
    
    with tab2:
        st.subheader("🏎️ Análise Detalhada de Pneus")
        
        try:
            pneus_df = PneuManager.listar_todos_pneus()
            
            if not pneus_df.empty:
                # Criar opções mais descritivas com conversão segura
                opcoes_pneus = []
                for _, row in pneus_df.iterrows():
                    km_atual = safe_float(row['km_atual'], 0)
                    opcoes_pneus.append(f"{row['id']} - {str(row['tipo']).upper()} ({row['status']}) - {km_atual:.0f}km")
                
                pneu_selecionado_idx = st.selectbox(
                    "Selecione um pneu para análise detalhada:",
                    range(len(opcoes_pneus)),
                    format_func=lambda x: opcoes_pneus[x]
                )
                
                pneu_selecionado = pneus_df.iloc[pneu_selecionado_idx]['id']
                
                if pneu_selecionado:
                    # Dados do pneu
                    pneu_data = PneuManager.get_pneu_by_id(pneu_selecionado)
                                      
                    # Buscar histórico DETALHADO - DE VOLTA!
                    try:
                        with get_database_connection() as conn:
                            query = '''
                                SELECT h.*, o.data, p.nome as pista_nome, o.voltas, o.tipo_sessao, o.condicao
                                FROM historico_pneus h
                                JOIN outings o ON h.outing_id = o.id
                                JOIN pistas p ON o.pista_id = p.id
                                WHERE h.pneu_id = ?
                                ORDER BY o.data DESC, o.id DESC
                            '''
                            historico_df = pd.read_sql_query(query, conn, params=(pneu_selecionado,))
                        
                        if not historico_df.empty:
                            # Tabela de histórico DETALHADO
                            st.subheader(f"📋 Timeline Detalhada do Pneu {pneu_selecionado}")
                            st.info("🎯 **Histórico completo**: onde foi usado, em qual posição, em qual pista")
                            
                            historico_display = historico_df[['data', 'pista_nome', 'tipo_sessao', 'condicao', 'voltas', 'posicao', 'km_antes', 'km_depois']].copy()
                            historico_display.columns = ['Data', 'Pista', 'Tipo Sessão', 'Condição', 'Voltas', 'Posição', 'KM Antes', 'KM Depois']
                            
                            # Conversão segura para cálculo
                            historico_display['KM Antes'] = historico_display['KM Antes'].apply(lambda x: safe_float(x, 0))
                            historico_display['KM Depois'] = historico_display['KM Depois'].apply(lambda x: safe_float(x, 0))
                            historico_display['KM Ganho'] = historico_display['KM Depois'] - historico_display['KM Antes']
                            
                            st.dataframe(historico_display, use_container_width=True)
                            
                            # Estatísticas do pneu selecionado
                            st.subheader(f"📊 Estatísticas do Pneu {pneu_selecionado}")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            col1.metric("📈 Total de Usos", len(historico_df))
                            col2.metric("🏁 Total de Voltas", safe_int(historico_df['voltas'].sum()))
                            col3.metric("📏 KM Acumulado", f"{km_atual:.1f}")
                            
                            # Calcular pistas mais utilizadas
                            pistas_mais_usadas = historico_df['pista_nome'].mode()
                            pista_favorita = pistas_mais_usadas.iloc[0] if len(pistas_mais_usadas) > 0 else "N/A"
                            col4.metric("🏁 Pista Mais Usada", pista_favorita)
                            
                            # Distribuição por posição
                            if len(historico_df) > 0:
                                st.subheader("🎯 Uso por Posição no Carro")
                                posicoes_count = historico_df['posicao'].value_counts()
                                
                                col_pos1, col_pos2, col_pos3, col_pos4 = st.columns(4)
                                col_pos1.metric("🔵 DE", posicoes_count.get('DE', 0))
                                col_pos2.metric("🔴 DD", posicoes_count.get('DD', 0))
                                col_pos3.metric("🟢 TE", posicoes_count.get('TE', 0))
                                col_pos4.metric("🟡 TD", posicoes_count.get('TD', 0))
                        else:
                            st.info("ℹ️ Nenhum histórico encontrado para este pneu.")
                    except Exception as e:
                        st.error(f"Erro ao buscar histórico: {str(e)}")
            else:
                st.info("ℹ️ Nenhum pneu cadastrado ainda.")
        except Exception as e:
            st.error(f"Erro ao carregar pneus: {str(e)}")

def configuracoes():
    st.title("⚙️ Configurações do Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("ℹ️ Informações do Sistema")
        st.markdown("""
        **Sistema de Controle de Pneus para Motorsport**  
        
        - 🐍 **Python** + **Streamlit**
        - 🗄️ **SQLite** Database
        - 📱 **Interface Responsiva**
        - 🎯 **Desenvolvido para Motorsport**
        
        **Funcionalidades:**
        - ✅ Página inicial com visão geral
        - ✅ Histórico detalhado de pneus
        - ✅ Análise completa por posição/pista
        - ✅ Interface mobile otimizada
        - ✅ Decisões rápidas e práticas
        """)
        
        # Verificar dependências CORRIGIDO
        dependencias_ok = True
        try:
            import sqlite3
            import pandas as pd
            import plotly.express as px
            st.success("✅ Todas as dependências carregadas")
        except ImportError as e:
            st.error(f"❌ Erro nas dependências: {e}")
            dependencias_ok = False
    
    with col2:
        st.subheader("🎨 Configurações Padrão")
        
        # Limites recomendados por categoria
        st.markdown("### 🏎️ Limites Recomendados por Categoria")
        
        categorias = {
            "Stock Car": 600,
            "Fórmula": 300,
            "Endurance": 1200,
            "Turismo": 800,
            "Rally": 400
        }
        
        for categoria, limite in categorias.items():
            st.info(f"**{categoria}**: {limite}km")
    
    # Estatísticas do sistema
    st.markdown("---")
    st.subheader("📊 Estatísticas do Sistema")
    
    try:
        with get_database_connection() as conn:
            # Estatísticas gerais
            col1, col2, col3, col4 = st.columns(4)
            
            total_pneus = pd.read_sql_query("SELECT COUNT(*) as count FROM pneus", conn).iloc[0]['count']
            total_sets = pd.read_sql_query("SELECT COUNT(*) as count FROM sets", conn).iloc[0]['count']
            total_pistas = pd.read_sql_query("SELECT COUNT(*) as count FROM pistas", conn).iloc[0]['count']
            total_outings = pd.read_sql_query("SELECT COUNT(*) as count FROM outings", conn).iloc[0]['count']
            
            col1.metric("🏎️ Pneus", total_pneus)
            col2.metric("🔧 Sets", total_sets)
            col3.metric("🏁 Pistas", total_pistas)
            col4.metric("📝 Outings", total_outings)
            
            # Estatísticas por tipo
            if total_pneus > 0:
                st.subheader("📈 Distribuição de Pneus")
                
                stats_tipo = pd.read_sql_query("""
                    SELECT tipo, COUNT(*) as quantidade, AVG(km_atual) as km_medio
                    FROM pneus 
                    GROUP BY tipo
                """, conn)
                
                if not stats_tipo.empty:
                    for _, row in stats_tipo.iterrows():
                        km_medio = safe_float(row['km_medio'], 0)
                        st.metric(f"Pneus {str(row['tipo']).upper()}", 
                                 f"{row['quantidade']} unidades", 
                                 delta=f"Média: {km_medio:.0f}km")
    except Exception as e:
        st.error(f"Erro ao carregar estatísticas: {str(e)}")
    
    # Ações do sistema
    st.markdown("---")
    st.subheader("🔧 Ações do Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CORRIGIDO
        if st.button("🔄 Recarregar Sistema", use_container_width=True):
            st.rerun()
    
    with col2:
        # CORRIGIDO
        if st.button("🧹 Limpar Cache", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("✅ Cache limpo!")
    
    with col3:
        # CORRIGIDO
        if st.button("📋 Status do Banco", use_container_width=True):
            try:
                with get_database_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tabelas = cursor.fetchall()
                
                st.success(f"✅ Banco OK - {len(tabelas)} tabelas")
                for tabela in tabelas:
                    st.text(f"• {tabela[0]}")
            except Exception as e:
                st.error(f"❌ Erro no banco: {str(e)}")

if __name__ == "__main__":
    main()