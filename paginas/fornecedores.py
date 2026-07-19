import streamlit as st
import pandas as pd
import shared

evento_atual = shared.get_evento_atual()
if not evento_atual:
    st.info("Por favor, selecione ou acesse um evento válido.")
    st.stop()

is_admin = st.session_state.tipo_usuario == "admin"

st.markdown(f"### Alinhamento com Fornecedores — {evento_atual['noivos']}")

# Filtros
cf1, cf2 = st.columns(2)
with cf1:
    filtro = st.selectbox(
        "Filtrar por status", ["Todos"] + shared.STATUS_OPCOES, key="filt_status"
    )
with cf2:
    busca = st.text_input("Buscar setor / empresa", placeholder="Digite…", key="busca_forn")

# Monta DataFrame completo
df_full = pd.DataFrame(evento_atual["fornecedores"])
df_view = df_full.copy()

if filtro != "Todos":
    df_view = df_view[df_view["STATUS"] == filtro]
if busca:
    df_view = df_view[
        df_view["SETOR"].str.contains(busca, case=False, na=False) |
        df_view["EMPRESA"].str.contains(busca, case=False, na=False)
    ]

# ── Mapeamento de cores por status ────────────────────────────────────────
STATUS_CORES = {
    "Orçando":                                     {"bg": "#FEE2E2", "text": "#991B1B", "border": "#FECACA",  "emoji": "🔴"},
    "Dados enviados":                               {"bg": "#DBEAFE", "text": "#1E40AF", "border": "#BFDBFE",  "emoji": "🔵"},
    "Contrato recebido":                            {"bg": "#FEF3C7", "text": "#92400E", "border": "#FDE68A",  "emoji": "🟡"},
    "Análise concluída / liberado para assinatura": {"bg": "#F3E8FF", "text": "#6B21A8", "border": "#E9D5FF",  "emoji": "🟣"},
    "Aguardando assinatura do CONTRATADO":          {"bg": "#ECFEFF", "text": "#155E75", "border": "#A5F3FC",  "emoji": "🩵"},
    "CONTRATADO":                                   {"bg": "#D1FAE5", "text": "#065F46", "border": "#6EE7B7",  "emoji": "🟢"},
    "Não haverá":                                   {"bg": "#F1F5F9", "text": "#475569", "border": "#CBD5E1",  "emoji": "⚪"},
}

# ── Legenda de cores ───────────────────────────────────────────────────────
badges_html = " ".join([
    f'<span style="background:{c["bg"]};color:{c["text"]};border:1px solid {c["border"]};'
    f'border-radius:6px;padding:2px 9px;font-size:11px;font-weight:500;white-space:nowrap;">'
    f'{c["emoji"]} {s}</span>'
    for s, c in STATUS_CORES.items()
])
st.markdown(
    f'<div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:14px;">'
    f'<span style="font-size:12px;font-weight:600;color:#64748B;margin-right:2px;">Legenda:</span>'
    f'{badges_html}</div>',
    unsafe_allow_html=True,
)

# ── Cards de fornecedores ──────────────────────────────────────────────────
can_edit = is_admin or st.session_state.tipo_usuario == "cliente"
fornecedores_dict = {f["SETOR"]: f for f in evento_atual["fornecedores"]}

for forn in df_view.to_dict("records"):
    setor   = forn["SETOR"]
    status  = forn.get("STATUS") or "Orçando"
    cor     = STATUS_CORES.get(status, {"bg": "#F8FAFC", "text": "#334155", "border": "#CBD5E1", "emoji": "❔"})
    empresa = forn.get("EMPRESA", "") or ""
    resp    = forn.get("RESPONSÁVEL", "") or ""
    tel     = forn.get("CEL/TEL", "") or ""
    insta   = forn.get("INSTAGRAM", "") or ""

    # Format values for display
    try:
        val_fmt = f"R$ {float(forn.get('VALOR CONTRATO', 0) or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        val_fmt = "R$ 0,00"
    try:
        he_fmt = f"R$ {float(forn.get('HORA EXTRA', 0) or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        he_fmt = "R$ 0,00"

    # Expandable header label
    label = f"{cor['emoji']} {setor}" + (f" — {empresa}" if empresa else " — (Pendente)")
    with st.expander(label, expanded=False):
        # Badge status display
        st.markdown(
            f'<div style="background:{cor["bg"]};border:1px solid {cor["border"]};'
            f'border-radius:8px;padding:6px 12px;margin-bottom:12px;display:inline-block;">'
            f'<span style="color:{cor["text"]};font-size:12px;font-weight:600;">'
            f'{cor["emoji"]} {status}</span></div>',
            unsafe_allow_html=True,
        )

        if can_edit:
            with st.form(key=f"form_forn_{setor}_{st.session_state.evento_id}"):
                c1, c2 = st.columns(2)
                with c1:
                    nova_empresa = st.text_input("🏢 Empresa",     value=empresa, key=f"emp_{setor}")
                    novo_resp    = st.text_input("👤 Responsável", value=resp,    key=f"resp_{setor}")
                    novo_tel     = st.text_input("📞 Cel/Tel",     value=tel,     key=f"tel_{setor}")
                    novo_insta   = st.text_input("📸 Instagram",   value=insta,   key=f"ig_{setor}")
                with c2:
                    novo_status = st.selectbox(
                        "📌 Status", shared.STATUS_OPCOES,
                        index=shared.STATUS_OPCOES.index(status) if status in shared.STATUS_OPCOES else 0,
                        key=f"st_{setor}"
                    )
                    try:
                        val_atual = float(forn.get("VALOR CONTRATO", 0) or 0)
                    except (ValueError, TypeError):
                        val_atual = 0.0
                    novo_val = st.number_input(
                        "💰 Valor Contrato (R$)", min_value=0.0, value=val_atual,
                        format="%.2f", step=100.0, key=f"val_{setor}"
                    )
                    try:
                        he_atual = float(forn.get("HORA EXTRA", 0) or 0)
                    except (ValueError, TypeError):
                        he_atual = 0.0
                    nova_he = st.number_input(
                        "⏱️ Hora Extra (R$)", min_value=0.0, value=he_atual,
                        format="%.2f", step=50.0, key=f"he_{setor}"
                    )
                    nova_obs = st.text_area(
                        "📝 Observação",
                        value=forn.get("OBSERVAÇÃO", "") or "",
                        height=80, key=f"obs_{setor}"
                    )
                if st.form_submit_button("💾 Salvar", type="primary", use_container_width=True):
                    item = fornecedores_dict.get(setor, {})
                    item["EMPRESA"]        = nova_empresa.strip()
                    item["RESPONSÁVEL"]    = novo_resp.strip()
                    item["CEL/TEL"]        = novo_tel.strip()
                    item["INSTAGRAM"]      = novo_insta.strip()
                    item["STATUS"]         = novo_status
                    item["VALOR CONTRATO"] = float(novo_val)
                    item["HORA EXTRA"]     = float(nova_he)
                    item["OBSERVAÇÃO"]     = nova_obs.strip()
                    shared.salvar_dados(st.session_state.dados)
                    st.toast(f"Fornecedor '{setor}' salvo!", icon="💾")
                    st.rerun()
        else:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**🏢 Empresa:** {empresa or '—'}")
                st.markdown(f"**👤 Responsável:** {resp or '—'}")
                st.markdown(f"**📞 Cel/Tel:** {tel or '—'}")
                st.markdown(f"**📸 Instagram:** {insta or '—'}")
            with c2:
                st.markdown(f"**💰 Valor Contrato:** {val_fmt}")
                st.markdown(f"**⏱️ Hora Extra:** {he_fmt}")
                obs = forn.get("OBSERVAÇÃO", "") or ""
                if obs:
                    st.markdown(f"**📝 Observação:** {obs}")

# Export button
st.write("")
cb1, _ = st.columns([2.5, 9.5])
with cb1:
    excel_bytes = shared.exportar_excel(evento_atual)
    st.download_button(
        "📥 Exportar Excel",
        data=excel_bytes,
        file_name=f"AT_{evento_atual['noivos'].replace(' ', '_').replace('&','e')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="dl_forn",
    )

if is_admin:
    # Add/Remove Sectors Expanders
    with st.expander("➕ / 🗑️ Adicionar ou Excluir Linhas (Setores)"):
        st.markdown("<small>Adicione novos setores ou exclua setores existentes da sua lista de fornecedores.</small>", unsafe_allow_html=True)
        
        c_add, c_del = st.columns(2)
        with c_add:
            st.markdown("**Adicionar Setor**")
            nome_novo_setor = st.text_input("Nome do Setor", placeholder="Ex: Banda Extra, Barman...", key="add_setor_name")
            if st.button("➕ Adicionar Setor", key="btn_add_setor"):
                if nome_novo_setor.strip():
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
                        shared.salvar_dados(st.session_state.dados)
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
                shared.salvar_dados(st.session_state.dados)
                st.toast(f"Setor '{setor_para_excluir}' excluído!", icon="🗑️")
                st.rerun()
