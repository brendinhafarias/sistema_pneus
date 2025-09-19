# 🚀 INÍCIO RÁPIDO - Sistema de Controle de Pneus

## ⚡ Execução Imediata

### 1. Instalar dependências:
```bash
pip install streamlit pandas
```

### 2. Executar o sistema:
```bash
streamlit run motorsport_tires.py
```

### 3. Abrir no navegador:
- Automático: http://localhost:8501
- Mobile: http://SEU_IP:8501

## 📱 USO MOBILE: SIM, FUNCIONA PERFEITAMENTE!
- ✅ Interface otimizada para celular/tablet
- ✅ Touch screen responsivo  
- ✅ Funciona offline após carregar
- ✅ Qualquer navegador (Chrome, Safari, etc.)

## 🏁 PRIMEIROS PASSOS (10 minutos)

### Passo 1: Cadastrar Pistas (Opcional - use o script)
```bash
# Executar APÓS primeira inicialização do sistema
python setup_pistas.py
```
**OU** cadastre manualmente suas pistas principais

### Passo 2: Cadastrar Pneus
```
Menu: ➕ Cadastrar Pneu
- Tipo: Normal/Chuva
- Controle: Quilometragem OU TWI
- Limite conforme sua categoria
```

### Passo 3: Montar Set
```
Menu: 🔧 Montar Set  
- Selecione 4 pneus do mesmo tipo
- Mix de marcas/compounds permitido
```

### Passo 4: Usar Dashboard
```
Menu: 📊 Dashboard Principal
- Visualizar status: 🟢🟡🔴
- Monitorar sets ativos
```

### Passo 5: Registrar Outing
```
Menu: 📝 Registrar Outing
- Selecione pista + voltas
- Sistema calcula KM automaticamente
```

## 🎯 CÓDIGOS DE STATUS

| Status | Significado | Ação |
|--------|------------|------|
| 🟢 Verde | 0-70% usado | Continue normalmente |
| 🟡 Amarelo | 71-90% usado | Prepare substituto |
| 🔴 Vermelho | 91-100% usado | TROCAR urgente |

## 💡 DICAS ESSENCIAIS

### ⚡ Uso Rápido no Paddock:
1. **Pré-sessão**: Check dashboard (30 segundos)
2. **Pós-sessão**: Registrar outing (1 minuto)
3. **Decisão**: Status visual imediato

### 🏆 Para Competição:
- Apenas pneus 🟢 VERDES para corridas críticas
- Pneus 🟡 AMARELOS para treinos
- NUNCA usar pneus 🔴 VERMELHOS

### 📊 Controle por Categoria:
- **Stock Car**: 400-600km ou TWI 2.0mm
- **Fórmula**: 200-300km ou TWI 1.5mm  
- **Endurance**: 800-1200km ou TWI 2.5mm

## 🛠️ RESOLUÇÃO DE PROBLEMAS

### Erro de módulo:
```bash
pip install --upgrade streamlit pandas
```

### Reset do banco:
```bash
# Deletar arquivo e reiniciar
rm motorsport_tires.db
```

## 📈 FUNCIONALIDADES PRINCIPAIS

✅ **Cadastro individual de pneus** (normal/chuva)  
✅ **Controle por quilometragem OU TWI**  
✅ **Montagem flexível de sets** (mix permitido)  
✅ **Registro rápido de outings**  
✅ **Cálculo automático de quilometragem**  
✅ **Histórico detalhado por pneu**  
✅ **Análise por pista específica**  
✅ **Dashboard visual em tempo real**  
✅ **Interface mobile completa**  
✅ **Banco SQLite integrado**  

## 🎯 FLUXO IDEAL DE TRABALHO

### No Paddock (Mobile):
1. **Chegada**: Check dashboard no celular
2. **Pré-treino**: Verificar set ativo  
3. **Pós-treino**: Registrar outing
4. **Entre sessões**: Monitorar alertas
5. **Pré-corrida**: Confirmar pneus verdes

### No Workshop:
1. **Recebimento**: Cadastrar pneus novos
2. **Preparação**: Montar sets por evento
3. **Análise**: Revisar histórico por pista
4. **Planejamento**: Estratégia de trocas

## 🏁 RESULTADO ESPERADO

**ANTES**: "Será que este pneu ainda está bom?"  
**DEPOIS**: Status visual imediato + dados precisos

**BENEFÍCIOS**:
- ⏱️ Decisões em segundos, não minutos
- 💰 Otimização de uso dos pneus
- 📊 Dados reais, não "achismo"
- 📱 Controle total via mobile
- 🎯 Foco na performance, não na planilha

---
**Sistema desenvolvido especificamente para o motorsport brasileiro** 🇧🇷