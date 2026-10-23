import math
import unittest
from credito import difuso, evaluar, pertenencias, validar
from motor_original import calcular_cuota, estrategia_evolutiva


def cliente(**cambios):
    return dict(dict(edad=30,ingreso_mensual=4e6,monto_credito=40e6,plazo=3,tasa_anual=18,score=780,endeudamiento=30,antiguedad_empleo_actual=5,reportes_negativos=0),**cambios)


class Motores(unittest.TestCase):
    def test_cuotas(self):
        self.assertEqual(calcular_cuota(1200,1,0),100)
        cuota=calcular_cuota(1200,1,12)
        i=1.12**(1/12)-1
        saldo=1200
        for _ in range(12): saldo=saldo*(1+i)-cuota
        self.assertAlmostEqual(saldo,0,places=8)

    def test_umbral_rigido(self):
        self.assertEqual(evaluar(cliente(score=549))[0],'RECHAZADO')
        self.assertEqual(evaluar(cliente(score=550))[0],'REVISIÓN')
        self.assertEqual(evaluar(cliente(monto_credito=1e6))[0],'APROBADO')
        self.assertEqual(evaluar(cliente(reportes_negativos=2))[0],'RECHAZADO')

    def test_particion_y_cobertura(self):
        for x in range(-50,901):
            valores=pertenencias(x,(500,650,800))
            self.assertAlmostEqual(sum(valores),1)
            self.assertTrue(all(0<=v<=1 for v in valores))
        for score in (300,550,650,750,850):
            for deuda in (0,40,60,100):
                for monto in (1e6,40e6,100e6):
                    f=difuso(cliente(score=score,endeudamiento=deuda,monto_credito=monto))
                    self.assertEqual(len(f['reglas']),27)
                    self.assertAlmostEqual(sum(r['Activación'] for r in f['reglas']),1)
                    self.assertTrue(15-1e-10<=f['indice']<=85+1e-10)

    def test_continuidad_y_monotonia(self):
        izquierda=difuso(cliente(score=749.99))['indice']
        derecha=difuso(cliente(score=750.01))['indice']
        self.assertLess(abs(derecha-izquierda),0.02)
        anterior=0
        for score in range(300,851):
            actual=difuso(cliente(score=score))['indice']
            self.assertGreaterEqual(actual+1e-9,anterior)
            anterior=actual

    def test_controles(self):
        self.assertEqual(difuso(cliente(monto_credito=1e6,score=850,endeudamiento=0))['decision'],'APROBADO')
        self.assertEqual(difuso(cliente(reportes_negativos=2))['decision'],'RECHAZADO')
        self.assertEqual(difuso(cliente(monto_credito=1e6,score=850,endeudamiento=0,reportes_negativos=1))['decision'],'REVISIÓN')
        for campo,valor in [('ingreso_mensual',0),('plazo',0),('plazo',1.01),('score',900),('tasa_anual',-1),('monto_credito',math.inf),('antiguedad_empleo_actual',40)]:
            with self.assertRaises(ValueError): validar(cliente(**{campo:valor}))

    def test_optimizacion(self):
        import random
        random.seed(42)
        c=cliente()
        individuo,fitness,h=estrategia_evolutiva(c)
        self.assertEqual(len(h),50)
        self.assertTrue(all(a<=b for a,b in zip(h,h[1:])))
        self.assertTrue(.7*c['monto_credito']<=individuo[0]<=c['monto_credito'])
        self.assertTrue(c['plazo']<=individuo[1]<=20)
        self.assertEqual(evaluar(dict(c,monto_credito=individuo[0],plazo=individuo[1]))[0],'APROBADO')
