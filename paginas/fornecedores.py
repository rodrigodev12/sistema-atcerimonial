import unicodedata
import streamlit as st
import pandas as pd
import shared

def _sort_key(s: str) -> str:
    s_clean = unicodedata.normalize('NFKD', str(s or ""))
    return "".join(c for c in s_clean if not unicodedata.combining(c)).lower().strip()

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

evento_atual = shared.get_evento_atual()
if not evento_atual:
    st.info("Por favor, selecione ou acesse um evento válido.")
    st.stop()

is_admin = st.session_state.tipo_usuario == "admin"

dias_restantes = shared.calcular_dias_restantes_evento(evento_atual)
dias_txt = shared.formatar_texto_dias_restantes(dias_restantes)
data_evento_str = evento_atual.get("data", "")

st.markdown(
    f"### Alinhamento com Fornecedores — {evento_atual['noivos']} &nbsp;"
    f"<span style='font-size:0.84rem; font-weight:500; color:#166534; background:#DCFCE7; border:1px solid #86EFAC; border-radius:14px; padding:3px 12px; vertical-align: middle; display: inline-block;'>"
    f"⏳ {dias_txt.capitalize()}{f' ({data_evento_str})' if data_evento_str else ''}</span>",
    unsafe_allow_html=True
)

# ── Central de Avisos WhatsApp ──────────────────────────────────────────────
with st.expander(f"📲 Central de Avisos WhatsApp — Contagem Regressiva ({dias_txt})", expanded=False):
    st.markdown(f"""
    <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 12px 16px; margin-bottom: 14px;">
        <div style="font-weight: 700; color: #166534; font-size: 0.98rem; margin-bottom: 3px;">
            📲 Automação de Mensagens para Fornecedores via WhatsApp
        </div>
        <div style="font-size: 0.85rem; color: #15803D;">
            Dispare lembretes com 1 clique para os fornecedores cadastrados informando que <strong>{dias_txt}</strong> para o grande dia{f' (<strong>{data_evento_str}</strong>)' if data_evento_str else ''}.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_m1, c_m2 = st.columns([1.5, 2.5])
    with c_m1:
        modelo_central = st.selectbox(
            "Modelo da Mensagem",
            [
                "📅 Contagem Regressiva & Alinhamento (Padrão)",
                "⏰ Confirmação de Horários & Chegada",
                "📝 Pendências Contratuais & Documentos"
            ],
            key="central_mod_wa"
        )
        tipo_central = "padrao"
        if "Horários" in modelo_central:
            tipo_central = "horarios"
        elif "Pendências" in modelo_central:
            tipo_central = "pendencias"

        apenas_contratados = st.checkbox(
            "Filtrar apenas fornecedores com status 'CONTRATADO'",
            value=False,
            key="chk_apenas_contratados"
        )

    with c_m2:
        exemplo_forn = {"SETOR": "Exemplo (Fotografia)", "EMPRESA": "Estúdio Parceiro", "RESPONSÁVEL": "Nome do Fornecedor"}
        msg_preview_central = shared.gerar_mensagem_whatsapp_fornecedor(exemplo_forn, evento_atual, modelo=tipo_central)
        st.caption("👀 **Prévia do modelo selecionado (variáveis são preenchidas automaticamente para cada fornecedor):**")
        st.text_area("Prévia", value=msg_preview_central, height=120, disabled=True, label_visibility="collapsed")

    # Lista de fornecedores com telefone cadastrado
    todos_forns = evento_atual.get("fornecedores", [])
    forns_com_tel = [
        f for f in todos_forns
        if shared.limpar_telefone_whatsapp(f.get("CEL/TEL", ""))
    ]
    if apenas_contratados:
        forns_com_tel = [f for f in forns_com_tel if f.get("STATUS") == "CONTRATADO"]

    st.markdown(f"**Fornecedores prontos para envio ({len(forns_com_tel)} encontrados):**")
    if not forns_com_tel:
        st.info("Nenhum fornecedor com telefone válido encontrado. Preencha o campo Cel/Tel nos cards abaixo.")
    else:
        for item_f in forns_com_tel:
            s_nome = item_f.get("SETOR", "")
            s_emp = item_f.get("EMPRESA", "")
            s_resp = item_f.get("RESPONSÁVEL", "")
            s_tel = item_f.get("CEL/TEL", "")
            s_st = item_f.get("STATUS", "Orçando")
            s_cor = STATUS_CORES.get(s_st, {"bg": "#F8FAFC", "text": "#334155", "border": "#CBD5E1", "emoji": "❔"}) if 'STATUS_CORES' in locals() else {"bg": "#F8FAFC", "text": "#334155", "border": "#CBD5E1", "emoji": "⚪"}

            c_f_info, c_f_st, c_f_act = st.columns([3.2, 1.3, 1.5])
            with c_f_info:
                st.markdown(f"**{s_nome}** — {s_emp or s_resp or 'Sem nome'}")
                st.caption(f"📞 WhatsApp: `{s_tel}` {f'• Resp: {s_resp}' if s_resp else ''}")
            with c_f_st:
                st.markdown(
                    f'<span style="background:{s_cor["bg"]};color:{s_cor["text"]};border:1px solid {s_cor["border"]};'
                    f'border-radius:6px;padding:2px 8px;font-size:11px;font-weight:600;">{s_cor["emoji"]} {s_st}</span>',
                    unsafe_allow_html=True
                )
            with c_f_act:
                msg_indiv = shared.gerar_mensagem_whatsapp_fornecedor(item_f, evento_atual, modelo=tipo_central)
                link_wa_indiv = shared.gerar_link_whatsapp(s_tel, msg_indiv)
                st.link_button("📲 Enviar WhatsApp", url=link_wa_indiv, use_container_width=True)
            st.markdown("<hr style='margin: 4px 0 8px 0; border: none; border-top: 1px solid #F1F5F9;'>", unsafe_allow_html=True)


# Dialog para visualização ampliada de fotos e documentos
if hasattr(st, "dialog"):
    @st.dialog("Visualizar Arquivo", width="large")
    def modal_visualizar_arquivo(item_obj):
        if "data_url" in item_obj and str(item_obj.get("data_url", "")).startswith("data:image"):
            st.image(item_obj["data_url"], use_container_width=True)
        st.markdown(f"**Arquivo:** `{item_obj.get('nome', '')}`")
        if item_obj.get("tamanho"):
            st.caption(f"Tamanho: {item_obj['tamanho'] // 1024} KB")
        doc_bytes = shared.obter_bytes_documento(item_obj)
        if doc_bytes:
            st.download_button(
                "⬇️ Baixar Arquivo",
                data=doc_bytes,
                file_name=item_obj.get("nome", "arquivo"),
                mime=item_obj.get("mime", "application/octet-stream"),
                key=f"modal_dl_{item_obj.get('id', 'temp')}"
            )
else:
    def modal_visualizar_arquivo(item_obj):
        if "data_url" in item_obj and str(item_obj.get("data_url", "")).startswith("data:image"):
            st.image(item_obj["data_url"], use_container_width=True)

st.markdown("""
<style>
.forn-card-foto {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 6px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    margin-bottom: 8px;
    text-align: center;
}
.forn-card-foto img {
    border-radius: 6px;
    height: 140px;
    width: 100%;
    object-fit: cover;
}
</style>
""", unsafe_allow_html=True)

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

# Ordena os fornecedores em ordem alfabética de A a Z pelo nome do Setor
if not df_view.empty and "SETOR" in df_view.columns:
    df_view = df_view.sort_values(by="SETOR", key=lambda col: col.map(_sort_key))

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

    item_ref = fornecedores_dict.get(setor, forn)
    fotos = item_ref.get("fotos", [])
    documentos = item_ref.get("documentos", [])

    qtd_fotos = len(fotos)
    qtd_docs = len(documentos)
    badges_extras = []
    if qtd_fotos > 0:
        badges_extras.append(f"📸 {qtd_fotos}")
    if qtd_docs > 0:
        badges_extras.append(f"📁 {qtd_docs}")
    extra_str = f"  [{' · '.join(badges_extras)}]" if badges_extras else ""

    # Expandable header label
    label = f"{cor['emoji']} {setor}" + (f" — {empresa}" if empresa else " — (Pendente)") + extra_str
    with st.expander(label, expanded=False):
        # Badge status display
        st.markdown(
            f'<div style="background:{cor["bg"]};border:1px solid {cor["border"]};'
            f'border-radius:8px;padding:6px 12px;margin-bottom:12px;display:inline-block;">'
            f'<span style="color:{cor["text"]};font-size:12px;font-weight:600;">'
            f'{cor["emoji"]} {status}</span></div>',
            unsafe_allow_html=True,
        )

        tab_dados, tab_fotos, tab_docs = st.tabs([
            "📝 Dados & Contrato",
            f"📸 Fotos do Trabalho ({qtd_fotos})",
            f"📁 Pasta de Contrato & Recibos ({qtd_docs})"
        ])

        with tab_dados:
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
                    if st.form_submit_button("💾 Salvar Dados", type="primary", use_container_width=True):
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

            # ── Seção Automação WhatsApp (Aviso de Contagem Regressiva) ───
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            tel_limpo = shared.limpar_telefone_whatsapp(tel)

            if tel_limpo:
                st.markdown(f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #22C55E; border-radius: 8px; padding: 12px 14px; margin-top: 10px; margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
                        <div>
                            <div style="font-weight: 700; color: #0F172A; font-size: 0.90rem;">
                                📲 Automação WhatsApp — Aviso de Contagem Regressiva
                            </div>
                            <div style="font-size: 0.80rem; color: #475569; margin-top: 3px;">
                                ⏳ <strong>{dias_txt}</strong> para o evento ({data_evento_str or 'Data a definir'}) &nbsp;•&nbsp; 
                                📞 WhatsApp: <strong style="color: #166534;">{tel}</strong>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.popover(f"📲 Preparar e Enviar Aviso via WhatsApp ({tel})", use_container_width=True):
                    st.markdown(f"**Disparo de Mensagem — {setor}**")
                    st.caption(f"Destinatário: **{resp or empresa or setor}** &nbsp;•&nbsp; WhatsApp: **{tel}**")

                    mod_opcoes = [
                        "📅 Contagem Regressiva & Alinhamento (Padrão)",
                        "⏰ Confirmação de Horários & Chegada",
                        "📝 Pendências Contratuais & Documentos"
                    ]
                    mod_escolhido = st.selectbox(
                        "Modelo da Mensagem:",
                        mod_opcoes,
                        key=f"mod_forn_{setor}_{st.session_state.evento_id}"
                    )

                    chave_mod = "padrao"
                    if "Horários" in mod_escolhido:
                        chave_mod = "horarios"
                    elif "Pendências" in mod_escolhido:
                        chave_mod = "pendencias"

                    msg_gerada = shared.gerar_mensagem_whatsapp_fornecedor(forn, evento_atual, modelo=chave_mod)

                    msg_final = st.text_area(
                        "Mensagem pronta (você pode personalizar livremente antes de enviar):",
                        value=msg_gerada,
                        height=160,
                        key=f"txt_msg_forn_{setor}_{st.session_state.evento_id}"
                    )

                    link_wa_btn = shared.gerar_link_whatsapp(tel, msg_final)

                    st.link_button(
                        "🚀 Abrir no WhatsApp e Enviar Mensagem",
                        url=link_wa_btn,
                        type="primary",
                        use_container_width=True
                    )
            else:
                st.markdown(f"""
                <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-left: 4px solid #F59E0B; border-radius: 8px; padding: 10px 14px; margin-top: 10px; margin-bottom: 8px;">
                    <div style="font-weight: 600; color: #92400E; font-size: 0.86rem;">📲 Automação WhatsApp — Aviso de Contagem Regressiva</div>
                    <div style="font-size: 0.80rem; color: #B45309; margin-top: 2px;">
                        ⚠️ Para enviar o aviso automático com a contagem de dias restantes via WhatsApp, cadastre o número no campo <strong>'Cel/Tel'</strong> (com DDD) e salve os dados do fornecedor.
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with tab_fotos:
            st.markdown(f"""
            <div style="margin-bottom: 8px;">
                <span style="font-weight: 600; font-size: 0.92rem; color: #0F172A;">Galeria de Trabalhos & Portfólio — {setor}</span>
                <p style="font-size: 0.82rem; color: #64748B; margin: 2px 0 10px 0;">
                    Adicione fotos do trabalho deste fornecedor para exposição e acompanhamento do estilo e qualidade.
                </p>
            </div>
            """, unsafe_allow_html=True)

            if can_edit:
                novas_fotos = st.file_uploader(
                    f"📸 Adicionar fotos ({setor})",
                    type=["jpg", "jpeg", "png", "webp"],
                    accept_multiple_files=True,
                    key=f"up_fotos_{setor}_{st.session_state.evento_id}",
                    help="Arraste ou selecione imagens dos trabalhos realizados."
                )
                if novas_fotos:
                    item = fornecedores_dict.get(setor, {})
                    if "fotos" not in item or not isinstance(item["fotos"], list):
                        item["fotos"] = []
                    hashes_existentes = {f.get("hash") for f in item["fotos"] if f.get("hash")}
                    adicionadas = 0
                    for f_arq in novas_fotos:
                        ref = shared.processar_imagem_referencia(f_arq)
                        if ref["hash"] not in hashes_existentes:
                            item["fotos"].append(ref)
                            hashes_existentes.add(ref["hash"])
                            adicionadas += 1
                    if adicionadas > 0:
                        shared.salvar_dados(st.session_state.dados)
                        st.toast(f"✅ {adicionadas} foto(s) adicionada(s) ao portfólio!", icon="📸")
                        st.rerun()

            if fotos:
                cols_grid = st.columns(3)
                for idx_f, f_item in enumerate(fotos):
                    with cols_grid[idx_f % 3]:
                        st.markdown(f"""
                        <div class="forn-card-foto">
                            <img src="{f_item['data_url']}" alt="{f_item.get('nome', 'Foto')}">
                            <div style="font-size: 0.76rem; font-weight: 600; color: #1E293B; margin-top: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{f_item.get('nome', '')}">
                                {f_item.get('nome', 'Foto')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        cf_b1, cf_b2 = st.columns([1.2, 1])
                        with cf_b1:
                            if st.button("🔍 Ampliar", key=f"btn_zoom_{setor}_{f_item['id']}", use_container_width=True):
                                modal_visualizar_arquivo(f_item)
                        with cf_b2:
                            if can_edit:
                                if st.button("🗑️ Excluir", key=f"btn_del_foto_{setor}_{f_item['id']}", use_container_width=True):
                                    item = fornecedores_dict.get(setor, {})
                                    item["fotos"] = [f for f in item.get("fotos", []) if f.get("id") != f_item["id"]]
                                    shared.salvar_dados(st.session_state.dados)
                                    st.toast("Foto removida!", icon="🗑️")
                                    st.rerun()
            else:
                st.info("📷 Nenhuma foto do trabalho cadastrada ainda. Adicione fotos acima para expor o trabalho deste fornecedor.")

        with tab_docs:
            st.markdown(f"""
            <div style="margin-bottom: 8px;">
                <span style="font-weight: 600; font-size: 0.92rem; color: #0F172A;">📁 Pasta de Contrato & Recibos — {setor}</span>
                <p style="font-size: 0.82rem; color: #64748B; margin: 2px 0 10px 0;">
                    Armazene com segurança o contrato de prestação de serviços, recibos de pagamento, notas fiscais e comprovantes.
                </p>
            </div>
            """, unsafe_allow_html=True)

            if can_edit:
                c_up_d1, c_up_d2 = st.columns([2.2, 1.2])
                with c_up_d1:
                    novos_docs = st.file_uploader(
                        f"📁 Adicionar documento ({setor})",
                        type=["pdf", "png", "jpg", "jpeg", "docx", "xlsx", "txt"],
                        accept_multiple_files=True,
                        key=f"up_docs_{setor}_{st.session_state.evento_id}",
                        help="Envie contrato assinado, recibos ou notas fiscais."
                    )
                with c_up_d2:
                    tipo_doc_sel = st.selectbox(
                        "Tipo do documento",
                        ["Contrato", "Recibo de Pagamento", "Comprovante / NF", "Proposta / Orçamento", "Outro Documento"],
                        key=f"tipo_doc_sel_{setor}_{st.session_state.evento_id}"
                    )
                
                if novos_docs:
                    item = fornecedores_dict.get(setor, {})
                    if "documentos" not in item or not isinstance(item["documentos"], list):
                        item["documentos"] = []
                    hashes_existentes = {d.get("hash") for d in item["documentos"] if d.get("hash")}
                    adicionados_docs = 0
                    for d_arq in novos_docs:
                        doc_obj = shared.processar_documento_fornecedor(d_arq, tipo=tipo_doc_sel)
                        if doc_obj["hash"] not in hashes_existentes:
                            item["documentos"].append(doc_obj)
                            hashes_existentes.add(doc_obj["hash"])
                            adicionados_docs += 1
                    if adicionados_docs > 0:
                        shared.salvar_dados(st.session_state.dados)
                        st.toast(f"✅ {adicionados_docs} documento(s) arquivado(s) na pasta de {setor}!", icon="📁")
                        st.rerun()

            if documentos:
                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                for idx_d, doc_item in enumerate(documentos):
                    d_nome = doc_item.get("nome", "Documento")
                    d_tipo = doc_item.get("tipo", "Documento")
                    d_tam = doc_item.get("tamanho", 0) // 1024
                    d_data = doc_item.get("enviado_em", "")

                    ext = d_nome.split(".")[-1].lower() if "." in d_nome else ""
                    if ext == "pdf":
                        icon_ext = "📕"
                    elif ext in ("jpg", "jpeg", "png", "webp"):
                        icon_ext = "🖼️"
                    elif ext in ("doc", "docx"):
                        icon_ext = "📘"
                    elif ext in ("xls", "xlsx", "csv"):
                        icon_ext = "📗"
                    else:
                        icon_ext = "📄"

                    if "contrato" in d_tipo.lower():
                        badge_style = "background:#DBEAFE; color:#1E40AF; border:1px solid #BFDBFE;"
                    elif "recibo" in d_tipo.lower():
                        badge_style = "background:#D1FAE5; color:#065F46; border:1px solid #6EE7B7;"
                    elif "comprovante" in d_tipo.lower() or "nf" in d_tipo.lower():
                        badge_style = "background:#F3E8FF; color:#6B21A8; border:1px solid #E9D5FF;"
                    else:
                        badge_style = "background:#F1F5F9; color:#475569; border:1px solid #CBD5E1;"

                    col_card, col_acoes = st.columns([3, 1.4])
                    with col_card:
                        st.markdown(f"""
                        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px;">
                            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 6px;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="font-size: 1.25rem;">{icon_ext}</span>
                                    <div>
                                        <div style="font-size: 0.88rem; font-weight: 600; color: #1E293B;">{d_nome}</div>
                                        <div style="font-size: 0.74rem; color: #64748B;">{d_tam} KB {f'• Enviado em {d_data}' if d_data else ''}</div>
                                    </div>
                                </div>
                                <span style="font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 10px; {badge_style}">
                                    {d_tipo}
                                </span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_acoes:
                        doc_bytes = shared.obter_bytes_documento(doc_item)
                        cd_b1, cd_b2 = st.columns([1, 1])
                        with cd_b1:
                            if doc_bytes:
                                st.download_button(
                                    "⬇️ Baixar",
                                    data=doc_bytes,
                                    file_name=d_nome,
                                    mime=doc_item.get("mime", "application/octet-stream"),
                                    key=f"dl_btn_{setor}_{doc_item['id']}",
                                    use_container_width=True
                                )
                        with cd_b2:
                            if can_edit:
                                if st.button("🗑️", key=f"del_doc_btn_{setor}_{doc_item['id']}", help="Excluir documento", use_container_width=True):
                                    item = fornecedores_dict.get(setor, {})
                                    item["documentos"] = [d for d in item.get("documentos", []) if d.get("id") != doc_item["id"]]
                                    shared.salvar_dados(st.session_state.dados)
                                    st.toast(f"Documento '{d_nome}' excluído da pasta!", icon="🗑️")
                                    st.rerun()
            else:
                st.info("📁 Pasta de documentos vazia. Faça upload do contrato do prestador e de recibos de pagamento para arquivamento.")

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
            setores_lista = sorted([f["SETOR"] for f in evento_atual["fornecedores"]], key=_sort_key)
            setor_para_excluir = st.selectbox("Selecione o Setor para Excluir", setores_lista, key="del_setor_name")
            if st.button("🗑️ Excluir Setor Selecionado", key="btn_del_setor"):
                evento_atual["fornecedores"] = [f for f in evento_atual["fornecedores"] if f["SETOR"] != setor_para_excluir]
                shared.salvar_dados(st.session_state.dados)
                st.toast(f"Setor '{setor_para_excluir}' excluído!", icon="🗑️")
                st.rerun()
