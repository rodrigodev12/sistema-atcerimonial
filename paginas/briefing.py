import streamlit as st
import shared

evento_atual = shared.get_evento_atual()
if not evento_atual:
    st.info("Por favor, selecione ou acesse um evento válido.")
    st.stop()

is_admin = st.session_state.tipo_usuario == "admin"

st.markdown(f"### Briefing Inicial — {evento_atual['noivos']}")
briefing = shared.get_briefing(evento_atual)

if is_admin or st.session_state.tipo_usuario == "cliente":
    st.text_area(
        "Estilo do evento / referências visuais",
        value=briefing["estilo"],
        placeholder="Ex: Rústico chic, paleta verde e terracota, ao ar livre…",
        height=80,
        key=f"bf_estilo_{st.session_state.evento_id}",
        on_change=shared.update_briefing_field,
        args=(st.session_state.evento_id, "estilo", f"bf_estilo_{st.session_state.evento_id}")
    )
    st.text_input(
        "Número estimado de convidados",
        value=briefing["convidados"],
        key=f"bf_convidados_{st.session_state.evento_id}",
        on_change=shared.update_briefing_field,
        args=(st.session_state.evento_id, "convidados", f"bf_convidados_{st.session_state.evento_id}")
    )
    st.text_input(
        "Paleta de cores principal",
        value=briefing["cores"],
        placeholder="Ex: Branco, verde esmeralda e dourado",
        key=f"bf_cores_{st.session_state.evento_id}",
        on_change=shared.update_briefing_field,
        args=(st.session_state.evento_id, "cores", f"bf_cores_{st.session_state.evento_id}")
    )
    st.text_area(
        "Restrições alimentares / observações do buffet",
        value=briefing["alimentar"],
        placeholder="Ex: 3 vegetarianos, 1 celíaco, sem glúten na mesa 5…",
        height=70,
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
    shared.bf_field("Estilo do evento",         briefing["estilo"])
    shared.bf_field("Convidados estimados",      briefing["convidados"])
    shared.bf_field("Paleta de cores",           briefing["cores"])
    shared.bf_field("Restrições alimentares",    briefing["alimentar"])
    shared.bf_field("Preferências musicais",     briefing["musica"])
    shared.bf_field("Observações gerais",        briefing["obs"])
