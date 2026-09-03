import streamlit as st
import shared

evento_atual = shared.get_evento_atual()
if not evento_atual:
    st.info("Por favor, selecione ou acesse um evento válido.")
    st.stop()

is_admin = st.session_state.tipo_usuario == "admin"
can_edit = is_admin or st.session_state.tipo_usuario == "cliente"

st.markdown(f"### Briefing Inicial — {evento_atual['noivos']}")
briefing = shared.get_briefing(evento_atual)

# Dialog para visualização de imagem em alta definição
if hasattr(st, "dialog"):
    @st.dialog("Visualização da Referência", width="large")
    def modal_visualizar_referencia(ref):
        st.image(ref["data_url"], use_container_width=True)
        col_m1, col_m2 = st.columns([3, 1])
        with col_m1:
            st.markdown(f"**Arquivo:** `{ref.get('nome', 'imagem.jpg')}`")
            if ref.get("legenda"):
                st.markdown(f"📌 **Nota:** {ref['legenda']}")
        with col_m2:
            st.caption(f"Dimensões: {ref.get('largura', '-')}x{ref.get('altura', '-')} px")
            st.caption(f"Tamanho: {ref.get('tamanho', 0)//1024} KB")
else:
    def modal_visualizar_referencia(ref):
        st.image(ref["data_url"], use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ESTILOS CSS EXCLUSIVOS DO BRIEFING VISUAL
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* Estilização da área de Drag and Drop */
[data-testid="stFileUploader"] {
    background-color: #FFFFFF !important;
    border: 2px dashed #94A3B8 !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    transition: all 0.25s ease-in-out;
}
[data-testid="stFileUploader"]:hover {
    border-color: #2563EB !important;
    background-color: #F8FAFC !important;
}

/* Card de Imagem da Galeria */
.ref-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    margin-bottom: 12px;
    transition: transform 0.2s, box-shadow 0.2s;
}
.ref-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
.ref-card-img {
    width: 100%;
    height: 170px;
    object-fit: cover;
    border-radius: 8px;
    display: block;
}
.ref-card-title {
    font-size: 0.8rem;
    font-weight: 600;
    color: #1E293B;
    margin-top: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.ref-card-meta {
    font-size: 0.72rem;
    color: #64748B;
}
</style>
""", unsafe_allow_html=True)

if can_edit:
    # ═══════════════════════════════════════════════════════════════════════════
    # 1. ESTILO DO EVENTO / REFERÊNCIAS VISUAIS (DRAG & DROP + PINTEREST)
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <div style="margin-top: 14px; margin-bottom: 6px;">
        <label style="font-size: 1.05rem; font-weight: 600; color: #0F172A; display: flex; align-items: center; gap: 8px;">
            <span>📸 Estilo do Evento & Referências Visuais</span>
            <span style="font-size: 0.75rem; font-weight: 600; background: #E0E7FF; color: #3730A3; padding: 2px 10px; border-radius: 12px;">Drag & Drop · Pinterest</span>
        </label>
        <p style="font-size: 0.86rem; color: #64748B; margin: 4px 0 10px 0;">
            Arraste e solte imagens de referências salvas do <strong>Pinterest</strong>, fotos de decoração, buquê, altar, vestidos ou paletas de cores.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Uploader com chave dinâmica para limpar após processamento
    counter_key = f"up_cnt_{st.session_state.evento_id}"
    if counter_key not in st.session_state:
        st.session_state[counter_key] = 0

    uploader_key = f"up_files_{st.session_state.evento_id}_{st.session_state[counter_key]}"
    arquivos_up = st.file_uploader(
        "Arraste e solte fotos de referências aqui",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        key=uploader_key,
        help="Formatos aceitos: PNG, JPG, JPEG, WEBP. É possível arrastar vários arquivos de uma vez.",
        label_visibility="collapsed"
    )

    if arquivos_up:
        with st.spinner("Processando e otimizando referências visuais..."):
            qtd_adicionadas = shared.adicionar_referencias_visuais(st.session_state.evento_id, arquivos_up)
            st.session_state[counter_key] += 1
            if qtd_adicionadas > 0:
                st.toast(f"✅ {qtd_adicionadas} referência(s) visual(is) adicionada(s)!", icon="📸")
            else:
                st.toast("ℹ️ As imagens enviadas já estavam cadastradas.", icon="ℹ️")
            st.rerun()

    # Galeria de referências visuais salvas
    referencias = briefing.get("referencias_visuais", [])
    if referencias:
        st.markdown(f"<div style='font-size: 0.88rem; font-weight: 600; color: #334155; margin: 12px 0 8px 0;'>🖼️ Inspirações Salvas ({len(referencias)} imagens)</div>", unsafe_allow_html=True)
        
        # Grid de 3 colunas
        cols = st.columns(3)
        for idx, ref in enumerate(referencias):
            col = cols[idx % 3]
            with col:
                st.markdown(f"""
                <div class="ref-card">
                    <img src="{ref['data_url']}" class="ref-card-img" alt="{ref.get('nome', 'Inspiração')}">
                    <div class="ref-card-title" title="{ref.get('nome', '')}">{ref.get('nome', 'Inspiração')}</div>
                    <div class="ref-card-meta">{ref.get('tamanho', 0)//1024} KB</div>
                </div>
                """, unsafe_allow_html=True)
                
                c_btn1, c_btn2 = st.columns([1, 1])
                with c_btn1:
                    if st.button("🔍 Ver", key=f"btn_ver_{ref['id']}", use_container_width=True):
                        modal_visualizar_referencia(ref)
                with c_btn2:
                    if st.button("🗑️", key=f"btn_del_{ref['id']}", help="Remover esta foto", use_container_width=True):
                        shared.remover_referencia_visual(st.session_state.evento_id, ref["id"])
                        st.toast("Referência removida!", icon="🗑️")
                        st.rerun()
    else:
        st.info("💡 Nenhuma foto de referência adicionada ainda. Arraste suas imagens favoritas acima!")

    # Integração adicional com Pinterest & Notas textuais
    with st.expander("📌 Link da pasta no Pinterest & Detalhes de Estilo (Opcional)", expanded=bool(briefing.get("pinterest_link") or briefing.get("estilo"))):
        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            st.text_input(
                "Link da pasta / moodboard no Pinterest",
                value=briefing.get("pinterest_link", ""),
                placeholder="Ex: https://br.pinterest.com/seuperfil/meu-casamento/",
                key=f"bf_pinterest_{st.session_state.evento_id}",
                on_change=shared.update_briefing_field,
                args=(st.session_state.evento_id, "pinterest_link", f"bf_pinterest_{st.session_state.evento_id}")
            )
        with col_p2:
            st.write("")
            st.write("")
            p_link = briefing.get("pinterest_link", "").strip()
            if p_link and p_link.startswith("http"):
                st.link_button("👉 Abrir Pinterest", url=p_link, use_container_width=True)
                
        st.text_area(
            "Anotações sobre o estilo / conceito visual",
            value=briefing.get("estilo", ""),
            placeholder="Ex: Rústico chic com elementos em madeira, luzinhas suspensas, toalhas em linho cru...",
            height=80,
            key=f"bf_estilo_{st.session_state.evento_id}",
            on_change=shared.update_briefing_field,
            args=(st.session_state.evento_id, "estilo", f"bf_estilo_{st.session_state.evento_id}")
        )

    st.markdown("<hr style='margin: 18px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # DEMAIS CAMPOS DO BRIEFING
    # ═══════════════════════════════════════════════════════════════════════════
    try:
        convidados_val = int(briefing.get("convidados") or 0)
        if convidados_val < 0:
            convidados_val = 0
    except (ValueError, TypeError):
        convidados_val = 0

    st.number_input(
        "Número estimado de convidados",
        min_value=0,
        max_value=10000,
        value=convidados_val,
        step=1,
        key=f"bf_convidados_{st.session_state.evento_id}",
        help="Use os botões + e - ou digite o número previsto de convidados.",
        on_change=shared.update_briefing_field,
        args=(st.session_state.evento_id, "convidados", f"bf_convidados_{st.session_state.evento_id}")
    )
    # ═══════════════════════════════════════════════════════════════════════════
    # PALETA DE CORES PRINCIPAL (SELETOR VISUAL + TAGS COLORIDAS)
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <div style="margin-top: 14px; margin-bottom: 6px;">
        <label style="font-size: 1.05rem; font-weight: 600; color: #0F172A; display: flex; align-items: center; gap: 8px;">
            <span>🎨 Paleta de Cores Principal</span>
            <span style="font-size: 0.75rem; font-weight: 600; background: #FEF3C7; color: #92400E; padding: 2px 10px; border-radius: 12px;">Seletor Visual & Tags</span>
        </label>
        <p style="font-size: 0.85rem; color: #64748B; margin: 2px 0 8px 0;">
            Monte a paleta oficial do casamento selecionando as cores exatas e visualizando a harmonia entre elas.
        </p>
    </div>
    """, unsafe_allow_html=True)

    paleta = briefing.get("paleta_cores", [])

    # Exibição da faixa contínua da paleta (harmonia visual)
    if paleta:
        strips_html = "".join([f"<div style='flex: 1; height: 100%; background: {c['hex']};' title='{c.get('nome') or c['hex']} ({c['hex']})'></div>" for c in paleta])
        st.markdown(f"""
        <div style="display: flex; height: 36px; border-radius: 10px; overflow: hidden; margin-bottom: 12px; border: 1px solid #CBD5E1; box-shadow: 0 1px 3px rgba(0,0,0,0.06);">
            {strips_html}
        </div>
        """, unsafe_allow_html=True)

        # Tags coloridas com botão de exclusão
        st.markdown("<div style='font-size: 0.82rem; font-weight: 600; color: #475569; margin-bottom: 6px;'>Cores Selecionadas:</div>", unsafe_allow_html=True)
        cols_cores = st.columns(min(len(paleta), 4))
        for idx, cor in enumerate(paleta):
            col_c = cols_cores[idx % min(len(paleta), 4)]
            with col_c:
                c_card, c_del = st.columns([3, 1])
                with c_card:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 8px; background: #FFFFFF; padding: 6px 10px; border-radius: 8px; border: 1px solid #E2E8F0; box-shadow: 0 1px 2px rgba(0,0,0,0.04);">
                        <div style="width: 22px; height: 22px; border-radius: 50%; background: {cor['hex']}; border: 1.5px solid rgba(0,0,0,0.15); flex-shrink: 0;"></div>
                        <div style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                            <div style="font-weight: 600; font-size: 0.82rem; color: #1E293B; line-height: 1.2;">{cor.get('nome') or cor['hex']}</div>
                            <div style="font-size: 0.72rem; color: #64748B;">{cor['hex']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with c_del:
                    if st.button("✕", key=f"del_cor_{idx}_{st.session_state.evento_id}", help=f"Remover {cor.get('nome') or cor['hex']}", use_container_width=True):
                        shared.remover_cor_paleta(st.session_state.evento_id, idx)
                        st.rerun()
    else:
        st.info("💡 Nenhuma cor adicionada à paleta ainda. Escolha uma cor abaixo ou selecione sugestões rápidas!")

    # Controles para adicionar nova cor
    col_pick, col_nome, col_btn = st.columns([1.2, 2.5, 1.3])
    with col_pick:
        nova_cor = st.color_picker("Cor", value="#0F5257", key=f"picker_{st.session_state.evento_id}", help="Clique para abrir o seletor visual de cores")
    with col_nome:
        novo_nome = st.text_input("Nome / Rótulo da cor", placeholder="Ex: Verde Esmeralda, Dourado, Rosé...", key=f"nome_cor_{st.session_state.evento_id}")
    with col_btn:
        st.write("")
        st.write("")
        if st.button("➕ Adicionar", key=f"btn_add_cor_{st.session_state.evento_id}", use_container_width=True):
            shared.adicionar_cor_paleta(st.session_state.evento_id, nova_cor, novo_nome)
            st.rerun()

    # Sugestões rápidas de casamento
    with st.expander("✨ Sugestões de tons populares para casamentos", expanded=False):
        SUGESTOES = [
            ("Verde Esmeralda", "#0F5257"),
            ("Dourado Suave", "#D4AF37"),
            ("Branco Off-White", "#FDFBF7"),
            ("Rosé Gold", "#B76E79"),
            ("Terracota", "#C86446"),
            ("Fendi / Nude", "#C5A880"),
            ("Marsala Clássico", "#5B1E31"),
            ("Azul Serenity", "#8EA8C3"),
            ("Lavanda Suave", "#BDB2CF"),
            ("Verde Oliva", "#556B2F"),
        ]
        sug_cols = st.columns(5)
        for i, (s_nome, s_hex) in enumerate(SUGESTOES):
            with sug_cols[i % 5]:
                st.markdown(f"""
                <div style="display:flex; align-items:center; gap:6px; margin-bottom:4px;">
                    <div style="width:14px; height:14px; border-radius:50%; background:{s_hex}; border:1px solid rgba(0,0,0,0.2);"></div>
                    <span style="font-size:0.75rem; font-weight:600; color:#334155;">{s_nome}</span>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Adicionar", key=f"btn_sug_{i}_{st.session_state.evento_id}", use_container_width=True):
                    shared.adicionar_cor_paleta(st.session_state.evento_id, s_hex, s_nome)
                    st.rerun()

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # RESTRIÇÕES ALIMENTARES (CHECKBOXES RÁPIDAS + OBSERVAÇÕES DETALHADAS)
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <div style="margin-top: 14px; margin-bottom: 4px;">
        <label style="font-size: 1.05rem; font-weight: 600; color: #0F172A; display: flex; align-items: center; gap: 8px;">
            <span>🥗 Restrições Alimentares / Observações do Buffet</span>
        </label>
        <p style="font-size: 0.84rem; color: #64748B; margin: 2px 0 8px 0;">
            Marque as opções mais comuns e utilize o campo abaixo para detalhar mesas, exceções ou nomes de convidados.
        </p>
    </div>
    """, unsafe_allow_html=True)

    restricoes_atuais = briefing.get("restricoes_selecionadas", [])
    OPCOES_RESTRICOES = [
        ("Vegano", "🥗 Vegano"),
        ("Vegetariano", "🥬 Vegetariano"),
        ("Celíaco (Sem Glúten)", "🌾 Celíaco (Sem Glúten)"),
        ("Intolerante à Lactose", "🥛 Intolerante à Lactose"),
    ]

    col_ck1, col_ck2, col_ck3, col_ck4 = st.columns(4)
    cols_ck = [col_ck1, col_ck2, col_ck3, col_ck4]

    for idx, (tag, label) in enumerate(OPCOES_RESTRICOES):
        with cols_ck[idx]:
            st.checkbox(
                label,
                value=tag in restricoes_atuais,
                key=f"ck_restricao_{idx}_{st.session_state.evento_id}",
                on_change=shared.toggle_restricao_alimentar,
                args=(st.session_state.evento_id, tag, f"ck_restricao_{idx}_{st.session_state.evento_id}")
            )

    st.text_area(
        "Observações detalhadas do buffet (mesas, quantidades, exceções)",
        value=briefing["alimentar"],
        placeholder="Ex: 3 vegetarianos na mesa 2, 1 celíaco na mesa da família, sem frutos do mar no coquetel…",
        height=75,
        key=f"bf_alimentar_{st.session_state.evento_id}",
        on_change=shared.update_briefing_field,
        args=(st.session_state.evento_id, "alimentar", f"bf_alimentar_{st.session_state.evento_id}")
    )
    st.text_area(
        "Preferências musicais",
        value=briefing["musica"],
        placeholder="Ex: MPB e sertanejo raiz; evitar funk e pagode…",
        height=70,
        key=f"bf_musica_{st.session_state.evento_id}",
        on_change=shared.update_briefing_field,
        args=(st.session_state.evento_id, "musica", f"bf_musica_{st.session_state.evento_id}")
    )
    st.text_area(
        "Observações gerais",
        value=briefing["obs"],
        height=90,
        key=f"bf_obs_{st.session_state.evento_id}",
        on_change=shared.update_briefing_field,
        args=(st.session_state.evento_id, "obs", f"bf_obs_{st.session_state.evento_id}")
    )
    st.caption("✨ As alterações no briefing são salvas automaticamente.")
else:
    st.info("🔒 Briefing registrado pelo cerimonial.")
    
    # Exibição das referências visuais no modo somente leitura
    st.markdown("#### 📸 Estilo do Evento & Referências Visuais")
    referencias = briefing.get("referencias_visuais", [])
    if referencias:
        cols = st.columns(3)
        for idx, ref in enumerate(referencias):
            col = cols[idx % 3]
            with col:
                st.markdown(f"""
                <div class="ref-card">
                    <img src="{ref['data_url']}" class="ref-card-img" alt="{ref.get('nome', 'Inspiração')}">
                    <div class="ref-card-title" title="{ref.get('nome', '')}">{ref.get('nome', 'Inspiração')}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🔍 Ver ampliada", key=f"btn_ver_ro_{ref['id']}", use_container_width=True):
                    modal_visualizar_referencia(ref)
    else:
        st.markdown("<p style='color: #64748B; font-style: italic;'>Nenhuma foto de referência anexada.</p>", unsafe_allow_html=True)
        
    p_link = briefing.get("pinterest_link", "").strip()
    if p_link and p_link.startswith("http"):
        st.link_button("📌 Ver Pasta no Pinterest", url=p_link)
        
    if briefing.get("estilo"):
        shared.bf_field("Conceito / Detalhes de Estilo", briefing["estilo"])
        
    val_conv = briefing.get("convidados")
    try:
        val_conv_num = int(val_conv or 0)
        exib_conv = f"{val_conv_num} convidados" if val_conv_num > 0 else ""
    except Exception:
        exib_conv = str(val_conv) if val_conv else ""

    shared.bf_field("Convidados estimados",      exib_conv)

    # Exibição da paleta de cores no modo leitura
    paleta = briefing.get("paleta_cores", [])
    if paleta:
        strips_html = "".join([f"<div style='flex: 1; height: 100%; background: {c['hex']};' title='{c.get('nome') or c['hex']} ({c['hex']})'></div>" for c in paleta])
        st.markdown(f"""
        <div style="margin-top: 10px; margin-bottom: 6px;">
            <div class="bf-label">Paleta de cores principal</div>
            <div style="display: flex; height: 30px; border-radius: 8px; overflow: hidden; margin: 6px 0 8px 0; border: 1px solid #CBD5E1; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                {strips_html}
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                {' '.join([f'''<div style="display:inline-flex; align-items:center; gap:6px; background:#fff; padding:4px 10px; border-radius:16px; border:1px solid #e2e8f0; font-size:0.8rem; font-weight:600; color:#1e293b;"><span style="width:14px; height:14px; border-radius:50%; background:{c['hex']}; border:1px solid rgba(0,0,0,0.2); display:inline-block;"></span>{c.get('nome') or c['hex']} <small style="color:#64748b; font-weight:normal;">({c['hex']})</small></div>''' for c in paleta])}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        shared.bf_field("Paleta de cores", briefing.get("cores", ""))

    # Exibição das restrições alimentares no modo leitura
    restricoes_atuais = briefing.get("restricoes_selecionadas", [])
    obs_alim = briefing.get("alimentar", "").strip()
    
    st.markdown("<div style='margin-top: 10px; margin-bottom: 4px;'><div class='bf-label'>Restrições alimentares / buffet</div></div>", unsafe_allow_html=True)
    if restricoes_atuais:
        chips_html = " ".join([f"<span style='display:inline-block; background:#FEF2F2; color:#991B1B; font-weight:600; font-size:0.78rem; padding:3px 10px; border-radius:12px; border:1px solid #FECACA; margin-right:6px; margin-bottom:4px;'>🥗 {r}</span>" for r in restricoes_atuais])
        st.markdown(f"<div style='margin-bottom:6px;'>{chips_html}</div>", unsafe_allow_html=True)
    
    if obs_alim:
        st.markdown(f"<div style='font-size:0.9rem; color:#334155; margin-bottom: 8px;'>{obs_alim}</div>", unsafe_allow_html=True)
    elif not restricoes_atuais:
        st.markdown("<em style='opacity:0.45; display:block; margin-bottom: 8px;'>Não informado</em>", unsafe_allow_html=True)

    shared.bf_field("Preferências musicais",     briefing["musica"])
    shared.bf_field("Observações gerais",        briefing["obs"])


