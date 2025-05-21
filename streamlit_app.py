# 2. Integración en un Dashboard (Streamlit)

# Importacion de librerias
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

##############################
# Configuracion del Dashboard
##############################

# Configuración inicial y basica de la pagina

st.set_page_config(
    page_title="Análisis de Ventas", 
    layout="wide",
    initial_sidebar_state='expanded' )


st.title("📊 Dashboard de Ventas y Clientes")
st.markdown("Análisis interactivo basado en ventas, clientes y finanzas para mejorar la estrategia de marketing.")

# configuracion de los graficos
sns.set_style('whitegrid')


# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Time"] = pd.to_datetime(df["Time"], format='%H:%M').dt.time
    df["Day"] = df["Date"].dt.day
    df["Month"] = df["Date"].dt.month
    df["Weekday"] = df["Date"].dt.day_name()
    return df

df = load_data()

# ===========================
# Barra lateral - Filtros
# ===========================
st.sidebar.header('Filtros del dashboard')

# Filtros únicos
sucursales = st.sidebar.multiselect("Sucursal", options=df["Branch"].unique(), default=df["Branch"].unique())
tipos_cliente = st.sidebar.multiselect("Tipo de Cliente", options=df["Customer type"].unique(), default=df["Customer type"].unique())

# Aplicar filtros
df_filtrado = df[(df["Branch"].isin(sucursales)) & (df["Customer type"].isin(tipos_cliente))]


# ===========================
# Creación de pestañas
# ===========================
tab1, tab2, tab3 = st.tabs(["📈 Ventas", "👥 Clientes", "💰 Finanzas"])


#==========================
# Creacion pestaña Ventas
#==========================
with tab1:
    st.subheader("🔹 Evolución de las Ventas Totales con Indicadores")

    # Agrupar ventas por fecha
    ventas_por_fecha = df_filtrado.groupby('Date')['Total'].sum().reset_index()

    # Calcular promedio
    promedio_ventas = ventas_por_fecha['Total'].mean()

    # Marcar si está sobre el promedio
    ventas_por_fecha['SobrePromedio'] = ventas_por_fecha['Total'] > promedio_ventas

    # Crear el gráfico personalizado
    fig, ax = plt.subplots(figsize=(12, 6))

    # Línea general
    ax.plot(ventas_por_fecha['Date'], ventas_por_fecha['Total'], color='lightblue', label='Ventas Diarias')

    # Puntos bajo el promedio
    ax.scatter(
        ventas_por_fecha[~ventas_por_fecha['SobrePromedio']]['Date'],
        ventas_por_fecha[~ventas_por_fecha['SobrePromedio']]['Total'],
        color='black', label='Bajo el promedio'
    )

    # Puntos sobre el promedio
    ax.scatter(
        ventas_por_fecha[ventas_por_fecha['SobrePromedio']]['Date'],
        ventas_por_fecha[ventas_por_fecha['SobrePromedio']]['Total'],
        color='red', label='Sobre el promedio'
    )

    # Línea de promedio
    ax.axhline(promedio_ventas, color='green', linestyle='--', label=f'Promedio diario = {promedio_ventas:.2f}')

    # Etiquetas para los 3 días con mayor venta
    top_dias = ventas_por_fecha.sort_values(by='Total', ascending=False).head(3)
    for _, fila in top_dias.iterrows():
        ax.text(fila['Date'], fila['Total'] + 10, f"{fila['Total']:.0f}", color='black', ha='center')

    # Detalles del gráfico
    ax.set_title('Evolución de las Ventas Totales con Indicadores de Alto Rendimiento')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Ventas Totales ($)')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True)
    ax.legend()
    plt.tight_layout()

    st.pyplot(fig)


    # Ingresos por Línea de Producto
    st.subheader("🔹 Ingresos por Línea de Producto")

    lineas_disponibles = df_filtrado["Product line"].unique()
    lineas_seleccionadas = st.sidebar.multiselect(
        "Línea(s) de Producto",
        options=sorted(lineas_disponibles),
        default=sorted(lineas_disponibles)
    )

    df_lineas = df_filtrado[df_filtrado["Product line"].isin(lineas_seleccionadas)]
    
    # Subtabs para los gráficos
    linea_subtab1, linea_subtab2 = st.tabs(["📊 Gráfico de Barras", "🥧 Pie Chart"])
    # 📊 Subtab: Barras
    with linea_subtab1:
        ingresos = df_lineas.groupby("Product line")["Total"].sum().sort_values()
        fig_barras, ax_barras = plt.subplots(figsize=(10, 5))
        sns.barplot(x=ingresos.values, y=ingresos.index, palette="Blues_r", ax=ax_barras)
        ax_barras.set_title("Ingresos por Línea de Producto", fontsize=14)
        ax_barras.set_xlabel("Total ($)")
        ax_barras.set_ylabel("Línea de Producto")
        ax_barras.grid(axis='x', linestyle='--', alpha=0.5)
        st.pyplot(fig_barras)

    # 🥧 Subtab: Pie Chart
    with linea_subtab2:
        ingresos_por_linea = df_lineas.groupby('Product line')['Total'].sum()
        fig_pie, ax_pie = plt.subplots(figsize=(8, 8))
        ax_pie.pie(
            ingresos_por_linea,
            labels=ingresos_por_linea.index,
            autopct='%1.1f%%',
            startangle=140,
            colors=sns.color_palette('Set2')
        )
        ax_pie.set_title('Distribución de Ingresos por Línea de Producto')
        ax_pie.axis('equal')  # Para que sea un círculo perfecto
        plt.tight_layout()
        st.pyplot(fig_pie)
    
    
    
    # Relación entre Costo y Ganancia Bruta
    st.subheader("🔹 Relación entre Costo y Ganancia Bruta")

    fig3, ax3 = plt.subplots(figsize=(8, 5))
    sns.scatterplot(data=df_filtrado, x="cogs", y="gross income", hue="Branch", alpha=0.7, ax=ax3)
    ax3.set_title("Costo vs. Ganancia Bruta", fontsize=14)
    ax3.set_xlabel("Costo de Bienes Vendidos (cogs)")
    ax3.set_ylabel("Ingreso Bruto (gross income)")
    ax3.legend(title="Sucursal")
    st.pyplot(fig3)

    # Análisis de Correlación Numérica
    st.subheader("🔹 Análisis de Correlación Numérica")

    variables_numericas = ["Unit price", "Quantity", "Tax 5%", "Total", "cogs", "gross income", "Rating"]
    df_corr = df_filtrado[variables_numericas].corr()

    fig4, ax4 = plt.subplots(figsize=(10, 6))
    sns.heatmap(df_corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax4)
    ax4.set_title("Matriz de Correlación entre Variables Numéricas", fontsize=14)
    st.pyplot(fig4)

# =================================================
# Creacion pestaña Clientes
#==================================================
with tab2:
    st.subheader("🔹 Distribución de la Calificación de Clientes")

    # Clasificación con emojis
    def clasificar_rating(valor):
        if valor <= 5.0:
            return "Muy Malo"
        elif valor <= 6.0:
            return "Malo"
        elif valor <= 7.0:
            return "Regular"
        elif valor <= 8.0:
            return "Bueno"
        elif valor <= 9.0:
            return "Muy Bueno"
        else:
            return "Excelente"

    # Agregar columna con categorías de rating
    df['Rating_categoria'] = df['Rating'].apply(clasificar_rating)

    # Conteo y orden
    conteo = df['Rating_categoria'].value_counts().sort_values(ascending=False)
    categorias = conteo.index
    total = conteo.sum()

    
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=conteo.values, y=categorias, palette='viridis', ax=ax)

    # Mostrar porcentaje en cada barra
    for i, valor in enumerate(conteo.values):
        porcentaje = valor / total * 100
        ax.text(valor + 1, i, f'{porcentaje:.1f}%', va='center', fontsize=10)

    ax.set_xlabel('Cantidad de Clientes')
    ax.set_ylabel('Categoría')
    ax.set_title('Distribución de la Calificación de Clientes')
    ax.grid(axis='x', linestyle='--', alpha=0.6)

    st.pyplot(fig)



    # fig3, ax3 = plt.subplots(figsize=(10, 4))
    # sns.histplot(df_filtrado["Rating"], bins=10, kde=True, color="skyblue", ax=ax3)
    # ax3.set_title("Distribución de Calificaciones de Clientes", fontsize=14)
    # ax3.set_xlabel("Calificación")
    # ax3.set_ylabel("Frecuencia")
    # st.pyplot(fig3)

    # st.subheader("🔹 Comparación del Gasto por Tipo de Cliente")

    # gasto_por_tipo = df_filtrado.groupby("Customer type")["Total"].sum().reset_index()

    # fig4, ax4 = plt.subplots(figsize=(7, 4))
    # sns.barplot(data=gasto_por_tipo, x="Customer type", y="Total", palette="pastel", ax=ax4)
    # ax4.set_title("Gasto Total por Tipo de Cliente", fontsize=14)
    # ax4.set_ylabel("Total ($)")
    # ax4.set_xlabel("Tipo de Cliente")
    # st.pyplot(fig4)


    st.subheader("🔸 Comparación del Gasto por Tipo de Cliente")

    if 'Customer type' in df.columns and 'Total' in df.columns:

        subtab1, subtab2 = st.tabs(["📦 Distribución (Boxplot)", "📊 Promedio (Barplot)"])

        with subtab1:
            st.write("Visualiza cómo varía el gasto dentro de cada tipo de cliente.")
            fig1, ax1 = plt.subplots(figsize=(8, 5))
            sns.boxplot(data=df, x='Customer type', y='Total', palette='Set2', ax=ax1)
            ax1.set_title('Distribución del Gasto Total por Tipo de Cliente')
            ax1.set_xlabel('Tipo de Cliente')
            ax1.set_ylabel('Gasto Total')
            ax1.grid(axis='y', linestyle='--', alpha=0.6)
            st.pyplot(fig1)

        with subtab2:
            st.write("Compara el promedio de gasto entre tipos de clientes.")
            gasto_promedio = df.groupby('Customer type')['Total'].mean().sort_values(ascending=False)
            fig2, ax2 = plt.subplots(figsize=(8, 5))
            sns.barplot(x=gasto_promedio.values, y=gasto_promedio.index, palette='coolwarm', ax=ax2)
            for i, valor in enumerate(gasto_promedio.values):
                ax2.text(valor + 1, i, f"${valor:.1f}", va='center', fontsize=10)
            ax2.set_title('Promedio de Gasto por Tipo de Cliente')
            ax2.set_xlabel('Gasto Promedio')
            ax2.set_ylabel('Tipo de Cliente')
            ax2.grid(axis='x', linestyle='--', alpha=0.6)
            st.pyplot(fig2)
    else:
        st.warning("⚠️ No se encuentran las columnas 'Tipo_Cliente' y 'Total' en el DataFrame.")





# ==================================================
# Creacion pestaña Finanzas
#===================================================
with tab3:
    st.subheader("💳 Métodos de Pago Preferidos")

    if 'Payment' in df.columns:
        # Subtabs para métodos de pago
        pago_subtab1, pago_subtab2 = st.tabs(["📊 Barras", "🥧 Pie Chart"])

        with pago_subtab1:
            st.write("Cantidad de clientes por método de pago.")
            payment_counts = df['Payment'].value_counts()
            fig1, ax1 = plt.subplots(figsize=(5, 5))
            sns.barplot(x=payment_counts.values, y=payment_counts.index, palette='pastel', ax=ax1)
            ax1.set_xlabel('Cantidad de Clientes')
            ax1.set_ylabel('Método de Pago')
            ax1.set_title('Frecuencia de Métodos de Pago')
            for i, valor in enumerate(payment_counts.values):
                ax1.text(valor + 1, i, str(valor), va='center')
            ax1.grid(axis='x', linestyle='--', alpha=0.6)
            st.pyplot(fig1)

        with pago_subtab2:
            st.write("Porcentaje de clientes por método de pago.")
            fig2, ax2 = plt.subplots(figsize=(5, 6))
            ax2.pie(payment_counts, labels=payment_counts.index, autopct='%1.1f%%',
                    colors=sns.color_palette('pastel'), startangle=90)
            ax2.set_title('Distribución de Métodos de Pago')
            ax2.axis('equal')
            st.pyplot(fig2)
    else:
        st.warning("⚠️ No se encuentra la columna 'Payment' en el DataFrame.")

    # Subtabs para el análisis de ingreso bruto
    st.subheader("🔹 Ingreso Bruto por Sucursal y Línea de Producto")
    ingreso_subtab1, ingreso_subtab2, ingreso_subtab3 = st.tabs([
        "📊 Barras Apiladas", "🌡️ Heatmap", "📋 Tabla Resumida"
    ])

    # 1. 📊 Gráfico de barras apiladas
    with ingreso_subtab1:
        grouped_income = df.groupby(['Branch', 'Product line'])['gross income'].sum().reset_index()
        pivot_income = grouped_income.pivot(index='Branch', columns='Product line', values='gross income')

        fig3, ax3 = plt.subplots(figsize=(10, 6))
        pivot_income.plot(kind='bar', stacked=True, colormap='tab20', ax=ax3)
        ax3.set_title('Contribución de cada Línea de Producto al Ingreso Bruto por Sucursal')
        ax3.set_xlabel('Sucursal')
        ax3.set_ylabel('Ingreso Bruto Total')
        ax3.legend(title='Línea de Producto', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax3.grid(axis='y', linestyle='--', alpha=0.5)
        st.pyplot(fig3)

    # 2. 🌡️ Heatmap
    with ingreso_subtab2:
        pivot_heatmap = grouped_income.pivot(index='Product line', columns='Branch', values='gross income')
        fig4, ax4 = plt.subplots(figsize=(8, 6))
        sns.heatmap(pivot_heatmap, annot=True, fmt=".0f", cmap='YlGnBu', ax=ax4)
        ax4.set_title('Ingreso Bruto por Línea de Producto y Sucursal')
        ax4.set_xlabel('Sucursal')
        ax4.set_ylabel('Línea de Producto')
        st.pyplot(fig4)

    # 3. 📋 Tabla Resumida
    with ingreso_subtab3:
        tabla_ingresos = pd.pivot_table(
            df,
            values='gross income',
            index='Product line',
            columns='Branch',
            aggfunc='sum',
            margins=True,
            margins_name='Total general'
        ).round(2)

        st.write("Resumen de Ingresos por Línea de Producto y Sucursal")
        st.dataframe(tabla_ingresos.style
                     .format("{:.2f}")
                     .set_table_styles([
                         {'selector': 'thead th', 'props': [('border-bottom', '2px solid black')]},
                         {'selector': 'tbody tr:last-child', 'props': [('border-top', '2px solid black')]}
                     ])
        )

