import streamlit as st
import pandas as pd
import json
import os
import io
import random
import string
import secrets
from supabase import create_client, Client

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
# CONEXÃO SUPABASE
# ═══════════════════════════════════════════════════════════════════════════════
try:
    SUPABASE_URL = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
except Exception:
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase_error = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        supabase_client = None
        supabase_error = str(e)
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

def gerar_link_token() -> str:
    return secrets.token_hex(12)

def _novo_evento(noivos: str, data: str) -> dict:
    return {
        "noivos": noivos,
        "data": data,
        "link_token": gerar_link_token(),
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
        
    modificado = False
    for ev_id, ev in dados.get("eventos", {}).items():
        for forn in ev.get("fornecedores", []):
            if "VALOR CONTRATO" not in forn:
                forn["VALOR CONTRATO"] = 0.0
                modificado = True
                
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
            
            ev["checklist_cerimonial"] = old_checklist
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
            
        for key in ["checklist_cerimonial", "checklist_noivos"]:
            if isinstance(ev.get(key), list):
                for item in ev[key]:
                    val = item.get("feito")
                    if pd.isna(val) or val is None:
                        item["feito"] = False
                        modificado = True
                        
        if "link_token" not in ev:
            ev["link_token"] = gerar_link_token()
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
    if "dados" not in st.session_state or st.session_state.dados is None:
        st.session_state.dados = carregar_dados()
    ev = st.session_state.dados["eventos"].get(ev_id)
    if ev:
        lista_nome = "checklist_cerimonial" if tipo_ck == "cerimonial" else "checklist_noivos"
        for item in ev.get(lista_nome, []):
            if item["id"] == item_id:
                item["feito"] = st.session_state[key]
                salvar_dados(st.session_state.dados)
                st.toast("Checklist salvo!", icon="✅")
                break

def update_briefing_field(ev_id: str, field_name: str, key: str) -> None:
    if "dados" not in st.session_state or st.session_state.dados is None:
        st.session_state.dados = carregar_dados()
    ev = st.session_state.dados["eventos"].get(ev_id)
    if ev:
        if "briefing" not in ev:
            ev["briefing"] = {}
        ev["briefing"][field_name] = st.session_state[key]
        salvar_dados(st.session_state.dados)
        st.toast("Briefing atualizado!", icon="📝")

def get_ev(dados: dict, ev_id: str) -> dict:
    return dados["eventos"][ev_id]

def gerar_ev_id() -> str:
    return "ev_" + "".join(random.choices(string.digits, k=6))

def gerar_senha(n: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))

def obter_link_acesso(ev_id: str) -> str:
    token = ev_id
    try:
        if "dados" in st.session_state and st.session_state.dados:
            dados = st.session_state.dados
            if ev_id in dados["eventos"]:
                token = dados["eventos"][ev_id].get("link_token", ev_id)
    except Exception:
        pass

    try:
        from streamlit.web.server.websocket_headers import _get_websocket_headers
        headers = _get_websocket_headers()
        if headers:
            host = headers.get("Host")
            if host and "localhost" not in host and "127.0.0.1" not in host:
                proto = headers.get("X-Forwarded-Proto", "https" if "streamlit.app" in host else "http")
                return f"{proto}://{host}/?ev={token}"
    except Exception:
        pass
    
    if os.name == 'nt':
        return f"http://localhost:8501/?ev={token}"
    return f"https://sistema-atcerimonial.streamlit.app/?ev={token}"

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
    val_str = str(valor) if pd.notna(valor) and valor is not None else ""
    conteudo = val_str.strip() if val_str.strip() else "<em style='opacity:0.45;'>Não informado</em>"
    st.markdown(
        f"<div class='bf-field'><div class='bf-label'>{label}</div>{conteudo}</div>",
        unsafe_allow_html=True,
    )

def get_evento_atual():
    if "dados" not in st.session_state or st.session_state.dados is None:
        st.session_state.dados = carregar_dados()
    if "evento_id" in st.session_state and st.session_state.evento_id:
        return get_ev(st.session_state.dados, st.session_state.evento_id)
    return None

def obter_nome_noivos_por_token(token: str) -> str:
    # 1. Tenta carregar do Supabase sem chamar st.error
    if supabase_client:
        try:
            response = supabase_client.table("at_cerimonial").select("data").eq("id", "dados_sistema").execute()
            if response.data:
                dados = response.data[0]["data"]
                for ev in dados.get("eventos", {}).values():
                    if ev.get("link_token") == token or ev.get("ev_id") == token:
                        return ev.get("noivos", "")
        except Exception:
            pass
    # 2. Tenta carregar do arquivo local
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                dados = json.load(f)
                for ev in dados.get("eventos", {}).values():
                    if ev.get("link_token") == token or ev.get("ev_id") == token:
                        return ev.get("noivos", "")
    except Exception:
        pass
    return ""

def limpar_nome_slug(nome: str) -> str:
    import re
    import unicodedata
    nome = nome.lower().replace("casamento", "")
    nome = "".join(c for c in unicodedata.normalize('NFD', nome) if unicodedata.category(c) != 'Mn')
    nome = nome.replace("&", "-")
    nome = re.sub(r'\b(e)\b', '-', nome)
    slug = re.sub(r'[^a-z0-9]+', '-', nome).strip('-')
    slug = re.sub(r'-+', '-', slug)
    return slug

def gerar_slug_token(noivos: str, eventos: dict) -> str:
    base_slug = limpar_nome_slug(noivos)
    if not base_slug:
        base_slug = "evento"
    
    slug = base_slug
    tokens_existentes = {ev.get("link_token") for ev in eventos.values() if ev.get("link_token")}
    while slug in tokens_existentes:
        suffix = "".join(random.choices(string.digits, k=3))
        slug = f"{base_slug}-{suffix}"
    return slug
