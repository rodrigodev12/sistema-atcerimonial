import streamlit as st
import pandas as pd
import random
import string
import shared

evento_atual = shared.get_evento_atual()
if not evento_atual:
    st.info("Por favor, selecione ou acesse um evento válido.")
    st.stop()

is_admin = st.session_state.tipo_usuario == "admin"
if not is_admin:
    st.warning("Acesso restrito ao cerimonial.")
    st.stop()

st.markdown(f"### Checklist Cerimonial — {evento_atual['noivos']}")

sub_checklist_cerim = st.radio("Seção", ["📊 Acompanhar Checklist", "⚙️ Gerenciar Tarefas"], horizontal=True, label_visibility="collapsed", key="sub_ck_cerim")
checklist_cerim_items = shared.get_checklist_cerimonial(evento_atual)

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
                key_name = f"ck_cerim_{st.session_state.evento_id}_{item['id']}"
                states[item["id"]] = st.checkbox(
                    item["tarefa"],
                    value=val,
                    key=key_name,
                    on_change=shared.toggle_checklist_item,
                    args=(st.session_state.evento_id, item["id"], key_name, "cerimonial")
                )

    total_ck  = len(checklist_cerim_items)
    feitos_ck = sum(1 for i in checklist_cerim_items if i["feito"])
    st.write("")
    st.progress(feitos_ck / total_ck if total_ck else 0)
    st.markdown(f"**{feitos_ck} de {total_ck} tarefas concluídas**")
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
        shared.salvar_dados(st.session_state.dados)
        st.toast("Checklist Cerimonial atualizado!", icon="⚙️")
        st.rerun()
