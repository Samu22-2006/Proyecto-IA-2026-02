from pathlib import Path
import json
import random
import streamlit as st
from credito import evaluar, difuso, pertenencias
from motor_original import (calcular_cuota, estrategia_evolutiva, utilidad_cliente,
                            utilidad_prestamista)

st.set_page_config(page_title='Crédito · Sistema experto', page_icon='◈', layout='wide')
st.markdown('''<style>.block-container{max-width:1120px;padding-top:2.5rem}h1{letter-spacing:-.04em}div[data-testid="stMetric"]{background:#F3F6F7;padding:18px;border-radius:10px}</style>''',unsafe_allow_html=True)
st.sidebar.title('Crédito / IA')
st.sidebar.caption('Proyecto académico · 2026')
pagina=st.sidebar.radio('Explorar', ['Proyecto','Evaluar solicitud','Base de conocimiento','Lógica difusa','Documentos','Apoyo de IA'])
st.sidebar.divider()
st.sidebar.caption('Simulador educativo. No concede créditos ni estima probabilidades de incumplimiento. Usa datos ficticios; no se guardan solicitudes en archivos.')

if pagina=='Proyecto':
    st.caption('SISTEMA EXPERTO DE CRÉDITO')
    st.title('De reglas rígidas a decisiones explicables.')
    st.write('Una aplicación que reúne el conocimiento financiero, el motor de inferencia y la búsqueda evolutiva de contraofertas. La extensión difusa permite estudiar qué ocurre cerca de los límites de las reglas.')
    for titulo,texto in [('01 · Conocimiento','Representación del solicitante y reglas sobre score, deuda, capacidad de pago y estabilidad laboral.'),('02 · Inferencia','Evaluación determinista: aprobación, revisión o rechazo, con prioridad para las reglas de rechazo. El modelo inicial calcula cuotas sin intereses.'),('03 · Optimización','Cuota con tasa efectiva anual y estrategia evolutiva (μ+λ) para ajustar monto y plazo cuando la solicitud requiere revisión.')]:
        with st.container(border=True): st.subheader(titulo); st.write(texto)
    st.info('Trazabilidad: los adjuntos identifican explícitamente el Sprint 3. La división de los dos primeros sprints es una organización inferida del sistema experto inicial, pendiente de contrastar con sus entregas originales.')
    st.write('La lógica difusa es una extensión implementada para esta integración. Se conserva el motor original para comparar resultados y evitar confundir una recomendación gradual con una aprobación bancaria.')
    st.caption('Usa «Evaluar solicitud» en el menú para comenzar.')

elif pagina=='Evaluar solicitud':
    st.title('Evaluar solicitud')
    st.write('Un expediente, tres perspectivas. Valores monetarios en COP; cuotas sin seguros, comisiones ni otros cargos.')
    with st.form('solicitud'):
        a,b=st.columns(2)
        with a:
            edad=st.number_input('Edad',17,100,30)
            ingreso=st.number_input('Ingreso mensual · COP',min_value=1.,value=4000000.,step=100000.)
            monto=st.number_input('Monto solicitado · COP',min_value=1.,value=40000000.,step=1000000.)
            meses=st.number_input('Plazo · meses',1,240,36)
            tasa=st.number_input('Tasa efectiva anual · %',0.,200.,18.,step=0.5)
        with b:
            score=st.slider('Score crediticio',300,850,780)
            deuda=st.slider('Endeudamiento actual · %',0.,100.,30.)
            empleo=st.number_input('Antigüedad laboral · años',0.,84.,5.,step=0.5)
            reportes=st.number_input('Reportes negativos',0,50,0)
            semilla=st.number_input('Semilla de optimización reproducible',0,99999,42)
        enviado=st.form_submit_button('Analizar solicitud',type='primary')
    if enviado:
        c=dict(edad=edad,ingreso_mensual=ingreso,monto_credito=monto,plazo=meses/12,tasa_anual=tasa,score=score,endeudamiento=deuda,antiguedad_empleo_actual=empleo,reportes_negativos=reportes)
        try:
            base=evaluar(c,True); actual=evaluar(c); f=difuso(c)
            st.session_state['analisis']=(c,base,actual,f,semilla)
        except ValueError as exc:
            st.session_state.pop('analisis',None); st.error(str(exc))
    if 'analisis' in st.session_state:
        c,base,actual,f,semilla=st.session_state['analisis']
        st.caption('RESULTADOS DEL ÚLTIMO EXPEDIENTE ENVIADO · vuelve a analizar si modificas los datos')
        cuota=calcular_cuota(c['monto_credito'],c['plazo'],c['tasa_anual'])
        a,b,d=st.columns(3)
        a.metric('Cuota mensual',f'$ {cuota:,.0f}'); b.metric('Cuota / ingreso',f"{cuota/c['ingreso_mensual']:.1%}"); d.metric('Índice difuso',f"{f['indice']:.1f} / 100")
        for col,titulo,resultado in zip(st.columns(3),['Inicial · sin intereses','Sprint 3 · con intereses','Extensión · difusa'],[base,actual,(f['decision'],f['motivo'])]):
            with col:
                st.subheader(titulo); st.write('**'+resultado[0]+'**'); st.caption(resultado[1])
        st.caption('El índice difuso expresa conveniencia según reglas académicas; no es un porcentaje de probabilidad ni un score bancario.')
        with st.expander('Ver reglas difusas activadas'):
            st.dataframe([r for r in f['reglas'] if r['Activación']>0],hide_index=True,use_container_width=True)
        st.subheader('Contraoferta evolutiva · Sprint 3')
        if actual[0]=='REVISIÓN':
            estado=random.getstate()
            try:
                random.seed(semilla)
                individuo,fitness,historial=estrategia_evolutiva(c)
            finally: random.setstate(estado)
            oferta=dict(c,monto_credito=individuo[0],plazo=individuo[1])
            decision=evaluar(oferta)
            if decision[0]=='APROBADO': st.success('Se encontró una contraoferta aprobable según el motor original.')
            else: st.warning('La búsqueda no encontró una oferta aprobable. Cambiar monto y plazo no corrige score, deuda, reportes ni estabilidad.')
            st.dataframe([{'Monto COP':round(individuo[0],2),'Meses':round(individuo[1]*12),'Cuota COP':round(calcular_cuota(*individuo,c['tasa_anual']),2),'Decisión':decision[0],'Fitness':fitness,'Utilidad cliente':utilidad_cliente(*individuo,c),'Utilidad prestamista':utilidad_prestamista(*individuo,c)}],hide_index=True)
            st.line_chart({'Mejor fitness':historial},x_label='Generación (índice 0 = primera)',y_label='Fitness')
            st.caption('μ=6 · λ=12 · 50 generaciones. Monto entre 70–100 % del original; plazo entre el solicitado y 240 meses. No garantiza el óptimo global.')
        else: st.info('La estrategia original sólo se ejecuta para solicitudes en REVISIÓN.')
        st.download_button('Descargar análisis · JSON',json.dumps({'expediente':c,'motor_inicial':base,'motor_sprint3':actual,'difuso':f},ensure_ascii=False,indent=2),'analisis-credito.json','application/json')

elif pagina=='Base de conocimiento':
    st.title('Base de conocimiento')
    st.write('Hechos declarados → categorías → reglas priorizadas → decisión explicada. Fuente: notebooks originales incluidos en Documentos.')
    st.table([{'Variable':'Score','Reglas':'<550 malo · 550–749 regular · ≥750 bueno'}, {'Variable':'Endeudamiento','Reglas':'≤40 % bajo · >40–60 % medio · >60 % alto'}, {'Variable':'Cuota / ingreso','Reglas':'≤20 % buena · >20–30 % media · >30–40 % revisar · >40 % baja'}, {'Variable':'Reportes','Reglas':'0 permite aprobar · 1 revisar · ≥2 rechazar'}])
    st.subheader('Estabilidad laboral del modelo original')
    st.table([{'Edad':'17–20','Estable desde':'1 año','Media desde':'N/A si <1'}, {'Edad':'21–24','Estable desde':'1 año','Media desde':'0 años'}, {'Edad':'25–35','Estable desde':'4 años','Media desde':'2 años'}, {'Edad':'36–50','Estable desde':'6 años','Media desde':'4 años'}, {'Edad':'51–65','Estable desde':'8 años','Media desde':'6 años'}])
    st.write('Por debajo del umbral medio: estabilidad baja. Fuera de 17–65: N/A. El motor histórico acepta N/A en la aprobación: se conserva por trazabilidad, aunque requiere revisión antes de cualquier uso real.')
    st.subheader('Prioridad de las decisiones')
    st.markdown('1. **Rechazar:** capacidad baja, ≥2 reportes, score malo o deuda alta, en ese orden.\n2. **Aprobar:** score bueno, deuda baja, estabilidad estable o N/A, capacidad buena o media y cero reportes.\n3. **Revisar:** condiciones intermedias o cualquier caso restante.')
    st.latex(r'i_m=(1+TEA/100)^{1/12}-1,\qquad C=\frac{M i_m}{1-(1+i_m)^{-n}}')
    st.caption('Si la tasa es cero: C=M/n. El modelo inicial usa esta cuota sin intereses. Endeudamiento y cuota/ingreso son entradas separadas, como en los adjuntos; no se suman automáticamente.')
    st.subheader('Objetivo evolutivo conservado')
    st.write('Fitness = 0.50 × capacidad + 0.25 × cercanía del monto + 0.25 × cercanía del plazo − penalización. La penalización es 1 si el motor no aprueba; 0 si aprueba. Las utilidades del cliente y prestamista se reportan como indicadores separados, no se optimizan directamente en este fitness.')

elif pagina=='Lógica difusa':
    st.title('Suavizar los límites, explicar las reglas.')
    st.write('Una deuda de 40 % es baja en el motor rígido; 40.1 % pasa a media. Esa discontinuidad puede cambiar la decisión sin un cambio material del expediente. La lógica difusa permite pertenecer parcialmente a categorías vecinas.')
    st.subheader('Opción elegida: Sugeno de orden cero')
    st.write('Se elige por su trazabilidad y cálculo sencillo: cada regla tiene un consecuente constante; el resultado es su promedio ponderado. Frente a Mamdani, evita discretizar una salida y calcular su centroide. No requiere datos de entrenamiento, que no están presentes en las entregas.')
    st.table([{'Entrada':'Score','Centros bajo / medio / alto':'500 / 650 / 800'}, {'Entrada':'Deuda (%)','Centros bajo / medio / alto':'30 / 50 / 70'}, {'Entrada':'Cuota/ingreso (%)','Centros bajo / medio / alto':'15 / 30 / 45'}])
    st.write('Pertenencias triangulares lineales entre centros y hombros en los extremos. Son parámetros propuestos para el ejercicio, no calibrados con datos. Las tres pertenencias siempre suman 1.')
    variable=st.selectbox('Explorar funciones de pertenencia',['Score','Deuda','Carga'])
    centros={'Score':(500,650,800),'Deuda':(30,50,70),'Carga':(15,30,45)}[variable]
    universo=range(300,851,5) if variable=='Score' else range(101)
    import pandas as pd
    st.line_chart(pd.DataFrame([pertenencias(x,centros) for x in universo],index=list(universo),columns=['Bajo','Medio','Alto']),x_label=variable,y_label='Pertenencia')
    st.subheader('27 reglas, sin zonas sin cobertura')
    st.write('Se combinan las tres etiquetas de cada una de las tres entradas (3³). Si el score es bajo, la deuda alta o la carga alta, el consecuente es 15. Si las tres condiciones son favorables, es 85. En los demás casos, 50. AND usa producto; la salida es Σ(activación × consecuente) / Σ(activación).')
    st.write('Índice <35: rechazo; entre 35 y <70: revisión; ≥70: aprobación orientativa. Estos umbrales finales siguen siendo discretos: se suaviza el índice y la activación de reglas, no se elimina toda decisión categórica.')
    st.info('Modelo híbrido: dos o más reportes mantienen rechazo obligatorio. Un reporte, edad fuera de 18–65 o antigüedad inferior a un año impiden aprobación automática. Edad y antigüedad son controles explícitos, no entradas difusas. Estos controles son una propuesta de integración y difieren del motor histórico.')
    st.write('Limitaciones: faltan calibración, evaluación de sesgo y validación con expertos. El índice no es una probabilidad. Los criterios de edad de los adjuntos deben revisarse antes de cualquier aplicación financiera real.')

elif pagina=='Documentos':
    st.title('Entregas y archivos originales')
    st.write('Los cuatro adjuntos se conservan íntegros y pueden descargarse. Son fuentes del proyecto, no instrucciones de ejecución de esta aplicación.')
    for p in sorted((Path(__file__).parent/'documentos').iterdir()):
        with st.container(border=True):
            st.subheader(p.name)
            st.download_button('Descargar original',p.read_bytes(),p.name,key=p.name)
            if p.suffix=='.ipynb':
                with st.expander('Consultar código del notebook'):
                    n=json.loads(p.read_text())
                    for cell in n['cells']:
                        if cell['cell_type']=='code': st.code(''.join(cell['source']),language='python')
            else: st.caption('Prototipo HTML original. Descárgalo para abrirlo en tu navegador; no se ejecuta dentro de la aplicación.')

else:
    st.title('Apoyo de inteligencia artificial')
    st.subheader('Uso confirmado en esta integración')
    st.write('ChatGPT / Codex apoyó la lectura de los adjuntos, la organización de la aplicación Streamlit, la adaptación del motor existente, la propuesta de lógica difusa, la documentación y la preparación de pruebas. Python y Streamlit son herramientas de desarrollo, no modelos de IA.')
    st.subheader('Uso en los sprints originales')
    st.write('El autor confirmó el uso de ChatGPT durante el desarrollo de los sprints originales. No especificó las tareas concretas en las que lo utilizó; por ello no se atribuyen actividades adicionales sin confirmación.')
    st.caption('El apoyo de IA no sustituye la revisión del autor, la validación de reglas con expertos ni la responsabilidad sobre las conclusiones del proyecto.')
