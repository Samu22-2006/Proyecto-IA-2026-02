"""Funciones conservadas del notebook Sprint 3; sin ejecución interactiva."""
import random

def evaluar_score(score):
    if score >= 750:
        return 'BUENO'
    elif score >= 550:
        return 'REGULAR'
    else:
        return 'MALO'

def evaluar_endeudamiento(endeudamiento):
    if endeudamiento <= 40:
        return 'BAJO'
    elif endeudamiento <= 60:
        return 'MEDIO'
    else:
        return 'ALTO'

def evaluar_estabilidad_actual(antiguedad_actual, edad):
    if 17 <= edad <= 20:
        if antiguedad_actual >= 1:
            return 'ESTABLE'
        else:
            return 'N/A'
    elif 21 <= edad <= 24:
        if antiguedad_actual >= 1:
            return 'ESTABLE'
        else:
            return 'MEDIA'
    elif 25 <= edad <= 35:
        if antiguedad_actual >= 4:
            return 'ESTABLE'
        elif antiguedad_actual >= 2:
            return 'MEDIA'
        else:
            return 'BAJA'
    elif 36 <= edad <= 50:
        if antiguedad_actual >= 6:
            return 'ESTABLE'
        elif antiguedad_actual >= 4:
            return 'MEDIA'
        else:
            return 'BAJA'
    elif 51 <= edad <= 65:
        if antiguedad_actual >= 8:
            return 'ESTABLE'
        elif antiguedad_actual >= 6:
            return 'MEDIA'
        else:
            return 'BAJA'
    else:
        return 'N/A'

def convertir_tasa_mensual(tasa_anual):
    tasa_decimal = tasa_anual / 100
    tasa_mensual = (1 + tasa_decimal) ** (1 / 12) - 1
    return tasa_mensual

def calcular_cuota(monto_credito, plazo, tasa_anual):
    tasa_mensual = convertir_tasa_mensual(tasa_anual)
    meses = round(plazo * 12)
    if meses <= 0:
        raise ValueError('El plazo debe ser positivo.')
    if tasa_mensual == 0:
        return monto_credito / meses
    return monto_credito * tasa_mensual / (1 - (1 + tasa_mensual) ** (-meses))

def evaluar_capacidad_pago(cuota, ingreso_mensual):
    relacion = cuota / ingreso_mensual
    if 0 <= relacion <= 0.2:
        return 'BUENA'
    elif 0.2 < relacion <= 0.3:
        return 'MEDIA'
    elif 0.3 < relacion <= 0.4:
        return 'REVISAR'
    else:
        return 'BAJA'

def motor_inferencia(cliente):
    perfil_score = evaluar_score(cliente['score'])
    nivel_deuda = evaluar_endeudamiento(cliente['endeudamiento'])
    estabilidad_actual = evaluar_estabilidad_actual(cliente['antiguedad_empleo_actual'], cliente['edad'])
    cuota = calcular_cuota(cliente['monto_credito'], cliente['plazo'], cliente['tasa_anual'])
    capacidad_pago = evaluar_capacidad_pago(cuota, cliente['ingreso_mensual'])
    if capacidad_pago == 'BAJA':
        return ('RECHAZADO', 'El cliente no tiene suficiente capacidad de pago.')
    if cliente['reportes_negativos'] >= 2:
        return ('RECHAZADO', 'El cliente tiene dos o más reportes negativos.')
    if perfil_score == 'MALO':
        return ('RECHAZADO', 'El score crediticio es demasiado bajo.')
    if nivel_deuda == 'ALTO':
        return ('RECHAZADO', 'El nivel de endeudamiento es demasiado alto.')
    if perfil_score == 'BUENO' and nivel_deuda == 'BAJO' and (estabilidad_actual == 'ESTABLE' or estabilidad_actual == 'N/A') and (capacidad_pago == 'BUENA' or (capacidad_pago == 'MEDIA' and nivel_deuda == 'BAJO')) and (cliente['reportes_negativos'] == 0):
        return ('APROBADO', 'El cliente presenta un buen perfil financiero.')
    if perfil_score == 'REGULAR' or capacidad_pago == 'REVISAR' or nivel_deuda == 'MEDIO' or (estabilidad_actual == 'MEDIA') or (cliente['reportes_negativos'] == 1):
        return ('REVISIÓN', 'El cliente presenta condiciones intermedias y necesita una evaluación adicional.')
    return ('REVISIÓN', 'La solicitud necesita ser revisada con mayor detalle.')

def crear_individuo(cliente):
    monto_original = cliente['monto_credito']
    meses_original = round(cliente['plazo'] * 12)
    monto = random.uniform(monto_original * 0.7, monto_original)
    meses = random.randint(meses_original, 240)
    return [monto, meses / 12]

def crear_poblacion(cliente, tamaño=20):
    poblacion = []
    for i in range(tamaño):
        individuo = crear_individuo(cliente)
        poblacion.append(individuo)
    return poblacion

def calcular_fitness(individuo, cliente):
    monto, plazo = individuo
    monto_original = cliente['monto_credito']
    plazo_original = cliente['plazo']
    cuota = calcular_cuota(monto, plazo, cliente['tasa_anual'])
    capacidad = max(0, min(1, 1 - cuota / cliente['ingreso_mensual']))
    cercania_monto = max(0, min(1, monto / monto_original))
    if plazo_original == 20:
        cercania_plazo = 1
    else:
        cercania_plazo = max(0, min(1, 1 - (plazo - plazo_original) / (20 - plazo_original)))
    oferta = cliente.copy()
    oferta['monto_credito'] = monto
    oferta['plazo'] = plazo
    decision, _ = motor_inferencia(oferta)
    penalizacion = 0 if decision == 'APROBADO' else 1
    return 0.5 * capacidad + 0.25 * cercania_monto + 0.25 * cercania_plazo - penalizacion

def calcular_intereses_totales(monto, plazo, tasa_anual):
    cuota = calcular_cuota(monto, plazo, tasa_anual)
    meses = plazo * 12
    intereses = cuota * meses - monto
    return intereses

def utilidad_cliente(monto, plazo, cliente):
    monto_original = cliente['monto_credito']
    plazo_original = cliente['plazo']
    tasa_anual = cliente['tasa_anual']
    cercania_monto = monto / monto_original
    if plazo_original == 20:
        cercania_plazo = 1
    else:
        cercania_plazo = 1 - (plazo - plazo_original) / (20 - plazo_original)
    intereses = calcular_intereses_totales(monto, plazo, tasa_anual)
    intereses_referencia = calcular_intereses_totales(monto_original, 20, tasa_anual)
    if intereses_referencia == 0:
        conveniencia_intereses = 1
    else:
        conveniencia_intereses = 1 - intereses / intereses_referencia
    conveniencia_intereses = max(0, min(1, conveniencia_intereses))
    utilidad = 0.4 * cercania_monto + 0.3 * cercania_plazo + 0.3 * conveniencia_intereses
    return utilidad

def utilidad_prestamista(monto, plazo, cliente):
    tasa_anual = cliente['tasa_anual']
    ingreso = cliente['ingreso_mensual']
    monto_original = cliente['monto_credito']
    cuota = calcular_cuota(monto, plazo, tasa_anual)
    relacion = cuota / ingreso
    capacidad = 1 - relacion
    capacidad = max(0, min(1, capacidad))
    intereses = calcular_intereses_totales(monto, plazo, tasa_anual)
    intereses_referencia = calcular_intereses_totales(monto_original, 20, tasa_anual)
    if intereses_referencia == 0:
        ingresos_intereses = 0
    else:
        ingresos_intereses = intereses / intereses_referencia
    ingresos_intereses = max(0, min(1, ingresos_intereses))
    utilidad = 0.6 * capacidad + 0.4 * ingresos_intereses
    return utilidad

def mutar(individuo, cliente):
    hijo = individuo.copy()
    hijo[0] += random.uniform(-0.05, 0.05) * cliente['monto_credito']
    meses = round(hijo[1] * 12) + random.randint(-6, 6)
    hijo[1] = meses / 12
    return hijo

def reparar(individuo, cliente):
    monto_original = cliente['monto_credito']
    individuo[0] = max(monto_original * 0.7, min(monto_original, individuo[0]))
    meses_original = round(cliente['plazo'] * 12)
    meses = max(meses_original, min(240, round(individuo[1] * 12)))
    individuo[1] = meses / 12
    return individuo

def estrategia_evolutiva(cliente, mu=6, lambda_=12, generaciones=50):
    historial_fitness = []
    poblacion = crear_poblacion(cliente, tamaño=mu)
    for generacion in range(generaciones):
        poblacion.sort(key=lambda individuo: calcular_fitness(individuo, cliente), reverse=True)
        padres = poblacion[:mu]
        descendientes = []
        for i in range(lambda_):
            padre = random.choice(padres)
            hijo = mutar(padre, cliente)
            hijo = reparar(hijo, cliente)
            descendientes.append(hijo)
        candidatos = padres + descendientes
        candidatos.sort(key=lambda individuo: calcular_fitness(individuo, cliente), reverse=True)
        poblacion = candidatos[:mu]
        mejor_fitness_generacion = calcular_fitness(poblacion[0], cliente)
        historial_fitness.append(mejor_fitness_generacion)
    mejor_individuo = poblacion[0]
    mejor_fitness = calcular_fitness(mejor_individuo, cliente)
    return (mejor_individuo, mejor_fitness, historial_fitness)
