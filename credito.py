"""Modelo difuso académico, independiente del motor histórico."""
import math
from itertools import product
from motor_original import calcular_cuota, motor_inferencia


def validar(c):
    campos = ['edad', 'ingreso_mensual', 'monto_credito', 'plazo', 'tasa_anual', 'score', 'endeudamiento', 'antiguedad_empleo_actual', 'reportes_negativos']
    if any(not math.isfinite(c[k]) for k in campos):
        raise ValueError('Los datos deben ser finitos.')
    if c['ingreso_mensual'] <= 0 or c['monto_credito'] <= 0:
        raise ValueError('Ingreso y monto deben ser positivos.')
    if not 0 < c['plazo'] <= 20 or not math.isclose(c['plazo']*12, round(c['plazo']*12)):
        raise ValueError('Usa entre 1 y 240 meses completos.')
    if not 17 <= c['edad'] <= 100 or int(c['edad']) != c['edad']:
        raise ValueError('La edad debe ser un entero entre 17 y 100.')
    if not 300 <= c['score'] <= 850 or not 0 <= c['endeudamiento'] <= 100:
        raise ValueError('Score: 300–850; endeudamiento: 0–100 %.')
    if c['tasa_anual'] < 0 or not 0 <= c['antiguedad_empleo_actual'] <= c['edad']-16 or c['reportes_negativos'] < 0 or int(c['reportes_negativos']) != c['reportes_negativos']:
        raise ValueError('Revisa tasa, antigüedad y reportes; el empleo se cuenta desde los 16 años.')


def pertenencias(x, centros):
    """Partición lineal con hombros: suma de pertenencias igual a uno."""
    a,b,c = centros
    if x <= a: return [1.,0.,0.]
    if x < b: return [(b-x)/(b-a),(x-a)/(b-a),0.]
    if x < c: return [0.,(c-x)/(c-b),(x-b)/(c-b)]
    return [0.,0.,1.]


def difuso(c):
    validar(c)
    cuota = calcular_cuota(c['monto_credito'], c['plazo'], c['tasa_anual'])
    entradas = {'Score': pertenencias(c['score'], (500,650,800)),
                'Endeudamiento': pertenencias(c['endeudamiento'], (30,50,70)),
                'Cuota / ingreso': pertenencias(100*cuota/c['ingreso_mensual'], (15,30,45))}
    reglas=[]
    for s,d,p in product(range(3),repeat=3):
        peso=entradas['Score'][s]*entradas['Endeudamiento'][d]*entradas['Cuota / ingreso'][p]
        # Cualquier condición desfavorable domina; sólo tres favorables aprueban.
        salida=15 if s==0 or d==2 or p==2 else (85 if s==2 and d==0 and p==0 else 50)
        reglas.append({'Regla':f"Score {['bajo','medio','alto'][s]} · deuda {['baja','media','alta'][d]} · carga {['baja','media','alta'][p]}", 'Activación':peso,'Consecuente':salida})
    indice=sum(r['Activación']*r['Consecuente'] for r in reglas)/sum(r['Activación'] for r in reglas)
    recomendacion='APROBADO' if indice>=70 else ('RECHAZADO' if indice<35 else 'REVISIÓN')
    motivo='Recomendación difusa; sujeta a revisión humana.'
    if c['reportes_negativos']>=2:
        recomendacion='RECHAZADO'; motivo='Restricción explícita: dos o más reportes negativos.'
    elif c['reportes_negativos']==1 or c['edad']<18 or c['edad']>65 or c['antiguedad_empleo_actual']<1:
        if recomendacion=='APROBADO': recomendacion='REVISIÓN'
        motivo='Revisión requerida por reporte, edad fuera del rango 18–65 o antigüedad inferior a un año.'
    return {'indice':indice,'decision':recomendacion,'motivo':motivo,'entradas':entradas,'reglas':reglas}


def evaluar(c, sin_intereses=False):
    validar(c)
    return motor_inferencia(dict(c,tasa_anual=0) if sin_intereses else c)
