import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import os
import io
import random
import string
from itertools import groupby
from supabase import create_client, Client

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AT Cerimonial — Controle",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# PREVENIR TRADUÇÃO AUTOMÁTICA (CHROME/EDGE/SAFARI)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)
components.html("""
<script>
    const desativarTraducao = () => {
        const html = window.parent.document.documentElement;
        const body = window.parent.document.body;
        if (html) {
            html.setAttribute('translate', 'no');
            html.classList.add('notranslate');
        }
        if (body) {
            body.setAttribute('translate', 'no');
            body.classList.add('notranslate');
        }
    };
    desativarTraducao();
    // Garante a aplicação caso o DOM ainda esteja carregando
    window.parent.addEventListener('DOMContentLoaded', desativarTraducao);
    setTimeout(desativarTraducao, 500);
    setTimeout(desativarTraducao, 1500);

    // MÁSCARA DE DATA AUTOMÁTICA (Real-time formatting)
    const aplicarMascaraData = () => {
        const labels = window.parent.document.querySelectorAll('label');
        for (const label of labels) {
            if (label.textContent.trim() === 'Data') {
                const container = label.closest('[data-testid="stTextInput"]');
                if (container) {
                    const input = container.querySelector('input');
                    if (input && !input.dataset.masked) {
                        input.dataset.masked = "true";
                        input.placeholder = "DD/MM/AAAA";
                        
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype, "value").set;
                        
                        input.addEventListener('input', function(e) {
                            let value = e.target.value.replace(/\D/g, '');
                            if (value.length > 8) {
                                value = value.slice(0, 8);
                            }
                            let formatted = '';
                            if (value.length > 0) {
                                formatted += value.slice(0, 2);
                            }
                            if (value.length > 2) {
                                formatted += '/' + value.slice(2, 4);
                            }
                            if (value.length > 4) {
                                formatted += '/' + value.slice(4, 8);
                            }
                            
                            // Evita recursão infinita se o valor já estiver correto
                            if (e.target.value === formatted) {
                                return;
                            }
                            
                            // Define valor através do setter nativo do React
                            nativeInputValueSetter.call(e.target, formatted);
                            e.target.dispatchEvent(new Event('input', { bubbles: true }));
                        });
                    }
                }
            }
        }
    };

    // Executa e observa mudanças no DOM
    aplicarMascaraData();
    const observer = new MutationObserver(aplicarMascaraData);
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
</script>
""", height=0, width=0)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.stApp { background: #F1F5F9; font-family: 'Inter', sans-serif; }

/* ── Sidebar ── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
section[data-testid="stSidebar"] .block-container {
    background-color: #0B2545 !important;
}

/* Força fundo transparente em TODOS os elementos internos da sidebar */
/* Texto da sidebar sempre branco */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] li,
section[data-testid="stSidebar"] a {
    color: #FFFFFF !important;
}


/* Corrige tarja branca: containers internos com fundo transparente */
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stMarkdown > div,
section[data-testid="stSidebar"] .element-container,
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div,
section[data-testid="stSidebar"] .stCheckbox {
    background-color: transparent !important;
    background:       transparent !important;
}

/* Expanders na sidebar */
section[data-testid="stSidebar"] [data-testid="stExpander"],
section[data-testid="stSidebar"] details summary {
    background-color: rgba(255,255,255,0.08) !important;
    border-color: rgba(255,255,255,0.15) !important;
}

/* Inputs na sidebar: texto escuro sobre fundo branco */
section[data-testid="stSidebar"] input {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
}
/* Selectbox na sidebar */
section[data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="select-control"],
section[data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="select-control"] * {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
}

/* ════════════════════════════════════════════════
   BOTÕES — Azul marinho em qualquer tema
════════════════════════════════════════════════ */
div.stButton > button, div.stFormSubmitButton > button {
    background-color: #134074 !important;
    color: #FFFFFF !important;
    border-radius: 6px !important;
    border: none !important;
    font-weight: 600 !important;
    width: 100%;
    transition: background 0.2s;
}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {
    background-color: #0B2545 !important;
}
div.stButton > button *, div.stFormSubmitButton > button * {
    color: #FFFFFF !important;
}

/* ── Alert rows (urgency list) ── */
.alert-row {
    background: #FFF7ED;
    border-left: 4px solid #F97316;
    border-radius: 4px;
    padding: 8px 14px;
    margin-bottom: 6px;
    font-size: 14px;
    color: #0F172A;
}

/* ── Briefing read-only field ── */
.bf-field {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 10px;
    font-size: 14px;
    color: #0F172A;
}
.bf-label { font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 4px; }

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 12px 16px;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════════════════════
DB_FILE = "eventos_db.json"

SETORES_PADRAO = [
    "Igreja / local da cerimônia", "Celebrante", "Carro da noiva",
    "Músicos cerimônia religiosa", "Instrumento extra", "Dia da noiva", "Dia do noivo",
    "Fotógrafo", "Salão de festas / sítio", "Buffet", "Comida Japonesa", "Disk Bebidas",
    "Decoração", "Luz / Som / Pista de dança", "Banda principal", "DJ",
    "Iluminação cênica", "Tenda / palco / tablado", "Doces 01", "Doces 02",
    "Bolo fake / maquete do bolo", "Lembranças (bem casados??)", "Sobremesa",
    "Cabine de fotos", "Brinquedos Espaço Kids", "Recreação Infantil", "Segurança",
    "Limpeza / Vassourinha de ouro", "Gerador de energia", "Hotel Noite de Núpcias",
    "Vans", "Ambulância",
]

STATUS_OPCOES = [
    "Orçando", "Dados enviados", "Contrato recebido",
    "Análise concluída / liberado para assinatura",
    "Aguardando assinatura do CONTRATADO", "CONTRATADO", "Não haverá",
]

STATUS_CORES = {
    "Orçando":                                              "#DC2626",
    "Dados enviados":                                       "#2563EB",
    "Contrato recebido":                                    "#D97706",
    "Análise concluída / liberado para assinatura":         "#7C3AED",
    "Aguardando assinatura do CONTRATADO":                  "#0891B2",
    "CONTRATADO":                                           "#16A34A",
    "Não haverá":                                           "#94A3B8",
}

CHECKLIST_CERIMONIAL_PADRAO = [
    {"id": "cc01", "grupo": "12 meses antes", "tarefa": "Reunião inicial de planejamento e cronograma geral"},
    {"id": "cc02", "grupo": "12 meses antes", "tarefa": "Auxílio na definição e controle do orçamento do casamento"},
    {"id": "cc03", "grupo": "9 meses antes",  "tarefa": "Apresentação e validação de propostas de fornecedores essenciais (Buffet, Fotografia, Decoração)"},
    {"id": "cc04", "grupo": "6 meses antes",  "tarefa": "Reunião técnica para alinhamento do layout físico do evento"},
    {"id": "cc05", "grupo": "6 meses antes",  "tarefa": "Verificar documentações exigidas para o casamento civil/religioso com efeitos civis"},
    {"id": "cc06", "grupo": "3 meses antes",  "tarefa": "Revisão geral de todos os contratos de fornecedores fechados até o momento"},
    {"id": "cc07", "grupo": "2 meses antes",  "tarefa": "Início da elaboração do roteiro detalhado do dia do evento"},
    {"id": "cc08", "grupo": "2 meses antes",  "tarefa": "Enviar cronograma macro do evento para alinhamento de fornecedores parceiros"},
    {"id": "cc09", "grupo": "2 meses antes",  "tarefa": "Reunião de alinhamento técnico de som, luz, imagem e decoração"},
    {"id": "cc10", "grupo": "1 mês antes",    "tarefa": "Enviar roteiro oficial final detalhado para todos os fornecedores contratados"},
    {"id": "cc11", "grupo": "1 mês antes",    "tarefa": "Realizar vistoria técnica final no local da cerimônia e recepção"},
    {"id": "cc12", "grupo": "1 semana antes", "tarefa": "Confirmar horários exatos de montagem, chegada e saída de todas as equipes"},
    {"id": "cc13", "grupo": "1 semana antes", "tarefa": "Coordenar o ensaio prático do cortejo com noivos, pais e padrinhos"},
    {"id": "cc14", "grupo": "1 semana antes", "tarefa": "Elaborar o checklist de materiais e itens pessoais da noiva para o dia do casamento"},
    {"id": "cc15", "grupo": "1 semana antes", "tarefa": "Recebimento de cheques/envelopes de pagamentos finais destinados aos fornecedores"},
]

CHECKLIST_NOIVOS_PADRAO = [
    {"id": "cn01", "grupo": "12 meses antes", "tarefa": "Definir a data do casamento e reservar o local da cerimônia/recepção"},
    {"id": "cn02", "grupo": "12 meses antes", "tarefa": "Contratar o cerimonialista / assessoria"},
    {"id": "cn03", "grupo": "12 meses antes", "tarefa": "Definir o orçamento máximo de investimento para o evento"},
    {"id": "cn04", "grupo": "12 meses antes", "tarefa": "Elaborar a primeira lista preliminar de convidados"},
    {"id": "cn05", "grupo": "9 meses antes",  "tarefa": "Contratar fotógrafo e cinegrafista (videomaker)"},
    {"id": "cn06", "grupo": "9 meses antes",  "tarefa": "Escolher buffet, decoração e serviços de bar"},
    {"id": "cn07", "grupo": "9 meses antes",  "tarefa": "Pesquisar roteiros e pacotes para a Lua de Mel"},
    {"id": "cn08", "grupo": "6 meses antes",  "tarefa": "Definir o vestido de noiva e acessórios (véu, grinalda, sapatos)"},
    {"id": "cn09", "grupo": "6 meses antes",  "tarefa": "Escolher o traje do noivo e sapatos"},
    {"id": "cn10", "grupo": "6 meses antes",  "tarefa": "Convidar formalmente os padrinhos, madrinhas, pajens e daminhas"},
    {"id": "cn11", "grupo": "6 meses antes",  "tarefa": "Criar o site dos noivos e definir a lista de presentes virtuais/físicos"},
    {"id": "cn12", "grupo": "6 meses antes",  "tarefa": "Agendar e realizar a sessão fotográfica de pré-wedding"},
    {"id": "cn13", "grupo": "3 meses antes",  "tarefa": "Escolher e encomendar as alianças do casal"},
    {"id": "cn14", "grupo": "3 meses antes",  "tarefa": "Realizar a degustação final de doces, bolo e pratos do buffet"},
    {"id": "cn15", "grupo": "3 meses antes",  "tarefa": "Enviar os convites físicos ou digitais para todos os convidados"},
    {"id": "cn16", "grupo": "2 meses antes",  "tarefa": "Entregar as lembranças/convites especiais dos padrinhos, pajens e daminhas"},
    {"id": "cn17", "grupo": "2 meses antes",  "tarefa": "Contratar maquiagem e cabelo da noiva e noivo (Dia da Noiva/Noivo)"},
    {"id": "cn18", "grupo": "1 mês antes",    "tarefa": "Dar entrada na documentação do casamento civil no Cartório"},
    {"id": "cn19", "grupo": "1 mês antes",    "tarefa": "Acompanhar e atualizar o controle de RSVP (confirmações de presença)"},
    {"id": "cn20", "grupo": "1 mês antes",    "tarefa": "Fazer as últimas provas do vestido de noiva e terno do noivo"},
    {"id": "cn21", "grupo": "1 semana antes", "tarefa": "Preparar as malas e documentos para a viagem de Lua de Mel"},
    {"id": "cn22", "grupo": "1 semana antes", "tarefa": "Retirar o vestido de noiva e traje do noivo nos ateliês"},
    {"id": "cn23", "grupo": "1 semana antes", "tarefa": "Participar do ensaio geral da cerimônia no local reservado"},
]

CHECKLIST_PADRAO = CHECKLIST_CERIMONIAL_PADRAO + CHECKLIST_NOIVOS_PADRAO

ROTEIRO_PADRAO = [
    {"HORÁRIO": "09:00", "MOMENTO": "Início da montagem do salão",               "RESPONSÁVEL": "Decoração",       "LOCAL": "Salão",           "OBSERVAÇÃO": ""},
    {"HORÁRIO": "12:00", "MOMENTO": "Chegada do buffet e montagem da cozinha",   "RESPONSÁVEL": "Buffet",          "LOCAL": "Cozinha",         "OBSERVAÇÃO": ""},
    {"HORÁRIO": "14:00", "MOMENTO": "Instalação de som, luz e pista de dança",   "RESPONSÁVEL": "Luz / Som",       "LOCAL": "Salão",           "OBSERVAÇÃO": ""},
    {"HORÁRIO": "16:00", "MOMENTO": "Ensaio fotográfico pré-cerimônia",          "RESPONSÁVEL": "Fotógrafo",       "LOCAL": "Local cerimônia", "OBSERVAÇÃO": ""},
    {"HORÁRIO": "17:00", "MOMENTO": "Chegada dos padrinhos e madrinhas",         "RESPONSÁVEL": "Cerimonialista",  "LOCAL": "Cerimônia",       "OBSERVAÇÃO": ""},
    {"HORÁRIO": "17:30", "MOMENTO": "Abertura dos portões para convidados",      "RESPONSÁVEL": "Segurança",       "LOCAL": "Entrada",         "OBSERVAÇÃO": ""},
    {"HORÁRIO": "18:00", "MOMENTO": "Início da cerimônia",                       "RESPONSÁVEL": "Celebrante",      "LOCAL": "Cerimônia",       "OBSERVAÇÃO": ""},
    {"HORÁRIO": "18:05", "MOMENTO": "Entrada dos padrinhos",                     "RESPONSÁVEL": "Cerimonialista",  "LOCAL": "Cerimônia",       "OBSERVAÇÃO": ""},
    {"HORÁRIO": "18:15", "MOMENTO": "Entrada da noiva",                          "RESPONSÁVEL": "Cerimonialista",  "LOCAL": "Cerimônia",       "OBSERVAÇÃO": ""},
    {"HORÁRIO": "18:45", "MOMENTO": "Encerramento da cerimônia / saída dos noivos", "RESPONSÁVEL": "Celebrante",  "LOCAL": "Cerimônia",       "OBSERVAÇÃO": ""},
    {"HORÁRIO": "19:00", "MOMENTO": "Início do coquetel",                        "RESPONSÁVEL": "Buffet",          "LOCAL": "Área coquetel",   "OBSERVAÇÃO": ""},
    {"HORÁRIO": "19:30", "MOMENTO": "Sessão de fotos dos noivos",                "RESPONSÁVEL": "Fotógrafo",       "LOCAL": "Jardim",          "OBSERVAÇÃO": ""},
    {"HORÁRIO": "20:30", "MOMENTO": "Abertura do salão / entrada dos convidados","RESPONSÁVEL": "Cerimonialista",  "LOCAL": "Salão",           "OBSERVAÇÃO": ""},
    {"HORÁRIO": "21:00", "MOMENTO": "Entrada dos noivos no salão",               "RESPONSÁVEL": "Cerimonialista",  "LOCAL": "Salão",           "OBSERVAÇÃO": ""},
    {"HORÁRIO": "21:15", "MOMENTO": "Primeira dança dos noivos",                 "RESPONSÁVEL": "DJ / Banda",      "LOCAL": "Pista",           "OBSERVAÇÃO": ""},
    {"HORÁRIO": "21:30", "MOMENTO": "Jantar",                                    "RESPONSÁVEL": "Buffet",          "LOCAL": "Salão",           "OBSERVAÇÃO": ""},
    {"HORÁRIO": "22:30", "MOMENTO": "Corte do bolo",                             "RESPONSÁVEL": "Cerimonialista",  "LOCAL": "Salão",           "OBSERVAÇÃO": ""},
    {"HORÁRIO": "22:45", "MOMENTO": "Animação e música ao vivo",                 "RESPONSÁVEL": "Banda / DJ",      "LOCAL": "Pista",           "OBSERVAÇÃO": ""},
    {"HORÁRIO": "23:00", "MOMENTO": "Jogamento do buquê",                        "RESPONSÁVEL": "Cerimonialista",  "LOCAL": "Pista",           "OBSERVAÇÃO": ""},
    {"HORÁRIO": "00:30", "MOMENTO": "Despedida e encerramento do evento",        "RESPONSÁVEL": "Cerimonialista",  "LOCAL": "Salão",           "OBSERVAÇÃO": ""},
]

BRIEFING_DEFAULTS = {
    "estilo": "", "convidados": "", "cores": "",
    "alimentar": "", "musica": "", "obs": "",
}

LARGURAS_PADRAO = {
    "SETOR": 180,
    "EMPRESA": 180,
    "RESPONSÁVEL": 150,
    "CEL/TEL": 120,
    "VALOR CONTRATO": 120,
    "HORA EXTRA": 120,
    "INSTAGRAM": 120,
    "OBSERVAÇÃO": 300,
    "STATUS": 180,
}

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _novo_evento(noivos: str, data: str) -> dict:
    """Cria estrutura completa de um novo evento."""
    return {
        "noivos": noivos,
        "data": data,
        "fornecedores": [
            {"SETOR": s, "EMPRESA": "", "RESPONSÁVEL": "", "CEL/TEL": "",
             "HORA EXTRA": 0.0, "VALOR CONTRATO": 0.0, "INSTAGRAM": "", "OBSERVAÇÃO": "", "STATUS": "Orçando"}
            for s in SETORES_PADRAO
        ],
        "checklist_cerimonial": [
            {"id": item["id"], "grupo": item["grupo"], "tarefa": item["tarefa"], "feito": False}
            for item in CHECKLIST_CERIMONIAL_PADRAO
        ],
        "checklist_noivos": [
            {"id": item["id"], "grupo": item["grupo"], "tarefa": item["tarefa"], "feito": False}
            for item in CHECKLIST_NOIVOS_PADRAO
        ],
        "briefing": dict(BRIEFING_DEFAULTS),
        "roteiro": [r.copy() for r in ROTEIRO_PADRAO],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CONEXÃO SUPABASE
# ═══════════════════════════════════════════════════════════════════════════════
try:
    SUPABASE_URL = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
except Exception:
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        supabase_client = None
else:
    supabase_client = None


def _dados_iniciais() -> dict:
    return {
        "usuarios": {
            "atcerimonial": {"senha": "Linhares@26", "tipo": "admin"},
            "maria_joao":  {"senha": "at01",  "tipo": "cliente", "evento_id": "ev_01"},
        },
        "eventos": {
            "ev_01": _novo_evento("Maria & João", "10/10/2026"),
        },
    }


def carregar_dados() -> dict:
    dados = None
    if supabase_client:
        try:
            response = supabase_client.table("at_cerimonial").select("data").eq("id", "dados_sistema").execute()
            if response.data:
                dados = response.data[0]["data"]
            else:
                if os.path.exists(DB_FILE):
                    try:
                        with open(DB_FILE, "r", encoding="utf-8") as f:
                            dados = json.load(f)
                    except Exception:
                        dados = _dados_iniciais()
                else:
                    dados = _dados_iniciais()
                supabase_client.table("at_cerimonial").insert({"id": "dados_sistema", "data": dados}).execute()
        except Exception as e:
            st.error(f"Erro ao carregar dados do Supabase: {e}")
            dados = None

    if dados is None:
        if not os.path.exists(DB_FILE):
            dados = _dados_iniciais()
            salvar_dados(dados)
            return dados
        with open(DB_FILE, "r", encoding="utf-8") as f:
            dados = json.load(f)
        
    # --- MIGRAÇÃO AUTOMÁTICA DE FORMATOS ANTIGOS ---
    modificado = False
    for ev_id, ev in dados.get("eventos", {}).items():
        # 1. Garantir coluna "VALOR CONTRATO" em fornecedores
        for forn in ev.get("fornecedores", []):
            if "VALOR CONTRATO" not in forn:
                forn["VALOR CONTRATO"] = 0.0
                modificado = True
                
        # 2. Migração do Checklist Único para split (Cerimonial + Noivos)
        if "checklist" in ev:
            old_checklist = ev.pop("checklist")
            if isinstance(old_checklist, dict):
                new_list = []
                for item in CHECKLIST_PADRAO:
                    new_list.append({
                        "id": item["id"],
                        "grupo": item["grupo"],
                        "tarefa": item["tarefa"],
                        "feito": old_checklist.get(item["id"], False)
                    })
                old_checklist = new_list
            
            # Atribui o antigo ao Cerimonial
            ev["checklist_cerimonial"] = old_checklist
            # Inicializa Noivos com padrão
            ev["checklist_noivos"] = [
                {"id": item["id"], "grupo": item["grupo"], "tarefa": item["tarefa"], "feito": False}
                for item in CHECKLIST_NOIVOS_PADRAO
            ]
            modificado = True

        if "checklist_cerimonial" not in ev:
            ev["checklist_cerimonial"] = [
                {"id": item["id"], "grupo": item["grupo"], "tarefa": item["tarefa"], "feito": False}
                for item in CHECKLIST_CERIMONIAL_PADRAO
            ]
            modificado = True

        if "checklist_noivos" not in ev:
            ev["checklist_noivos"] = [
                {"id": item["id"], "grupo": item["grupo"], "tarefa": item["tarefa"], "feito": False}
                for item in CHECKLIST_NOIVOS_PADRAO
            ]
            modificado = True
            
        # 3. Garantir que "feito" seja booleano (não NaN ou None) em ambos os checklists
        for key in ["checklist_cerimonial", "checklist_noivos"]:
            if isinstance(ev.get(key), list):
                for item in ev[key]:
                    val = item.get("feito")
                    if pd.isna(val) or val is None:
                        item["feito"] = False
                        modificado = True
            
    if modificado:
        salvar_dados(dados)
        
    return dados


def salvar_dados(dados: dict) -> None:
    if supabase_client:
        try:
            supabase_client.table("at_cerimonial").update({"data": dados}).eq("id", "dados_sistema").execute()
            return
        except Exception as e:
            st.error(f"Erro ao salvar dados no Supabase: {e}")
            
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)



def toggle_checklist_item(ev_id: str, item_id: str, key: str, tipo_ck: str) -> None:
    ev = dados["eventos"].get(ev_id)
    if ev:
        lista_nome = "checklist_cerimonial" if tipo_ck == "cerimonial" else "checklist_noivos"
        for item in ev.get(lista_nome, []):
            if item["id"] == item_id:
                item["feito"] = st.session_state[key]
                salvar_dados(dados)
                st.toast("Checklist salvo!", icon="✅")
                break


def update_briefing_field(ev_id: str, field_name: str, key: str) -> None:
    ev = dados["eventos"].get(ev_id)
    if ev:
        if "briefing" not in ev:
            ev["briefing"] = {}
        ev["briefing"][field_name] = st.session_state[key]
        salvar_dados(dados)
        st.toast("Briefing atualizado!", icon="📝")


def get_ev(dados: dict, ev_id: str) -> dict:
    """Acesso seguro a um evento. Nunca usar dados[ev_id] diretamente."""
    return dados["eventos"][ev_id]


def gerar_ev_id() -> str:
    return "ev_" + "".join(random.choices(string.digits, k=6))


def gerar_senha(n: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def obter_link_acesso(ev_id: str) -> str:
    try:
        from streamlit.web.server.websocket_headers import _get_websocket_headers
        headers = _get_websocket_headers()
        if headers:
            host = headers.get("Host")
            if host and "localhost" not in host and "127.0.0.1" not in host:
                proto = headers.get("X-Forwarded-Proto", "https" if "streamlit.app" in host else "http")
                return f"{proto}://{host}/?ev={ev_id}"
    except Exception:
        pass
    
    if os.name == 'nt':
        return f"http://localhost:8501/?ev={ev_id}"
    return f"https://sistema-atcerimonial.streamlit.app/?ev={ev_id}"



def exportar_excel(evento: dict) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        pd.DataFrame(evento["fornecedores"]).to_excel(
            writer, sheet_name="Fornecedores", index=False
        )
        pd.DataFrame(evento.get("roteiro", ROTEIRO_PADRAO)).to_excel(
            writer, sheet_name="Roteiro", index=False
        )
    buf.seek(0)
    return buf.getvalue()


def get_checklist_cerimonial(evento: dict) -> list:
    return evento.get("checklist_cerimonial", [])


def get_checklist_noivos(evento: dict) -> list:
    return evento.get("checklist_noivos", [])


def get_briefing(evento: dict) -> dict:
    return {**BRIEFING_DEFAULTS, **evento.get("briefing", {})}


def bf_field(label: str, valor) -> None:
    """Renderiza campo de briefing em modo leitura."""
    val_str = str(valor) if pd.notna(valor) and valor is not None else ""
    conteudo = val_str.strip() if val_str.strip() else "<em style='opacity:0.45;'>Não informado</em>"
    st.markdown(
        f"<div class='bf-field'><div class='bf-label'>{label}</div>{conteudo}</div>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# DADOS & SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
dados = carregar_dados()

_ss_defaults = {
    "logado": False, "usuario": None, "tipo_usuario": None, "evento_id": None,
    "edit_forn_ver": 0, "edit_rot_ver": 0, "novo_ev_cred": None, "sel_ev": None,
}
for k, v in _ss_defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Recupera sessão por link direto do evento (ex: ?ev=ev_01) ou por parâmetro de sessão (F5)
if not st.session_state.logado:
    # 1. Verifica se está acessando via link direto de evento
    ev_id_url = st.query_params.get("evento") or st.query_params.get("ev")
    if ev_id_url and ev_id_url in dados.get("eventos", {}):
        st.session_state.update(
            logado=True,
            usuario=f"noivos_{ev_id_url}",
            tipo_usuario="cliente",
            evento_id=ev_id_url,
        )
        st.rerun()
    
    # 2. Verifica sessão do admin persistida (F5)
    token_url = st.query_params.get("session")
    if token_url:
        usuario_encontrado = None
        for u_name, u_info in dados.get("usuarios", {}).items():
            if u_info.get("sessao_token") == token_url:
                usuario_encontrado = (u_name, u_info)
                break
        
        if usuario_encontrado:
            u_name, u_info = usuario_encontrado
            st.session_state.update(
                logado=True,
                usuario=u_name,
                tipo_usuario=u_info["tipo"],
                evento_id=u_info.get("evento_id"),
            )
            st.rerun()
        else:
            if "session" in st.query_params:
                del st.query_params["session"]

# ═══════════════════════════════════════════════════════════════════════════════
# TELA DE LOGIN
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logado:
    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.write("")
        st.write("")
        st.markdown(
            "<h1 class='notranslate' style='text-align:center; font-size:32px; margin-bottom:4px;'>💍 AT Cerimonial</h1>"
            "<p style='text-align:center; opacity:0.65; margin-bottom:28px;'>Gestão Integrada de Eventos</p>",
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            st.subheader("Acesso Restrito", divider=False)
            u = st.text_input("Usuário", key="li_user")
            s = st.text_input("Senha", type="password", key="li_pass")
            if st.button("Entrar no Painel", key="btn_login"):
                usr = dados["usuarios"].get(u)
                if usr and usr["senha"] == s:
                    # Gera token de sessão e salva na base de dados
                    token = "".join(random.choices(string.ascii_letters + string.digits, k=32))
                    usr["sessao_token"] = token
                    salvar_dados(dados)
                    st.query_params["session"] = token
                    st.session_state.update(
                        logado=True, usuario=u,
                        tipo_usuario=usr["tipo"],
                        evento_id=usr.get("evento_id"),
                    )
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")
        st.markdown(
            "<p class='notranslate' style='text-align:center; font-size:11px; opacity:0.45; margin-top:20px;'>AT Cerimonial © 2026</p>",
            unsafe_allow_html=True,
        )
    st.stop()

is_admin = st.session_state.tipo_usuario == "admin"

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("<h2 class='notranslate' style='margin:0 0 4px;'>AT Cerimonial</h2>", unsafe_allow_html=True)
    st.markdown(f"Perfil: **{st.session_state.tipo_usuario.upper()}**")
    st.markdown("<hr style='opacity:.15; margin:10px 0;'>", unsafe_allow_html=True)

    if is_admin:
        lista_ev = list(dados["eventos"].keys())
        # Valida sel_ev
        if st.session_state.sel_ev not in lista_ev:
            st.session_state.sel_ev = lista_ev[0]

        st.session_state.evento_id = st.selectbox(
            "Evento Ativo",
            lista_ev,
            index=lista_ev.index(st.session_state.sel_ev),
            format_func=lambda x: dados["eventos"][x]["noivos"],
            key="sb_ev",
        )
        st.session_state.sel_ev = st.session_state.evento_id

        full_link = obter_link_acesso(st.session_state.evento_id)

        # Exibe o link de acesso dos noivos para o evento ativo
        st.markdown("**🔗 Link de Acesso do Casal:**")
        import streamlit.components.v1 as components
        components.html(f"""
        <style>
          * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }}
          body {{ background: transparent; }}
          .link-container {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: #1E293B;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 10px 12px;
          }}
          .link-text {{
            flex: 1;
            color: #94A3B8;
            font-family: monospace;
            font-size: 12px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            user-select: all;
          }}
          .copy-btn {{
            flex-shrink: 0;
            background: #3B82F6;
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 6px 14px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 6px;
            white-space: nowrap;
          }}
          .copy-btn:hover {{ background: #2563EB; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(59,130,246,0.4); }}
          .copy-btn:active {{ transform: translateY(0); }}
          .copy-btn.success {{ background: #10B981; box-shadow: 0 4px 12px rgba(16,185,129,0.4); }}
          .copy-btn .icon {{ font-size: 14px; transition: all 0.3s; }}
        </style>
        <div class="link-container">
          <span class="link-text" title="{full_link}">{full_link}</span>
          <button class="copy-btn" id="copyBtn" onclick="copyLink()">
            <span class="icon">📋</span>
            <span id="btnText">Copiar</span>
          </button>
        </div>
        <script>
          function copyLink() {{
            var link = "{full_link}";
            if (navigator.clipboard && window.isSecureContext) {{
              navigator.clipboard.writeText(link).then(showSuccess);
            }} else {{
              var el = document.createElement('textarea');
              el.value = link;
              document.body.appendChild(el);
              el.select();
              document.execCommand('copy');
              document.body.removeChild(el);
              showSuccess();
            }}
          }}
          function showSuccess() {{
            var btn = document.getElementById('copyBtn');
            var txt = document.getElementById('btnText');
            btn.classList.add('success');
            btn.querySelector('.icon').textContent = '✅';
            txt.textContent = 'Copiado!';
            setTimeout(function() {{
              btn.classList.remove('success');
              btn.querySelector('.icon').textContent = '📋';
              txt.textContent = 'Copiar';
            }}, 2000);
          }}
        </script>
        """, height=55)

        st.markdown("<hr style='opacity:.15; margin:14px 0;'>", unsafe_allow_html=True)

        # ── Criar novo evento ──────────────────────────────────────────────
        with st.expander("➕ Criar Novo Evento"):
            with st.form("form_criar_ev", clear_on_submit=True):
                ne_noivos = st.text_input("Noivos", placeholder="Ex: Carla & Lucas")
                ne_data   = st.text_input("Data", placeholder="DD/MM/AAAA")
                criar_ok  = st.form_submit_button("✅ Criar Evento")

            if criar_ok:
                if not (ne_noivos and ne_data):
                    st.warning("Preencha todos os campos.")
                else:
                    # Formata a data se o usuário tiver digitado sem barras (ex: 28092026 -> 28/09/2026)
                    data_limpa = "".join(filter(str.isdigit, ne_data))
                    if len(data_limpa) == 8:
                        ne_data = f"{data_limpa[:2]}/{data_limpa[2:4]}/{data_limpa[4:]}"
                    elif len(data_limpa) == 6:
                        ne_data = f"{data_limpa[:2]}/{data_limpa[2:4]}/20{data_limpa[4:]}"

                    ev_id = gerar_ev_id()
                    dados["eventos"][ev_id] = _novo_evento(ne_noivos, ne_data)
                    salvar_dados(dados)
                    st.session_state.sel_ev = ev_id
                    st.session_state.novo_ev_cred = {
                        "noivos": ne_noivos, "ev_id": ev_id
                    }
                    st.rerun()

        # Exibe credenciais do evento recém-criado
        if st.session_state.novo_ev_cred:
            c = st.session_state.novo_ev_cred
            link_acesso = obter_link_acesso(c['ev_id'])
            st.success(
                f"🎉 Evento de **{c['noivos']}** criado com sucesso!\n\n"
                f"Envie o seguinte link de acesso aos noivos:\n"
                f"[Clique aqui para abrir]({link_acesso})\n\n"
                f"URL de acesso: `{link_acesso}`"
            )
            if st.button("✖ Fechar", key="btn_close_cred"):
                st.session_state.novo_ev_cred = None
                st.rerun()

        # ── Excluir evento ─────────────────────────────────────────────────
        if len(dados["eventos"]) > 1:
            with st.expander("🗑️ Excluir Evento"):
                ev_del = st.selectbox(
                    "Evento para excluir",
                    lista_ev,
                    format_func=lambda x: dados["eventos"][x]["noivos"],
                    key="sb_del",
                )
                confirm_del = st.checkbox("Confirmo a exclusão permanente", key="ck_del")
                if st.button("Excluir", key="btn_del"):
                    if confirm_del:
                        # Remove usuário associado
                        dados["usuarios"] = {
                            u: v for u, v in dados["usuarios"].items()
                            if not (v.get("tipo") == "cliente" and v.get("evento_id") == ev_del)
                        }
                        del dados["eventos"][ev_del]
                        salvar_dados(dados)
                        novo_sel = list(dados["eventos"].keys())[0]
                        st.session_state.sel_ev = novo_sel
                        st.session_state.evento_id = novo_sel
                        st.rerun()
                    else:
                        st.warning("Marque a confirmação.")

    else:
        # Perfil cliente: exibe info do evento
        ev_cli = get_ev(dados, st.session_state.evento_id)
        st.markdown(f"**{ev_cli['noivos']}**")
        st.markdown(f"📅 {ev_cli['data']}")

    st.markdown("<hr style='opacity:.15; margin:14px 0;'>", unsafe_allow_html=True)
    if st.button("🚪 Sair do Sistema", key="btn_logout"):
        u_name = st.session_state.usuario
        if u_name in dados.get("usuarios", {}):
            dados["usuarios"][u_name].pop("sessao_token", None)
            salvar_dados(dados)
        st.query_params.clear()
        for k in ["logado", "usuario", "tipo_usuario", "evento_id", "sel_ev", "novo_ev_cred"]:
            st.session_state[k] = False if k == "logado" else None
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# EVENTO ATIVO
# ═══════════════════════════════════════════════════════════════════════════════
evento_atual = get_ev(dados, st.session_state.evento_id)

# ═══════════════════════════════════════════════════════════════════════════════
# ABAS
# ═══════════════════════════════════════════════════════════════════════════════
if is_admin:
    t_dash, t_brief, t_cerim, t_noivos, t_forn, t_rot = st.tabs([
        "📊 Dashboard",
        "📝 Briefing",
        "📋 Checklist Cerimonial",
        "💍 Checklist Noivos",
        "🤝 Fornecedores",
        "⏱️ Roteiro",
    ])
else:
    t_dash, t_brief, t_noivos, t_forn, t_rot = st.tabs([
        "📊 Dashboard",
        "📝 Briefing",
        "💍 Checklist Noivos",
        "🤝 Fornecedores",
        "⏱️ Roteiro",
    ])
    t_cerim = None

# ───────────────────────────────────────────────────────────────────────────────
# TAB 0 — DASHBOARD
# ───────────────────────────────────────────────────────────────────────────────
with t_dash:
    st.markdown(f"### Dashboard — {evento_atual['noivos']}  ·  📅 {evento_atual['data']}")

    # ⏳ Contagem Regressiva
    from datetime import datetime
    try:
        data_val = str(evento_atual["data"]) if pd.notna(evento_atual["data"]) else ""
        data_evento_str = data_val.strip()
        data_evento = datetime.strptime(data_evento_str, "%d/%m/%Y")
        hoje = datetime.now()
        delta = data_evento - hoje
        dias = delta.days + 1
        
        if dias > 0:
            st.info(f"💍 **Faltam {dias} dias para o grande dia! ({evento_atual['data']})**")
        elif dias == 0:
            st.success(f"🎉 **É hoje! O grande dia chegou! 💍**")
        else:
            st.success(f"✨ **O casamento aconteceu em {evento_atual['data']}! 🎉**")
    except Exception:
        st.warning(f"📅 Data do evento cadastrada: **{evento_atual['data']}** (insira no formato DD/MM/AAAA para habilitar contagem)")

    df_f  = pd.DataFrame(evento_atual["fornecedores"])
    total = len(df_f)

    contratados = int((df_f["STATUS"] == "CONTRATADO").sum())
    nao_havera  = int((df_f["STATUS"] == "Não haverá").sum())
    em_negoc    = int(df_f["STATUS"].isin([
        "Dados enviados", "Contrato recebido",
        "Análise concluída / liberado para assinatura",
        "Aguardando assinatura do CONTRATADO",
    ]).sum())
    orcando     = int((df_f["STATUS"] == "Orçando").sum())
    ativos      = total - nao_havera

    # Métricas Financeiras
    total_orcado = float(df_f["VALOR CONTRATO"].sum())
    pago_contratado = float(df_f[df_f["STATUS"] == "CONTRATADO"]["VALOR CONTRATO"].sum())
    valor_negociacao = float(df_f[df_f["STATUS"].isin([
        "Dados enviados", "Contrato recebido",
        "Análise concluída / liberado para assinatura",
        "Aguardando assinatura do CONTRATADO",
    ])]["VALOR CONTRATO"].sum())

    st.markdown("#### 💰 Painel Financeiro & Contratações")
    c_fin1, c_fin2, c_fin3, c_fin4 = st.columns(4)
    c_fin1.metric("Orçamento Total (Preenchido)", f"R$ {total_orcado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c_fin2.metric("✅ Total Contratado (Fechado)", f"R$ {pago_contratado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c_fin3.metric("🔄 Em Negociação", f"R$ {valor_negociacao:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c_fin4.metric("📊 Setores Ativos", f"{contratados} de {ativos}")

    # Progresso Geral
    st.write("")
    pct_geral = contratados / ativos if ativos > 0 else 0
    st.markdown(f"**Progresso de contratação:** {contratados} de {ativos} setores ativos  **({pct_geral:.0%})**")
    st.progress(pct_geral)

    # Gráficos
    st.write("")
    cg1, cg2 = st.columns(2)
    with cg1:
        st.markdown("##### 📊 Quantidade por Status")
        df_status_counts = df_f["STATUS"].value_counts().reset_index()
        df_status_counts.columns = ["Status", "Quantidade"]
        st.bar_chart(df_status_counts.set_index("Status"), height=250)
        
    with cg2:
        st.markdown("##### 💸 Maiores Contratos (R$)")
        df_money = df_f[df_f["VALOR CONTRATO"] > 0][["SETOR", "VALOR CONTRATO"]].sort_values(by="VALOR CONTRATO", ascending=False).head(8)
        if not df_money.empty:
            st.bar_chart(df_money.set_index("SETOR"), height=250)
        else:
            st.info("Preencha a coluna 'Valor Contrato' na aba Fornecedores para ver a distribuição financeira.")

    # Status por etapa (barras de progresso)
    st.write("")
    with st.expander("🔍 Ver Acompanhamento Detalhado por Etapa"):
        for opt in STATUS_OPCOES:
            qtd  = int((df_f["STATUS"] == opt).sum())
            pct_s = (qtd / total * 100) if total > 0 else 0
            cor  = STATUS_CORES[opt]
            st.markdown(f"""
            <div style='margin-bottom:10px;'>
                <div style='display:flex; justify-content:space-between; margin-bottom:3px;'>
                    <small style='font-weight:600;'>{opt}</small>
                    <small style='opacity:0.6;'>{qtd} setor(es)</small>
                </div>
                <div style='background:rgba(100,116,139,0.2); height:10px; border-radius:5px; overflow:hidden;'>
                    <div style='background:{cor}; width:{pct_s:.1f}%; height:100%; transition:width .3s;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Lista de urgências
    df_urgente = df_f[df_f["STATUS"] == "Orçando"]
    if not df_urgente.empty:
        st.write("")
        st.markdown(f"#### ⚠️ Atenção — {len(df_urgente)} setor(es) ainda sem fornecedor definido")
        for _, row in df_urgente.iterrows():
            emp_val = str(row["EMPRESA"]) if pd.notna(row["EMPRESA"]) and row["EMPRESA"] is not None else ""
            emp = emp_val.strip() if emp_val.strip() else "Empresa não definida"
            st.markdown(
                f"<div class='alert-row'>🔴 <b>{row['SETOR']}</b> — {emp}</div>",
                unsafe_allow_html=True,
            )

# ───────────────────────────────────────────────────────────────────────────────
# TAB — BRIEFING INICIAL
# ───────────────────────────────────────────────────────────────────────────────
with t_brief:
    st.markdown(f"### Briefing Inicial — {evento_atual['noivos']}")
    briefing = get_briefing(evento_atual)

    if is_admin or st.session_state.tipo_usuario == "cliente":
        st.text_area(
            "Estilo do evento / referências visuais",
            value=briefing["estilo"],
            placeholder="Ex: Rústico chic, paleta verde e terracota, ao ar livre…",
            height=80,
            key=f"bf_estilo_{st.session_state.evento_id}",
            on_change=update_briefing_field,
            args=(st.session_state.evento_id, "estilo", f"bf_estilo_{st.session_state.evento_id}")
        )
        st.text_input(
            "Número estimado de convidados",
            value=briefing["convidados"],
            key=f"bf_convidados_{st.session_state.evento_id}",
            on_change=update_briefing_field,
            args=(st.session_state.evento_id, "convidados", f"bf_convidados_{st.session_state.evento_id}")
        )
        st.text_input(
            "Paleta de cores principal",
            value=briefing["cores"],
            placeholder="Ex: Branco, verde esmeralda e dourado",
            key=f"bf_cores_{st.session_state.evento_id}",
            on_change=update_briefing_field,
            args=(st.session_state.evento_id, "cores", f"bf_cores_{st.session_state.evento_id}")
        )
        st.text_area(
            "Restrições alimentares / observações do buffet",
            value=briefing["alimentar"],
            placeholder="Ex: 3 vegetarianos, 1 celíaco, sem glúten na mesa 5…",
            height=70,
            key=f"bf_alimentar_{st.session_state.evento_id}",
            on_change=update_briefing_field,
            args=(st.session_state.evento_id, "alimentar", f"bf_alimentar_{st.session_state.evento_id}")
        )
        st.text_area(
            "Preferências musicais",
            value=briefing["musica"],
            placeholder="Ex: MPB e sertanejo raiz; evitar funk e pagode…",
            height=70,
            key=f"bf_musica_{st.session_state.evento_id}",
            on_change=update_briefing_field,
            args=(st.session_state.evento_id, "musica", f"bf_musica_{st.session_state.evento_id}")
        )
        st.text_area(
            "Observações gerais",
            value=briefing["obs"],
            height=90,
            key=f"bf_obs_{st.session_state.evento_id}",
            on_change=update_briefing_field,
            args=(st.session_state.evento_id, "obs", f"bf_obs_{st.session_state.evento_id}")
        )
        st.caption("✨ As alterações no briefing são salvas automaticamente.")
    else:
        st.info("🔒 Briefing registrado pelo cerimonial.")
        bf_field("Estilo do evento",         briefing["estilo"])
        bf_field("Convidados estimados",      briefing["convidados"])
        bf_field("Paleta de cores",           briefing["cores"])
        bf_field("Restrições alimentares",    briefing["alimentar"])
        bf_field("Preferências musicais",     briefing["musica"])
        bf_field("Observações gerais",        briefing["obs"])

# ───────────────────────────────────────────────────────────────────────────────
# TAB 1 — FORNECEDORES
# ───────────────────────────────────────────────────────────────────────────────
with t_forn:
    st.markdown(f"### Alinhamento com Fornecedores — {evento_atual['noivos']}")

    # Filtros e Toggle de Edição
    cf1, cf2, cf3 = st.columns([2.5, 2.5, 5])
    with cf1:
        filtro = st.selectbox(
            "Filtrar por status", ["Todos"] + STATUS_OPCOES, key="filt_status"
        )
    with cf2:
        busca = st.text_input("Buscar setor / empresa", placeholder="Digite…", key="busca_forn")
    with cf3:
        st.write("")
        st.write("")
        if is_admin or st.session_state.tipo_usuario == "cliente":
            modo_edicao = st.toggle("✏️ Modo Edição", value=False, key="toggle_edit_forn")
        else:
            modo_edicao = False

    # Monta DataFrame completo preservando índices originais
    df_full = pd.DataFrame(evento_atual["fornecedores"])
    df_view = df_full.copy()

    if filtro != "Todos":
        df_view = df_view[df_view["STATUS"] == filtro]
    if busca:
        df_view = df_view[
            df_view["SETOR"].str.contains(busca, case=False, na=False) |
            df_view["EMPRESA"].str.contains(busca, case=False, na=False)
        ]

    widths = evento_atual.get("col_widths", LARGURAS_PADRAO)

    col_cfg = {
        "SETOR":          st.column_config.TextColumn("Setor",        disabled=True, width=widths.get("SETOR", 180), pinned=True),
        "EMPRESA":        st.column_config.TextColumn("Empresa",      width=widths.get("EMPRESA", 180)),
        "RESPONSÁVEL":    st.column_config.TextColumn("Responsável",  width=widths.get("RESPONSÁVEL", 150)),
        "CEL/TEL":        st.column_config.TextColumn("Cel/Tel",      width=widths.get("CEL/TEL", 120)),
        "VALOR CONTRATO": st.column_config.NumberColumn("Valor Contrato", format="R$ %.2f", width=widths.get("VALOR CONTRATO", 120)),
        "HORA EXTRA":     st.column_config.NumberColumn("Hora Extra (R$)", format="R$ %.2f", width=widths.get("HORA EXTRA", 120)),
        "INSTAGRAM":      st.column_config.TextColumn("Instagram",    width=widths.get("INSTAGRAM", 120)),
        "OBSERVAÇÃO":     st.column_config.TextColumn("Observação",   width=widths.get("OBSERVAÇÃO", 300)),
        "STATUS":         st.column_config.SelectboxColumn("Status",  options=STATUS_OPCOES, required=True, width=widths.get("STATUS", 180)),
    }

    # Função para colorir linhas no DataFrame de acordo com o status
    def colorir_linhas(row):
        status = row.get("STATUS", "Orçando")
        cores_fundo = {
            "Orçando":                                              "background-color: #FEE2E2; color: #991B1B;",
            "Dados enviados":                                       "background-color: #DBEAFE; color: #1E40AF;",
            "Contrato recebido":                                    "background-color: #FEF3C7; color: #92400E;",
            "Análise concluída / liberado para assinatura":         "background-color: #F3E8FF; color: #6B21A8;",
            "Aguardando assinatura do CONTRATADO":                  "background-color: #ECFEFF; color: #155E75;",
            "CONTRATADO":                                           "background-color: #D1FAE5; color: #065F46;",
            "Não haverá":                                           "background-color: #F1F5F9; color: #475569;",
        }
        estilo_base = cores_fundo.get(status, "")
        
        styles = []
        for col in row.index:
            if col == "SETOR":
                styles.append(estilo_base + " font-weight: bold;")
            else:
                styles.append(estilo_base)
        return styles

    if modo_edicao:
        df_edit = st.data_editor(
            df_view,
            column_config=col_cfg,
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            key=f"ed_forn_{st.session_state.evento_id}",
        )

        if not df_edit.equals(df_view):
            idx_vis = df_view.index.tolist()
            for i, orig_idx in enumerate(idx_vis):
                for col in df_full.columns:
                    if col != "SETOR":
                        df_full.at[orig_idx, col] = df_edit.iloc[i][col]
            evento_atual["fornecedores"] = df_full.to_dict(orient="records")
            salvar_dados(dados)
            st.toast("Fornecedores salvos!", icon="💾")
            st.rerun()

        st.caption("✨ As alterações na tabela de fornecedores são salvas automaticamente.")
    else:
        st.dataframe(
            df_view.style.apply(colorir_linhas, axis=1),
            column_config=col_cfg,
            hide_index=True,
            use_container_width=True,
        )

    # Botão de exportar (visível em ambos os modos para quem tem acesso de edição)
    if is_admin or st.session_state.tipo_usuario == "cliente":
        st.write("")
        cb1, _ = st.columns([2.5, 9.5])
        with cb1:
            excel_bytes = exportar_excel(evento_atual)
            st.download_button(
                "📥 Exportar Excel",
                data=excel_bytes,
                file_name=f"AT_{evento_atual['noivos'].replace(' ', '_').replace('&','e')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_forn",
            )

        if is_admin:
            # ⚙️ Expander para ajustar largura das colunas (em pixels)
            with st.expander("⚙️ Ajustar Largura das Colunas (em pixels)"):
                st.markdown("<small>Use os controles abaixo para definir a largura de cada coluna. As alterações são aplicadas e salvas automaticamente.</small>", unsafe_allow_html=True)
                
                new_widths = {}
                cols_width_selectors = st.columns(3)
                with cols_width_selectors[0]:
                    new_widths["SETOR"] = st.number_input("Setor", min_value=50, max_value=800, value=int(widths.get("SETOR", 180)), step=10, key="w_setor")
                    new_widths["EMPRESA"] = st.number_input("Empresa", min_value=50, max_value=800, value=int(widths.get("EMPRESA", 180)), step=10, key="w_empresa")
                    new_widths["RESPONSÁVEL"] = st.number_input("Responsável", min_value=50, max_value=800, value=int(widths.get("RESPONSÁVEL", 150)), step=10, key="w_resp")
                with cols_width_selectors[1]:
                    new_widths["CEL/TEL"] = st.number_input("Cel/Tel", min_value=50, max_value=800, value=int(widths.get("CEL/TEL", 120)), step=10, key="w_cel")
                    new_widths["VALOR CONTRATO"] = st.number_input("Valor Contrato", min_value=50, max_value=800, value=int(widths.get("VALOR CONTRATO", 120)), step=10, key="w_val")
                    new_widths["HORA EXTRA"] = st.number_input("Hora Extra", min_value=50, max_value=800, value=int(widths.get("HORA EXTRA", 120)), step=10, key="w_hora")
                with cols_width_selectors[2]:
                    new_widths["INSTAGRAM"] = st.number_input("Instagram", min_value=50, max_value=800, value=int(widths.get("INSTAGRAM", 120)), step=10, key="w_inst")
                    new_widths["OBSERVAÇÃO"] = st.number_input("Observação", min_value=50, max_value=1200, value=int(widths.get("OBSERVAÇÃO", 300)), step=10, key="w_obs")
                    new_widths["STATUS"] = st.number_input("Status", min_value=50, max_value=800, value=int(widths.get("STATUS", 180)), step=10, key="w_status")
                
                if any(new_widths[k] != widths.get(k) for k in LARGURAS_PADRAO):
                    evento_atual["col_widths"] = new_widths
                    salvar_dados(dados)
                    st.toast("Largura das colunas atualizada!", icon="⚙️")
                    st.rerun()

            # ➕/❌ Gerenciar Linhas (Setores de Fornecedores)
            with st.expander("➕ / 🗑️ Adicionar ou Excluir Linhas (Setores)"):
                st.markdown("<small>Adicione novos setores ou exclua setores existentes da sua lista de fornecedores.</small>", unsafe_allow_html=True)
                
                c_add, c_del = st.columns(2)
                with c_add:
                    st.markdown("**Adicionar Setor**")
                    nome_novo_setor = st.text_input("Nome do Setor", placeholder="Ex: Banda Extra, Barman...", key="add_setor_name")
                    if st.button("➕ Adicionar Setor", key="btn_add_setor"):
                        if nome_novo_setor.strip():
                            # Verifica duplicados
                            setores_existentes = [f["SETOR"].strip().lower() for f in evento_atual["fornecedores"]]
                            if nome_novo_setor.strip().lower() in setores_existentes:
                                st.error("Este setor já existe.")
                            else:
                                novo_forn = {
                                    "SETOR": nome_novo_setor.strip(),
                                    "EMPRESA": "",
                                    "RESPONSÁVEL": "",
                                    "CEL/TEL": "",
                                    "VALOR CONTRATO": 0.0,
                                    "HORA EXTRA": 0.0,
                                    "INSTAGRAM": "",
                                    "OBSERVAÇÃO": "",
                                    "STATUS": "Orçando"
                                }
                                evento_atual["fornecedores"].append(novo_forn)
                                salvar_dados(dados)
                                st.toast(f"Setor '{nome_novo_setor}' adicionado com sucesso!", icon="🎉")
                                st.rerun()
                        else:
                            st.warning("Digite o nome do setor.")
                
                with c_del:
                    st.markdown("**Excluir Setor**")
                    setores_lista = [f["SETOR"] for f in evento_atual["fornecedores"]]
                    setor_para_excluir = st.selectbox("Selecione o Setor para Excluir", setores_lista, key="del_setor_name")
                    if st.button("🗑️ Excluir Setor Selecionado", key="btn_del_setor"):
                        evento_atual["fornecedores"] = [f for f in evento_atual["fornecedores"] if f["SETOR"] != setor_para_excluir]
                        salvar_dados(dados)
                        st.toast(f"Setor '{setor_para_excluir}' excluído!", icon="🗑️")
                        st.rerun()
    else:
        st.info("🔒 Visualização de acompanhamento. Edições são realizadas pelo cerimonial.")
        st.dataframe(
            df_view.style.apply(colorir_linhas, axis=1),
            column_config=col_cfg,
            hide_index=True,
            use_container_width=True,
        )

# ───────────────────────────────────────────────────────────────────────────────
# TAB 2 — CHECKLIST MÊS A MÊS
# ───────────────────────────────────────────────────────────────────────────────
if is_admin and t_cerim:
    with t_cerim:
        st.markdown(f"### Checklist Cerimonial — {evento_atual['noivos']}")
        
        if is_admin:
            sub_checklist_cerim = st.radio("Seção", ["📊 Acompanhar Checklist", "⚙️ Gerenciar Tarefas"], horizontal=True, label_visibility="collapsed", key="sub_ck_cerim")
        else:
            sub_checklist_cerim = "📊 Acompanhar Checklist"
            
        checklist_cerim_items = get_checklist_cerimonial(evento_atual)

        if sub_checklist_cerim == "📊 Acompanhar Checklist":
            grupos = {}
            for item in checklist_cerim_items:
                grupos.setdefault(item["grupo"], []).append(item)

            states = {}
            for grupo, itens in grupos.items():
                feitos_g = sum(1 for i in itens if i["feito"])
                all_done = feitos_g == len(itens)
                label    = f"{'✅' if all_done else '🗓️'}  {grupo}  —  {feitos_g}/{len(itens)} concluídos"

                with st.expander(label, expanded=not all_done):
                    for item in itens:
                        val = item["feito"]
                        if is_admin or st.session_state.tipo_usuario == "cliente":
                            key_name = f"ck_cerim_{st.session_state.evento_id}_{item['id']}"
                            states[item["id"]] = st.checkbox(
                                item["tarefa"],
                                value=val,
                                key=key_name,
                                on_change=toggle_checklist_item,
                                args=(st.session_state.evento_id, item["id"], key_name, "cerimonial")
                            )
                        else:
                            states[item["id"]] = val
                            icone = "✅" if val else "⬜"
                            st.markdown(f"{icone} &nbsp; {item['tarefa']}")

            total_ck  = len(checklist_cerim_items)
            feitos_ck = sum(1 for i in checklist_cerim_items if i["feito"])
            st.write("")
            st.progress(feitos_ck / total_ck if total_ck else 0)
            st.markdown(f"**{feitos_ck} de {total_ck} tarefas concluídas**")

            if is_admin or st.session_state.tipo_usuario == "cliente":
                st.caption("✨ As alterações no checklist são salvas automaticamente.")
                    
        else:
            st.markdown("#### ⚙️ Gerenciar Tarefas")
            st.markdown("Adicione novas tarefas, exclua ou altere as categorias do checklist cerimonial.")
            
            df_ck_tasks = pd.DataFrame(checklist_cerim_items)
            if df_ck_tasks.empty:
                df_ck_tasks = pd.DataFrame(columns=["id", "grupo", "tarefa", "feito"])
                
            df_ck_edit = st.data_editor(
                df_ck_tasks,
                column_config={
                    "grupo": st.column_config.SelectboxColumn(
                        "Grupo / Período",
                        options=[
                            "12 meses antes", "9 meses antes", "6 meses antes",
                            "3 meses antes", "2 meses antes", "1 mês antes",
                            "1 semana antes", "No dia", "Pós-evento"
                        ],
                        required=True,
                        width="medium"
                    ),
                    "tarefa": st.column_config.TextColumn("Tarefa / Descrição", required=True, width="large"),
                    "feito": st.column_config.CheckboxColumn("Concluído", width="small")
                },
                column_order=["grupo", "tarefa", "feito"],
                hide_index=True,
                use_container_width=True,
                num_rows="dynamic",
                key="df_ck_cerim_editor"
            )
            
            if not df_ck_edit.equals(df_ck_tasks):
                new_tasks = []
                for i, row in df_ck_edit.iterrows():
                    row_dict = row.to_dict()
                    if not row_dict.get("id") or pd.isna(row_dict.get("id")) or str(row_dict.get("id")).strip() == "":
                        row_dict["id"] = "cc_" + "".join(random.choices(string.digits, k=6))
                    if pd.isna(row_dict.get("tarefa")):
                        row_dict["tarefa"] = ""
                    if "feito" not in row_dict or pd.isna(row_dict["feito"]) or row_dict["feito"] is None:
                        row_dict["feito"] = False
                    else:
                        row_dict["feito"] = bool(row_dict["feito"])
                    new_tasks.append(row_dict)
                    
                evento_atual["checklist_cerimonial"] = new_tasks
                salvar_dados(dados)
                st.toast("Checklist Cerimonial atualizado!", icon="⚙️")
                st.rerun()
                
            st.caption("✨ As alterações nas tarefas são salvas automaticamente.")

# ───────────────────────────────────────────────────────────────────────────────
# TAB — CHECKLIST NOIVOS
# ───────────────────────────────────────────────────────────────────────────────
with t_noivos:
    st.markdown(f"### Checklist Noivos — {evento_atual['noivos']}")
    
    if is_admin:
        sub_checklist_noivos = st.radio("Seção", ["📊 Acompanhar Checklist", "⚙️ Gerenciar Tarefas"], horizontal=True, label_visibility="collapsed", key="sub_ck_noivos")
    else:
        sub_checklist_noivos = "📊 Acompanhar Checklist"
        
    checklist_noivos_items = get_checklist_noivos(evento_atual)

    if sub_checklist_noivos == "📊 Acompanhar Checklist":
        grupos = {}
        for item in checklist_noivos_items:
            grupos.setdefault(item["grupo"], []).append(item)

        states = {}
        for grupo, itens in grupos.items():
            feitos_g = sum(1 for i in itens if i["feito"])
            all_done = feitos_g == len(itens)
            label    = f"{'✅' if all_done else '🗓️'}  {grupo}  —  {feitos_g}/{len(itens)} concluídos"

            with st.expander(label, expanded=not all_done):
                for item in itens:
                    val = item["feito"]
                    if is_admin or st.session_state.tipo_usuario == "cliente":
                        key_name = f"ck_noivos_{st.session_state.evento_id}_{item['id']}"
                        states[item["id"]] = st.checkbox(
                            item["tarefa"],
                            value=val,
                            key=key_name,
                            on_change=toggle_checklist_item,
                            args=(st.session_state.evento_id, item["id"], key_name, "noivos")
                        )
                    else:
                        states[item["id"]] = val
                        icone = "✅" if val else "⬜"
                        st.markdown(f"{icone} &nbsp; {item['tarefa']}")

        total_ck  = len(checklist_noivos_items)
        feitos_ck = sum(1 for i in checklist_noivos_items if i["feito"])
        st.write("")
        st.progress(feitos_ck / total_ck if total_ck else 0)
        st.markdown(f"**{feitos_ck} de {total_ck} tarefas concluídas**")

        if is_admin or st.session_state.tipo_usuario == "cliente":
            st.caption("✨ As alterações no checklist são salvas automaticamente.")
                
    else:
        st.markdown("#### ⚙️ Gerenciar Tarefas")
        st.markdown("Adicione novas tarefas, exclua ou altere as categorias do checklist dos noivos.")
        
        df_ck_tasks = pd.DataFrame(checklist_noivos_items)
        if df_ck_tasks.empty:
            df_ck_tasks = pd.DataFrame(columns=["id", "grupo", "tarefa", "feito"])
            
        df_ck_edit = st.data_editor(
            df_ck_tasks,
            column_config={
                "grupo": st.column_config.SelectboxColumn(
                    "Grupo / Período",
                    options=[
                        "12 meses antes", "9 meses antes", "6 meses antes",
                        "3 meses antes", "2 meses antes", "1 mês antes",
                        "1 semana antes", "No dia", "Pós-evento"
                    ],
                    required=True,
                    width="medium"
                ),
                "tarefa": st.column_config.TextColumn("Tarefa / Descrição", required=True, width="large"),
                "feito": st.column_config.CheckboxColumn("Concluído", width="small")
            },
            column_order=["grupo", "tarefa", "feito"],
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            key="df_ck_noivos_editor"
        )
        
        if not df_ck_edit.equals(df_ck_tasks):
            new_tasks = []
            for i, row in df_ck_edit.iterrows():
                row_dict = row.to_dict()
                if not row_dict.get("id") or pd.isna(row_dict.get("id")) or str(row_dict.get("id")).strip() == "":
                    row_dict["id"] = "cn_" + "".join(random.choices(string.digits, k=6))
                if pd.isna(row_dict.get("tarefa")):
                    row_dict["tarefa"] = ""
                if "feito" not in row_dict or pd.isna(row_dict["feito"]) or row_dict["feito"] is None:
                    row_dict["feito"] = False
                else:
                    row_dict["feito"] = bool(row_dict["feito"])
                new_tasks.append(row_dict)
                
            evento_atual["checklist_noivos"] = new_tasks
            salvar_dados(dados)
            st.toast("Checklist Noivos atualizado!", icon="⚙️")
            st.rerun()
            
        st.caption("✨ As alterações nas tarefas são salvas automaticamente.")

# ───────────────────────────────────────────────────────────────────────────────
# TAB 4 — ROTEIRO E CRONOGRAMA
# ───────────────────────────────────────────────────────────────────────────────
with t_rot:
    st.markdown(f"### Roteiro do Evento — {evento_atual['noivos']}")
    roteiro = evento_atual.get("roteiro", [r.copy() for r in ROTEIRO_PADRAO])
    df_rot  = pd.DataFrame(roteiro)

    rot_cfg = {
        "HORÁRIO":     st.column_config.TextColumn("Horário",     width="small"),
        "MOMENTO":     st.column_config.TextColumn("Momento",     width="large"),
        "RESPONSÁVEL": st.column_config.TextColumn("Responsável", width="medium"),
        "LOCAL":       st.column_config.TextColumn("Local",       width="medium"),
        "OBSERVAÇÃO":  st.column_config.TextColumn("Observação",  width="large"),
    }

    if is_admin:
        df_rot_edit = st.data_editor(
            df_rot,
            column_config=rot_cfg,
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            key=f"ed_rot_{st.session_state.evento_id}",
        )

        if not df_rot_edit.equals(df_rot):
            evento_atual["roteiro"] = df_rot_edit.to_dict(orient="records")
            salvar_dados(dados)
            st.toast("Roteiro salvo!", icon="⏱️")
            st.rerun()

        cr1, _ = st.columns([2.5, 9.5])
        with cr1:
            excel_rot = exportar_excel(evento_atual)
            st.download_button(
                "📥 Exportar Excel",
                data=excel_rot,
                file_name=f"AT_{evento_atual['noivos'].replace(' ', '_').replace('&','e')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_rot",
            )
        st.caption("✨ As alterações no roteiro são salvas automaticamente.")
    else:
        st.dataframe(df_rot, column_config=rot_cfg, hide_index=True, use_container_width=True)
