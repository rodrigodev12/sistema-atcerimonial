import streamlit as st
import pandas as pd
import shared

evento_atual = shared.get_evento_atual()
if not evento_atual:
    st.info("Por favor, selecione ou acesse um evento válido.")
    st.stop()

is_admin = st.session_state.tipo_usuario == "admin"

st.markdown(f"### Roteiro do Evento — {evento_atual['noivos']}")
roteiro = evento_atual.get("roteiro", [r.copy() for r in shared.ROTEIRO_PADRAO])

def render_linha_tempo(roteiro_list):
    st.markdown("""
    <style>
    .timeline-container {
        padding: 5px 2px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .timeline-item {
        position: relative;
        padding-left: 26px;
        margin-bottom: 22px;
        border-left: 2px solid #00B4D8;
    }
    .timeline-dot {
        position: absolute;
        left: -6px;
        top: 6px;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #0B2545;
        border: 2px solid #00B4D8;
    }
    .timeline-time {
        font-weight: 700;
        font-size: 13px;
        color: #0B2545;
        margin-bottom: 6px;
        display: inline-block;
        background: #E0F2FE;
        padding: 2px 8px;
        border-radius: 4px;
    }
    .timeline-content {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .timeline-content:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
    }
    .timeline-title {
        font-weight: 600;
        font-size: 14px;
        color: #0F172A;
        margin-bottom: 8px;
        line-height: 1.4;
    }
    .timeline-meta {
        font-size: 12px;
        color: #475569;
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
    }
    .meta-badge {
        background: #F1F5F9;
        padding: 2px 8px;
        border-radius: 9999px;
        border: 1px solid #E2E8F0;
        white-space: nowrap;
        display: inline-flex;
        align-items: center;
    }
    .timeline-obs {
        font-size: 12px;
        color: #64748B;
        border-left: 2px dashed #CBD5E1;
        padding-left: 8px;
        margin-top: 8px;
        background: #FAFAFA;
        padding: 4px 8px;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

    timeline_html = '<div class="timeline-container">'
    for r in roteiro_list:
        horario = r.get("HORÁRIO", "") or r.get("horario", "")
        momento = r.get("MOMENTO", "") or r.get("momento", "")
        responsavel = r.get("RESPONSÁVEL", "") or r.get("responsavel", "")
        local = r.get("LOCAL", "") or r.get("local", "")
        obs = r.get("OBSERVAÇÃO", "") or r.get("observacao", "")
        
        obs_html = f'<div class="timeline-obs">💡 <b>Obs:</b> {obs}</div>' if obs else ""
        
        timeline_html += f"""
        <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-time">{horario}</div>
            <div class="timeline-content">
                <div class="timeline-title">{momento}</div>
                <div class="timeline-meta">
                    <span class="meta-badge">📍 {local}</span>
                    <span class="meta-badge">👤 {responsavel}</span>
                </div>
                {obs_html}
            </div>
        </div>
        """
    timeline_html += '</div>'
    st.markdown(timeline_html, unsafe_allow_html=True)

if is_admin:
    df_rot  = pd.DataFrame(roteiro)
    rot_cfg = {
        "HORÁRIO":     st.column_config.TextColumn("Horário",     width="small"),
        "MOMENTO":     st.column_config.TextColumn("Momento",     width="large"),
        "RESPONSÁVEL": st.column_config.TextColumn("Responsável", width="medium"),
        "LOCAL":       st.column_config.TextColumn("Local",       width="medium"),
        "OBSERVAÇÃO":  st.column_config.TextColumn("Observação",  width="large"),
    }

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
        shared.salvar_dados(st.session_state.dados)
        st.toast("Roteiro salvo!", icon="⏱️")
        st.rerun()

    cr1, _ = st.columns([2.5, 9.5])
    with cr1:
        excel_rot = shared.exportar_excel(evento_atual)
        st.download_button(
            "📥 Exportar Excel",
            data=excel_rot,
            file_name=f"AT_{evento_atual['noivos'].replace(' ', '_').replace('&','e')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_rot",
        )
    st.caption("✨ As alterações no roteiro são salvas automaticamente.")
    
    st.markdown("<hr style='opacity:.15; margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown("#### 👀 Visualização da Linha do Tempo (Noivos)")
    render_linha_tempo(roteiro)
else:
    render_linha_tempo(roteiro)
