# Vou criar o sistema completo de controle de pneus em Streamlit
# Primeiro, vamos instalar as dependências necessárias e criar a estrutura

import sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
from typing import Optional, List, Dict, Tuple

# Configuração da página
st.set_page_config(
    page_title="Motorsport Tire Control",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para inicializar o banco de dados
def init_database():
    """Cria as tabelas do banco de dados se não existirem"""
    conn = sqlite3.connect('motorsport_tires.db')
    cursor = conn.cursor()
    
    # Tabela de pneus individuais
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pneus (
            id TEXT PRIMARY KEY,
            tipo TEXT NOT NULL, -- 'normal' ou 'chuva'
            compound TEXT,
            marca TEXT,
            tamanho TEXT,
            data_cadastro DATE,
            controle_tipo TEXT, -- 'quilometragem' ou 'twi'
            limite_km INTEGER,
            twi_inicial REAL,
            twi_limite REAL,
            status TEXT DEFAULT 'disponivel', -- 'disponivel', 'em_uso', 'descartado'
            observacoes TEXT
        )
    ''')
    
    # Tabela de pistas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pistas (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            comprimento REAL NOT NULL,
            tipo TEXT, -- 'road', 'oval', 'misto'
            sentido TEXT, -- 'horario', 'anti_horario'
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
            tipo TEXT NOT NULL, -- 'normal' ou 'chuva'
            data_montagem DATE,
            status TEXT DEFAULT 'ativo', -- 'ativo', 'reserva', 'desmontado'
            pneu_de TEXT,
            pneu_dd TEXT,
            pneu_te TEXT,
            pneu_td TEXT,
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
            tipo_sessao TEXT, -- 'treino', 'corrida', 'classificacao'
            condicao TEXT, -- 'seco', 'molhado', 'misto'
            voltas INTEGER,
            km_calculado REAL,
            observacoes TEXT,
            FOREIGN KEY (pista_id) REFERENCES pistas (id),
            FOREIGN KEY (set_id) REFERENCES sets (id)
        )
    ''')
    
    # Tabela de histórico de uso por pneu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_pneus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pneu_id TEXT NOT NULL,
            outing_id INTEGER NOT NULL,
            posicao TEXT NOT NULL, -- 'DE', 'DD', 'TE', 'TD'
            km_antes REAL DEFAULT 0,
            km_depois REAL DEFAULT 0,
            twi_antes REAL,
            twi_depois REAL,
            FOREIGN KEY (pneu_id) REFERENCES pneus (id),
            FOREIGN KEY (outing_id) REFERENCES outings (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Funções de CRUD para pneus
class PneuManager:
    @staticmethod
    def cadastrar_pneu(id_pneu, tipo, compound, marca, tamanho, controle_tipo, 
                      limite_km=None, twi_inicial=None, twi_limite=None, observacoes=""):
        conn = sqlite3.connect('motorsport_tires.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pneus (id, tipo, compound, marca, tamanho, data_cadastro, 
                             controle_tipo, limite_km, twi_inicial, twi_limite, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (id_pneu, tipo, compound, marca, tamanho, datetime.now().date(),
              controle_tipo, limite_km, twi_inicial, twi_limite, observacoes))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def listar_pneus_disponiveis(tipo=None):
        conn = sqlite3.connect('motorsport_tires.db')
        query = "SELECT * FROM pneus WHERE status = 'disponivel'"
        if tipo:
            query += f" AND tipo = '{tipo}'"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    @staticmethod
    def get_pneu_by_id(pneu_id):
        conn = sqlite3.connect('motorsport_tires.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pneus WHERE id = ?", (pneu_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    @staticmethod
    def atualizar_status_pneu(pneu_id, novo_status):
        conn = sqlite3.connect('motorsport_tires.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE pneus SET status = ? WHERE id = ?", (novo_status, pneu_id))
        conn.commit()
        conn.close()

# Funções para pistas
class PistaManager:
    @staticmethod
    def cadastrar_pista(id_pista, nome, comprimento, tipo="road", sentido="horario", 
                       caracteristicas="", desgaste_de="medio", desgaste_dd="medio",
                       desgaste_te="medio", desgaste_td="medio"):
        conn = sqlite3.connect('motorsport_tires.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pistas (id, nome, comprimento, tipo, sentido, caracteristicas,
                              desgaste_de, desgaste_dd, desgaste_te, desgaste_td)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (id_pista, nome, comprimento, tipo, sentido, caracteristicas,
              desgaste_de, desgaste_dd, desgaste_te, desgaste_td))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def listar_pistas():
        conn = sqlite3.connect('motorsport_tires.db')
        df = pd.read_sql_query("SELECT * FROM pistas", conn)
        conn.close()
        return df
    
    @staticmethod
    def get_pista_by_id(pista_id):
        conn = sqlite3.connect('motorsport_tires.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pistas WHERE id = ?", (pista_id,))
        result = cursor.fetchone()
        conn.close()
        return result

print("Estrutura base do sistema criada!")
print("Resposta sobre celular/tablet: SIM! Streamlit funciona perfeitamente em dispositivos móveis através do navegador.")