import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Calculadora ACS CTE-DB-HE4",
    page_icon="💧",
    layout="centered"
)

# Título y descripción
st.title("Calculadora de Demanda de Agua Caliente Sanitaria (ACS)")
st.markdown("Esta aplicación calcula la demanda diaria de Agua Caliente Sanitaria (ACS) según el Código Técnico de la Edificación (CTE-DB-HE4).")

# Datos de referencia (Anejo F del CTE-DB-HE4)
# Tabla a: ocupación mínima según número de dormitorios
tabla_a = pd.DataFrame({
    'Número de dormitorios': [1, 2, 3, 4, 5, 6, '≥6'],
    'Número de personas': [1.5, 3, 4, 5, 6, 6, 7]
})

# Tabla b: factores de centralización según número de viviendas
tabla_b = pd.DataFrame({
    'Número de viviendas': ['≤3', '4-10', '11-20', '21-50', '51-75', '76-100', '≥101'],
    'Factor de centralización': [1, 0.95, 0.90, 0.85, 0.80, 0.75, 0.70]
})

# Tabla c: valores para usos terciarios
tabla_c = pd.DataFrame({
    'Criterio de demanda': [
        'Hospitales y clínicas', 
        'Ambulatorio y centro de salud', 
        'Hotel *****', 
        'Hotel ****', 
        'Hotel ***', 
        'Hotel/hostal **', 
        'Camping', 
        'Hostal/pensión *', 
        'Residencia', 
        'Centro penitenciario', 
        'Albergue', 
        'Vestuarios/duchas colectivas', 
        'Escuela sin ducha', 
        'Escuela con ducha', 
        'Cuarteles', 
        'Fábricas y talleres', 
        'Oficinas', 
        'Gimnasios', 
        'Restaurantes', 
        'Cafeterías'
    ],
    'Litros/día·persona': [
        55, 
        41, 
        69, 
        55, 
        41, 
        34, 
        21, 
        28, 
        41, 
        28, 
        24, 
        21, 
        4, 
        21, 
        28, 
        21, 
        2, 
        21, 
        8, 
        1
    ]
})

# Crear formulario para entrada de datos
with st.form("formulario_acs"):
    # Tipo de uso
    tipo_uso = st.radio(
        "Tipo de uso:",
        ["Residencial", "Terciario"],
        index=0,
        horizontal=True
    )
    
    if tipo_uso == "Residencial":
        # Número de dormitorios
        num_dormitorios = st.number_input(
            "Número de dormitorios:",
            min_value=1,
            max_value=10,
            value=2,
            step=1,
            help="Introduce el número de dormitorios (mínimo 1)"
        )
        
        # Tipo de edificación
        tipo_edificacion = st.radio(
            "Tipo de edificación:",
            ["Unifamiliar", "Colectiva"],
            index=0,
            horizontal=True
        )
        
        if tipo_edificacion == "Colectiva":
            # Número de viviendas
            num_viviendas = st.number_input(
                "Número de viviendas:",
                min_value=1,
                max_value=200,
                value=10,
                step=1,
                help="Introduce el número total de viviendas en la edificación"
            )
    else:  # Terciario
        # Criterio de demanda para uso terciario
        criterio_terciario = st.selectbox(
            "Criterio de demanda:",
            tabla_c['Criterio de demanda'].tolist()
        )
        
        # Número de personas/usuarios
        num_personas_terciario = st.number_input(
            "Número de personas/usuarios:",
            min_value=1,
            value=10,
            step=1,
            help="Introduce el número de personas o usuarios"
        )
    
    # Temperatura de servicio
    temp_servicio = st.slider(
        "Temperatura de servicio (°C):",
        min_value=30,
        max_value=90,
        value=60,
        step=1,
        help="Temperatura de servicio del agua caliente sanitaria"
    )
    
    # Botón de cálculo
    submitted = st.form_submit_button("Calcular demanda ACS")

# Función para obtener personas según dormitorios (Tabla a)
def obtener_personas(dormitorios):
    """Devuelve el número de personas según el número de dormitorios (Tabla a)"""
    if dormitorios >= 6:
        return 7
    return tabla_a.loc[tabla_a['Número de dormitorios'] == dormitorios, 'Número de personas'].values[0]

# Función para obtener factor de centralización (Tabla b)
def obtener_factor_centralizacion(viviendas):
    """Devuelve el factor de centralización según el número de viviendas (Tabla b)"""
    if viviendas <= 3:
        return 1
    elif viviendas <= 10:
        return 0.95
    elif viviendas <= 20:
        return 0.90
    elif viviendas <= 50:
        return 0.85
    elif viviendas <= 75:
        return 0.80
    elif viviendas <= 100:
        return 0.75
    else:
        return 0.70

# Función para obtener litros por persona en uso terciario (Tabla c)
def obtener_litros_terciario(criterio):
    """Devuelve los litros por persona para el criterio de uso terciario (Tabla c)"""
    return tabla_c.loc[tabla_c['Criterio de demanda'] == criterio, 'Litros/día·persona'].values[0]

# Función para calcular la demanda de ACS
def calcular_demanda_acs(uso, dormitorios=None, edificacion=None, viviendas=None, 
                         criterio_terciario=None, personas_terciario=None, 
                         temperatura=60):
    """
    Calcula la demanda diaria de ACS según el CTE-DB-HE4
    
    Args:
        uso: 'Residencial' o 'Terciario'
        dormitorios: Número de dormitorios (para uso residencial)
        edificacion: 'Unifamiliar' o 'Colectiva' (para uso residencial)
        viviendas: Número de viviendas (para edificación colectiva)
        criterio_terciario: Criterio de demanda para uso terciario
        personas_terciario: Número de personas para uso terciario
        temperatura: Temperatura de servicio en °C
    
    Returns:
        Demanda diaria de ACS en litros/día
    """
    # Valor de referencia: 28 L/día·persona a 60°C
    demanda_referencia = 28
    
    if uso == "Residencial":
        # Calcular personas mínimas según número de dormitorios
        personas = obtener_personas(dormitorios)
        
        # Calcular demanda base
        demanda = demanda_referencia * personas
        
        # Si es edificación colectiva, aplicar factor de centralización
        if edificacion == "Colectiva":
            factor = obtener_factor_centralizacion(viviendas)
            demanda = demanda * viviendas * factor
    else:  # Terciario
        # Obtener litros por persona según criterio
        litros_persona = obtener_litros_terciario(criterio_terciario)
        
        # Calcular demanda
        demanda = litros_persona * personas_terciario
    
    # Ajustar si la temperatura es diferente a 60°C
    if temperatura != 60:
        demanda = demanda * (60 - 15) / (temperatura - 15)
    
    return demanda

# Procesar el cálculo cuando se envía el formulario
if submitted:
    try:
        if tipo_uso == "Residencial":
            demanda = calcular_demanda_acs(
                uso=tipo_uso,
                dormitorios=num_dormitorios,
                edificacion=tipo_edificacion,
                viviendas=num_viviendas if tipo_edificacion == "Colectiva" else None,
                temperatura=temp_servicio
            )
            
            # Mostrar resultados detallados para uso residencial
            st.success(f"**Demanda diaria de ACS: {demanda:.2f} L/día**")
            
            # Explicación del cálculo
            st.subheader("Detalles del cálculo:")
            
            # Mostrar personas según dormitorios
            personas = obtener_personas(num_dormitorios)
            st.write(f"• Vivienda con {num_dormitorios} dormitorios: {personas} personas")
            st.write(f"• Demanda de referencia: 28 L/día por persona a 60°C")
            
            if tipo_edificacion == "Unifamiliar":
                st.write(f"• Cálculo base: {personas} personas × 28 L/día = {personas * 28} L/día")
            else:  # Colectiva
                factor = obtener_factor_centralizacion(num_viviendas)
                st.write(f"• Número de viviendas: {num_viviendas}")
                st.write(f"• Factor de centralización: {factor}")
                st.write(f"• Cálculo base: {personas} personas × 28 L/día × {num_viviendas} viviendas × {factor} = {personas * 28 * num_viviendas * factor} L/día")
            
            # Si hay ajuste de temperatura
            if temp_servicio != 60:
                st.write(f"• Ajuste por temperatura de servicio ({temp_servicio}°C): × {(60 - 15) / (temp_servicio - 15):.4f}")
        
        else:  # Terciario
            demanda = calcular_demanda_acs(
                uso=tipo_uso,
                criterio_terciario=criterio_terciario,
                personas_terciario=num_personas_terciario,
                temperatura=temp_servicio
            )
            
            # Mostrar resultados detallados para uso terciario
            st.success(f"**Demanda diaria de ACS: {demanda:.2f} L/día**")
            
            # Explicación del cálculo
            st.subheader("Detalles del cálculo:")
            
            # Mostrar litros por persona según criterio
            litros_persona = obtener_litros_terciario(criterio_terciario)
            st.write(f"• Criterio de demanda: {criterio_terciario}")
            st.write(f"• Demanda de referencia: {litros_persona} L/día por persona a 60°C")
            st.write(f"• Número de personas: {num_personas_terciario}")
            st.write(f"• Cálculo base: {num_personas_terciario} personas × {litros_persona} L/día = {num_personas_terciario * litros_persona} L/día")
            
            # Si hay ajuste de temperatura
            if temp_servicio != 60:
                st.write(f"• Ajuste por temperatura de servicio ({temp_servicio}°C): × {(60 - 15) / (temp_servicio - 15):.4f}")
    
    except Exception as e:
        st.error(f"Error en el cálculo: {str(e)}")

# Mostrar tablas de referencia
with st.expander("Ver tablas de referencia del CTE-DB-HE4"):
    st.subheader("Tabla A: Ocupación mínima según número de dormitorios")
    st.table(tabla_a)
    
    st.subheader("Tabla B: Factores de centralización según número de viviendas")
    st.table(tabla_b)
    
    st.subheader("Tabla C: Valores para usos terciarios")
    st.table(tabla_c)

# Ejemplos de cálculo
with st.expander("Ver ejemplos de cálculo"):
    st.subheader("Ejemplos:")
    
    # Ejemplo 1: Vivienda con 2 dormitorios
    st.markdown("**Ejemplo 1: Vivienda unifamiliar con 2 dormitorios**")
    st.write("- 2 dormitorios: 3 personas")
    st.write("- Demanda: 3 personas × 28 L/día = 84 L/día")
    
    # Ejemplo 2: Edificio de 10 viviendas con 4 dormitorios
    st.markdown("**Ejemplo 2: Edificio de 10 viviendas con 4 dormitorios cada una**")
    st.write("- 4 dormitorios: 5 personas por vivienda")
    st.write("- Factor de centralización para 10 viviendas: 0.95")
    st.write("- Demanda: 5 personas × 28 L/día × 10 viviendas × 0.95 = 1330 L/día")

# Información adicional
st.markdown("---")
st.markdown("### Notas:")
st.markdown("- La demanda de referencia es de 28 L/día·persona a 60 °C para uso residencial.")
st.markdown("- Si la temperatura de servicio es diferente a 60 °C, se aplica un factor de corrección.")
st.markdown("- Los cálculos se basan en el Código Técnico de la Edificación (CTE-DB-HE4), Anejo F.")
