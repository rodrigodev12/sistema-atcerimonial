import streamlit as st
import pandas as pd
import shared

evento_atual = shared.get_evento_atual()
if not evento_atual:
    st.info("Por favor, selecione ou acesse um evento válido.")
    st.stop()

st.markdown(f"### Dashboard — {evento_atual['noivos']}  ·  📅 {evento_atual['data']}")

# ⏳ Contagem Regressiva
from datetime import datetime
import pytz
try:
    data_val = str(evento_atual["data"]) if pd.notna(evento_atual["data"]) else ""
    data_evento_str = data_val.strip()
    data_evento = datetime.strptime(data_evento_str, "%d/%m/%Y").date()
    
    # Define o fuso horário do Brasil e pega a data de hoje correta no Brasil
    fuso_brasil = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso_brasil).date()
    
    # Cálculo exato dos dias restantes
    dias = (data_evento - hoje).days
    
    if dias > 0:
        st.info(f"💍 **Faltam {dias} dias para o grande dia! ({evento_atual['data']})**")
    elif dias == 0:
        st.success(f"🎉 **É hoje! O grande dia chegou! 💍**")
    else:
        st.success(f"✨ **O casamento aconteceu em {evento_atual['data']}! 🎉**")
except Exception:
    st.warning(f"📅 Data do evento cadastrada: **{evento_atual['data']}** (insira no formato DD/MM/AAAA para habilitar contagem)")

# Se for noivos, exibe um card amigável no topo para copiar/compartilhar o portal (visível no celular sem abrir menu)
if st.session_state.tipo_usuario == "cliente":
    link_acesso = shared.obter_link_acesso(st.session_state.evento_id)
    import streamlit.components.v1 as components
    components.html(f"""
    <style>
      * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
      body {{ background: transparent; }}
      .share-card {{
        display: flex;
        align-items: center;
        gap: 10px;
        background: #F0FDFA;
        border: 1px solid #CCFBF1;
        border-radius: 8px;
        padding: 10px 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      }}
      .share-text {{
        flex: 1;
        font-size: 13px;
        color: #0F766E;
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }}
      .share-btn {{
        background: #0D9488;
        color: #FFFFFF;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        gap: 6px;
      }}
      .share-btn:hover {{ background: #0F766E; }}
      .share-btn.success {{ background: #10B981; }}
    </style>
    <div class="share-card">
      <span class="share-text">{link_acesso}</span>
      <button class="share-btn" id="shareBtn" onclick="copyLink()">
        <span class="icon">📋</span>
        <span id="btnText">Copiar Link</span>
      </button>
    </div>
    <script>
      function copyLink() {{
        var link = "{link_acesso}";
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
        var btn = document.getElementById('shareBtn');
        var txt = document.getElementById('btnText');
        btn.classList.add('success');
        btn.querySelector('.icon').textContent = '✅';
        txt.textContent = 'Copiado!';
        setTimeout(function() {{
          btn.classList.remove('success');
          btn.querySelector('.icon').textContent = '📋';
          txt.textContent = 'Copiar Link';
        }}, 2000);
      }}
    </script>
    """, height=50)

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
    for opt in shared.STATUS_OPCOES:
        qtd  = int((df_f["STATUS"] == opt).sum())
        pct_s = (qtd / total * 100) if total > 0 else 0
        cor  = shared.STATUS_CORES[opt]
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
