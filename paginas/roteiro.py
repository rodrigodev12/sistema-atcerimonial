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
else:
    st.dataframe(df_rot, column_config=rot_cfg, hide_index=True, use_container_width=True)
