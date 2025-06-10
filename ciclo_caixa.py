import streamlit as st

st.set_page_config(page_title="Ciclo de Caixa", layout="centered")

st.title("🧾 Cálculo do Ciclo de Caixa")

# Entradas
receita = st.number_input("Receita Líquida (DRE) - R$", min_value=0.0, value=30000.0, format="%.2f")
custo = st.number_input("Custo (DRE) - R$", min_value=0.0, value=30000.0, format="%.2f")
estoques = st.number_input("Estoques (Balanço) - R$", min_value=0.0, value=1500.0, format="%.2f")
clientes = st.number_input("Contas a Receber (Balanço) - R$", min_value=0.0, value=1500.0, format="%.2f")
fornecedores = st.number_input("Fornecedores (Balanço) - R$", min_value=0.0, value=300.0, format="%.2f")
dias = st.number_input("Período (em dias)", min_value=1, value=360, step=1)

if st.button("Calcular"):
    try:
        pme = (estoques / custo) * dias
        pmr = (clientes / receita) * dias
        pmp = (fornecedores / custo) * dias
        co = pme + pmr
        cc = co - pmp

        st.subheader("📊 Resultados")
        st.write(f"**PME:** {pme:.0f} dias")
        st.write(f"**PMR:** {pmr:.0f} dias")
        st.write(f"**PMP:** {pmp:.0f} dias")
        st.write(f"**Ciclo Operacional (CO):** {co:.0f} dias")
        st.write(f"**Ciclo de Caixa (CC):** {cc:.0f} dias")


        if cc > 0:
            st.success(f"A empresa paga **{cc:.0f} dias antes** de receber.")
        else:
            st.success(f"A empresa recebe **{abs(cc):.0f} dias antes** de pagar.")
    except ZeroDivisionError:
        st.error("⚠️ Receita ou Custo não podem ser zero.")
