# 🏁 Sistema de Controle de Pneus para Motorsport

Sistema completo desenvolvido em Python com Streamlit para controle de pneus em competições de motorsport, focado em simplicidade e eficiência para tomada de decisões rápidas.

## 🚀 Compatibilidade Mobile/Tablet

✅ **SIM! Funciona perfeitamente em celular e tablet**
- Interface responsiva otimizada para dispositivos móveis
- Navegação por touch otimizada
- Funciona em qualquer navegador (Chrome, Safari, Firefox)
- Layout adaptável para diferentes tamanhos de tela
- Uso offline após carregamento inicial

## 📋 Funcionalidades

### ✅ Implementadas
- **Cadastro Individual de Pneus**: Normal/Chuva com controle por quilometragem OU TWI
- **Cadastro de Pistas**: Com cálculo automático de quilometragem por volta
- **Montagem Flexível de Sets**: Mix de pneus de diferentes lotes/marcas
- **Registro de Outings**: Entrada rápida com cálculo automático
- **Dashboard Visual**: Status por código de cores (🟢🟡🔴)
- **Histórico Detalhado**: Timeline completa por pneu individual
- **Análise por Pista**: Padrões de desgaste específicos
- **Banco SQLite**: Dados persistentes e portáveis

## 🛠️ Instalação e Configuração

### 1. Pré-requisitos
```bash
# Instalar Python 3.8 ou superior
# Instalar dependências
pip install streamlit pandas
```

### 2. Executar o Sistema
```bash
# Executar o comando no diretório do arquivo
streamlit run motorsport_tires.py

# O sistema abrirá automaticamente no navegador
# URL local: http://localhost:8501
```

### 3. Primeiro Acesso
1. **Cadastrar Pistas**: Comece cadastrando suas pistas principais
2. **Cadastrar Pneus**: Registre seu estoque de pneus
3. **Montar Sets**: Crie seus primeiros sets de corrida
4. **Usar Dashboard**: Monitore status em tempo real

## 📱 Uso Mobile

### Acesso via Celular/Tablet:
1. Execute o sistema no computador
2. Descubra o IP local da máquina
3. Acesse via celular: `http://IP_LOCAL:8501`
4. Salve como favorito no navegador mobile

### Exemplo de IP Local:
```bash
# No Windows: ipconfig
# No Linux/Mac: ifconfig
# Exemplo: http://192.168.1.100:8501
```

## 🎯 Fluxo de Uso Típico

### Preparação Pré-Evento (5 min)
1. **Dashboard**: Verificar status dos sets ativos
2. **Pneus Vermelhos**: Trocar antes do evento
3. **Pneus Amarelos**: Monitorar durante uso
4. **Set Reserva**: Preparar se necessário

### Durante o Evento (1 min por sessão)
1. **Registrar Outing**: Inserir pista + voltas
2. **Sistema Calcula**: Quilometragem automática
3. **Atualização**: Status de cada pneu automaticamente
4. **Alertas**: Notificações se pneu atingir limite

### Pós-Evento (2 min)
1. **Revisão**: Status final de todos os pneus
2. **Decisão**: Manter, trocar ou descartar
3. **Planejamento**: Preparação para próximo evento

## 📊 Sistema de Status

### 🟢 Verde (OK)
- **Quilometragem**: 0-70% do limite
- **TWI**: Profundidade adequada
- **Ação**: Continue usando normalmente

### 🟡 Amarelo (Atenção)  
- **Quilometragem**: 71-90% do limite
- **TWI**: Aproximando do limite
- **Ação**: Prepare substituto, monitore de perto

### 🔴 Vermelho (Trocar)
- **Quilometragem**: 91-100% do limite
- **TWI**: No limite mínimo
- **Ação**: TROCAR antes da próxima sessão

## 💾 Estrutura de Dados

### Banco SQLite Automático
- **Arquivo**: `motorsport_tires.db`
- **Local**: Mesmo diretório do programa
- **Backup**: Copie este arquivo para segurança

### Tabelas Principais:
- `pneus`: Registro individual de cada pneu
- `sets`: Montagem de conjuntos de 4 pneus  
- `pistas`: Cadastro com comprimento para cálculos
- `outings`: Histórico de cada sessão de uso
- `historico_pneus`: Timeline detalhada por pneu

## 🔧 Configurações por Categoria

### Stock Car
- **Limite KM**: 400-600km
- **TWI Mínimo**: 2.0mm
- **Foco**: Durabilidade e consistência

### Fórmula
- **Limite KM**: 200-300km
- **TWI Mínimo**: 1.5mm  
- **Foco**: Performance máxima

### Endurance
- **Limite KM**: 800-1200km
- **TWI Mínimo**: 2.5mm
- **Foco**: Resistência e economia

## 🛡️ Backup e Segurança

### Backup Manual:
```bash
# Copiar arquivo do banco
cp motorsport_tires.db backup_YYYY-MM-DD.db
```

### Restaurar Backup:
```bash
# Substituir arquivo atual
cp backup_YYYY-MM-DD.db motorsport_tires.db
```

## 📈 Análises Disponíveis

### Por Pneu Individual:
- Histórico completo de uso
- Performance por pista específica
- Padrão de desgaste por posição
- Previsão de vida útil

### Por Pista:
- Características de desgaste
- Sets mais adequados por local
- Histórico de performance
- Recomendações de limites

### Por Set:
- Balanceamento do conjunto
- Adequação por tipo de pista
- Histórico de resultados
- Previsão de próximas trocas

## 🆘 Solução de Problemas

### Erro "Module not found":
```bash
pip install --upgrade streamlit pandas
```

### Banco de dados corrompido:
```bash
# Deletar arquivo e reiniciar
rm motorsport_tires.db
# Sistema criará novo banco automaticamente
```

### Performance lenta:
- Mantenha histórico de até 1000 outings
- Faça backup e limpe dados antigos periodicamente

## 🎯 Dicas de Uso

### Eficiência Máxima:
1. **Use códigos curtos** para IDs de pneus (P001, P002...)
2. **Cadastre pistas principais** no início da temporada
3. **Mantenha sets padrão** (Corrida, Reserva, Treino, Chuva)
4. **Registre outings imediatamente** após cada sessão

### Decisões Inteligentes:
- **Nunca use pneus vermelhos** em situações críticas
- **Pneus amarelos** para treinos, verdes para corridas
- **Monitore padrões por pista** para otimizar estratégia
- **Use histórico** para planejar trocas antecipadas

## 📞 Suporte

Sistema desenvolvido especificamente para as necessidades do motorsport brasileiro, focando em:
- **Simplicidade operacional**
- **Decisões rápidas e confiáveis** 
- **Compatibilidade total mobile**
- **Dados precisos sem estimativas**

Para dúvidas ou sugestões, consulte o histórico de desenvolvimento ou adaptações necessárias para sua categoria específica.