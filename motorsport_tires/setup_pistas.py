# Script para popular o banco com pistas brasileiras principais
# Execute este script APÓS executar o sistema pela primeira vez

import sqlite3

def popular_pistas_brasileiras():
    """Popula o banco com as principais pistas do motorsport brasileiro"""
    
    conn = sqlite3.connect('motorsport_tires.db')
    cursor = conn.cursor()
    
    pistas = [
        # ID, Nome, Comprimento(km), Tipo, Sentido, Características, DE, DD, TE, TD
        ('INTER7', 'Interlagos', 4.309, 'road', 'anti_horario', 'Abrasivo - Desgasta mais lado direito', 'medio', 'alto', 'medio', 'alto'),
        ('GOIA8', 'Goiânia', 3.835, 'road', 'horario', 'Suave - Desgaste equilibrado', 'medio', 'medio', 'medio', 'medio'),
        ('TARUM6', 'Tarumã', 3.012, 'oval', 'horario', 'Oval - Desgaste uniforme', 'medio', 'medio', 'medio', 'medio'),
        ('VELOPA8', 'Velopark', 3.180, 'road', 'horario', 'Técnico - Abrasivo', 'alto', 'alto', 'medio', 'medio'),
        ('CASCA8', 'Cascavel', 3.458, 'road', 'horario', 'Rápido - Suave', 'baixo', 'baixo', 'medio', 'medio'),
        ('CURIT8', 'Curitiba', 2.432, 'road', 'horario', 'Urbano - Muito abrasivo', 'alto', 'alto', 'alto', 'alto'),
        ('SANTA7', 'Santa Cruz do Sul', 3.567, 'road', 'horario', 'Misto - Desgaste médio', 'medio', 'medio', 'medio', 'medio'),
        ('CAMPO6', 'Campo Grande', 3.433, 'road', 'anti_horario', 'Rápido - Desgasta lado esquerdo', 'alto', 'medio', 'alto', 'medio'),
        ('LONDRI6', 'Londrina', 3.295, 'road', 'horario', 'Técnico - Abrasivo', 'alto', 'alto', 'medio', 'alto'),
        ('CARUARU6', 'Caruaru', 3.048, 'road', 'horario', 'Nordeste - Muito abrasivo', 'alto', 'alto', 'alto', 'alto'),
    ]
    
    for pista in pistas:
        cursor.execute('''
            INSERT OR REPLACE INTO pistas (id, nome, comprimento, tipo, sentido, caracteristicas,
                                  desgaste_de, desgaste_dd, desgaste_te, desgaste_td)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', pista)
    
    conn.commit()
    conn.close()
    
    print("✅ Pistas brasileiras cadastradas com sucesso!")
    print("\nPistas adicionadas:")
    for pista in pistas:
        print(f"- {pista[1]}: {pista[2]}km ({pista[5]})")

if __name__ == "__main__":
    popular_pistas_brasileiras()