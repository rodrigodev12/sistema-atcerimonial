import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import shared
import streamlit_antd_components as sac

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
    window.parent.addEventListener('DOMContentLoaded', desativarTraducao);
    setTimeout(desativarTraducao, 500);
    setTimeout(desativarTraducao, 1500);

    // MÁSCARA DE DATA AUTOMÁTICA
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
                            
                            if (e.target.value === formatted) {
                                return;
                            }
                            
                            nativeInputValueSetter.call(e.target, formatted);
                            e.target.dispatchEvent(new Event('input', { bubbles: true }));
                        });
                    }
                }
            }
        }
    };

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

section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stMarkdown > div,
section[data-testid="stSidebar"] .element-container,
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div,
section[data-testid="stSidebar"] .stCheckbox {
    background-color: transparent !important;
    background:       transparent !important;
}

section[data-testid="stSidebar"] [data-testid="stExpander"],
section[data-testid="stSidebar"] details summary {
    background-color: rgba(255,255,255,0.08) !important;
    border-color: rgba(255,255,255,0.15) !important;
}

section[data-testid="stSidebar"] input {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="select-control"],
section[data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="select-control"] * {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
}/* 1. Alvo exato: O texto do primeiro elemento de cabeçalho do menu */
[data-testid="stSidebarNav"] > ul > li:first-child div[data-anchored="true"],
[data-testid="stSidebarNav"] div:first-child[data-anchored="true"] {
    font-size: 22px !important;       /* Aumenta exclusivamente o título principal */
    font-weight: bold !important;     /* Deixa em negrito */
    color: #ffffff !important;        /* Cor branca */
    padding-bottom: 15px !important;  /* Dá um pequeno espaço interno */
}

/* 2. Cria o espaçamento elegante separando o título das abas */
[data-testid="stSidebarNavItems"] {
    margin-top: 30px !important;      /* Afasta a lista de abas para baixo */
}

/* 3. Garante que os nomes das abas voltem e fiquem no tamanho padrão */
[data-testid="stSidebarNavItems"] span {
    font-size: 14px !important;       /* Protege o tamanho das abas */
    font-weight: normal !important;   /* Tira o negrito delas */
}
/* Força o botão do menu lateral no celular a ficar destacado e visível */
button[data-testid="stSidebarCollapseButton"] {
    background-color: #3b82f6 !important; /* Deixa o botão azul */
    color: white !important;               /* Deixa a seta branca */
    border-radius: 50% !important;         /* Transforma em um círculo */
    width: 45px !important;
    height: 45px !important;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3) !important; /* Dá relevo */
    position: fixed !important;
    top: 15px !important;
    left: 15px !important;
    z-index: 999999 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

button[data-testid="stSidebarCollapseButton"] svg {
    color: white !important;
    fill: white !important;
    width: 22px !important;
    height: 22px !important;
    transform: scale(1.3) !important;
}


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

.alert-row {
    background: #FFF7ED;
    border-left: 4px solid #F97316;
    border-radius: 4px;
    padding: 8px 14px;
    margin-bottom: 6px;
    font-size: 14px;
    color: #0F172A;
}

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

[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 12px 16px;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DADOS & SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
if "dados" not in st.session_state:
    st.session_state.dados = shared.carregar_dados()

_ss_defaults = {
    "logado": False, "usuario": None, "tipo_usuario": None, "evento_id": None,
    "edit_forn_ver": 0, "edit_rot_ver": 0, "novo_ev_cred": None, "sel_ev": None,
    "perfil": None,
}
for k, v in _ss_defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Recupera sessão por link direto do evento ou parâmetro de sessão
if not st.session_state.logado:
    ev_id_url = st.query_params.get("evento") or st.query_params.get("ev")
    if ev_id_url:
        evento_encontrado_id = None
        for ev_id, ev in st.session_state.dados.get("eventos", {}).items():
            if ev.get("link_token") == ev_id_url or ev_id == ev_id_url:
                evento_encontrado_id = ev_id
                break
        
        if evento_encontrado_id:
            st.session_state.update(
                logado=True,
                usuario=f"noivos_{evento_encontrado_id}",
                tipo_usuario="cliente",
                perfil="CLIENTE",
                evento_id=evento_encontrado_id,
            )
            st.rerun()
else:
    if "session" in st.query_params:
        del st.query_params["session"]

# ═══════════════════════════════════════════════════════════════════════════════
# TELA DE LOGIN
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logado:
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] { display: none !important; }
    header[data-testid="stHeader"]   { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.write("")
        st.markdown(
            "<h1 class='notranslate' style='text-align:center;font-size:28px;margin-bottom:2px;'>💍 AT Cerimonial</h1>"
            "<p style='text-align:center;opacity:0.65;margin-bottom:12px;font-size:13px;'>Gestão Integrada de Eventos</p>",
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            st.subheader("Acesso Restrito", divider=False)
            with st.form("form_login"):
                u = st.text_input("Usuário", key="li_user")
                s = st.text_input("Senha", type="password", key="li_pass")
                _, cb, _ = st.columns([1, 2, 1])
                with cb:
                    submitted = st.form_submit_button("Entrar no Painel")

            if submitted:
                usr = st.session_state.dados["usuarios"].get(u)
                if usr and usr["senha"] == s:
                    st.query_params.clear()
                    st.session_state.update(
                        logado=True, usuario=u,
                        tipo_usuario=usr["tipo"],
                        perfil=usr["tipo"].upper(),
                        evento_id=usr.get("evento_id"),
                    )
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")

            # Modo de depuração para verificar conexão e dados
            if st.query_params.get("debug") == "1":
                st.markdown("<hr style='opacity:.15; margin:10px 0;'>", unsafe_allow_html=True)
                st.caption("🔍 **Diagnóstico do Sistema**")
                st.write("• **Supabase conectado:**", shared.supabase_client is not None)
                st.write("• **Eventos carregados:**")
                eventos_dict = st.session_state.dados.get("eventos", {})
                if eventos_dict:
                    for ev_id, ev in eventos_dict.items():
                        st.write(f"- ID: `{ev_id}` | Noivos: **{ev.get('noivos')}** | Token: `{ev.get('link_token')}`")
                else:
                    st.write("Nenhum evento cadastrado no banco de dados.")

        st.markdown(
            "<p style='text-align:center;font-size:11px;opacity:0.4;margin-top:14px;'>AT Cerimonial © 2026</p>",
            unsafe_allow_html=True,
        )
    st.stop()

is_admin = st.session_state.tipo_usuario == "admin"
evento_atual = shared.get_evento_atual()

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # --- Rodapé (Mostrado nativamente abaixo do st.navigation) ---
    if is_admin:
        lista_ev = list(st.session_state.dados["eventos"].keys())
        if st.session_state.sel_ev not in lista_ev:
            st.session_state.sel_ev = lista_ev[0]

        st.session_state.evento_id = st.selectbox(
            "Evento Ativo",
            lista_ev,
            index=lista_ev.index(st.session_state.sel_ev),
            format_func=lambda x: st.session_state.dados["eventos"][x]["noivos"],
            key="sb_ev",
        )
        st.session_state.sel_ev = st.session_state.evento_id

        full_link = shared.obter_link_acesso(st.session_state.evento_id)

        st.markdown("**🔗 Link de Acesso do Casal:**")
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

        with st.expander("➕ Criar Novo Evento"):
            with st.form("form_criar_ev", clear_on_submit=True):
                ne_noivos = st.text_input("Noivos", placeholder="Ex: Carla & Lucas")
                ne_data   = st.text_input("Data", placeholder="DD/MM/AAAA")
                criar_ok  = st.form_submit_button("✅ Criar Evento")

            if criar_ok:
                if not (ne_noivos and ne_data):
                    st.warning("Preencha todos os campos.")
                else:
                    data_limpa = "".join(filter(str.isdigit, ne_data))
                    if len(data_limpa) == 8:
                        ne_data = f"{data_limpa[:2]}/{data_limpa[2:4]}/{data_limpa[4:]}"
                    elif len(data_limpa) == 6:
                        ne_data = f"{data_limpa[:2]}/{data_limpa[2:4]}/20{data_limpa[4:]}"

                    ev_id = shared.gerar_ev_id()
                    st.session_state.dados["eventos"][ev_id] = shared._novo_evento(ne_noivos, ne_data)
                    shared.salvar_dados(st.session_state.dados)
                    st.session_state.sel_ev = ev_id
                    st.session_state.novo_ev_cred = {
                        "noivos": ne_noivos, "ev_id": ev_id
                    }
                    st.rerun()

        if st.session_state.novo_ev_cred:
            c = st.session_state.novo_ev_cred
            link_acesso = shared.obter_link_acesso(c['ev_id'])
            st.success(
                f"🎉 Evento de **{c['noivos']}** criado com sucesso!\n\n"
                f"Envie o seguinte link de acesso aos noivos:\n"
                f"[Clique aqui para abrir]({link_acesso})\n\n"
                f"URL de acesso: `{link_acesso}`"
            )
            if st.button("✖ Fechar", key="btn_close_cred"):
                st.session_state.novo_ev_cred = None
                st.rerun()

        if len(st.session_state.dados["eventos"]) > 1:
            with st.expander("🗑️ Excluir Evento"):
                ev_del = st.selectbox(
                    "Evento para excluir",
                    lista_ev,
                    format_func=lambda x: st.session_state.dados["eventos"][x]["noivos"],
                    key="sb_del",
                )
                confirm_del = st.checkbox("Confirmo a exclusão permanente", key="ck_del")
                if st.button("Excluir", key="btn_del"):
                    if confirm_del:
                        st.session_state.dados["usuarios"] = {
                            u: v for u, v in st.session_state.dados["usuarios"].items()
                            if not (v.get("tipo") == "cliente" and v.get("evento_id") == ev_del)
                        }
                        del st.session_state.dados["eventos"][ev_del]
                        shared.salvar_dados(st.session_state.dados)
                        novo_sel = list(st.session_state.dados["eventos"].keys())[0]
                        st.session_state.sel_ev = novo_sel
                        st.session_state.evento_id = novo_sel
                        st.rerun()
                    else:
                        st.warning("Marque a confirmação.")

    else:
        ev_cli = shared.get_ev(st.session_state.dados, st.session_state.evento_id)
        st.markdown(f"**{ev_cli['noivos']}**")
        st.markdown(f"📅 {ev_cli['data']}")

    st.markdown("<hr style='opacity:.15; margin:14px 0;'>", unsafe_allow_html=True)
    if st.button("🚪 Sair do Sistema", key="btn_logout"):
        st.query_params.clear()
        for k in ["logado", "usuario", "tipo_usuario", "evento_id", "sel_ev", "novo_ev_cred"]:
            st.session_state[k] = False if k == "logado" else None
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# NAVEGAÇÃO MULTIPÁGINAS NATIVA COM DICIONÁRIO DE SEÇÃO
# ═══════════════════════════════════════════════════════════════════════════════
pag_dashboard = st.Page("paginas/dashboard.py", title="Dashboard", icon=":material/bar_chart:")
pag_briefing = st.Page("paginas/briefing.py", title="Briefing", icon=":material/description:")
pag_cerimonial = st.Page("paginas/checklist_cerimonial.py", title="Checklist Cerimonial", icon=":material/rule:")
pag_noivos = st.Page("paginas/checklist_noivos.py", title="Checklist Noivos", icon=":material/favorite:")
pag_fornecedores = st.Page("paginas/fornecedores.py", title="Fornecedores", icon=":material/store:")
pag_roteiro = st.Page("paginas/roteiro.py", title="Roteiro", icon=":material/schedule:")

lista_paginas = [pag_dashboard, pag_briefing]

if is_admin:
    lista_paginas.append(pag_cerimonial)

lista_paginas.extend([pag_noivos, pag_fornecedores, pag_roteiro])

# O título da chave vira o cabeçalho fixo no topo absoluto do menu lateral!
secao_titulo = f"AT Cerimonial ({st.session_state.tipo_usuario.upper()})"
menu_com_secao = {
    secao_titulo: lista_paginas
}

pg = st.navigation(menu_com_secao)

pg.run()