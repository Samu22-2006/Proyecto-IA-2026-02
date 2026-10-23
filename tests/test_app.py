from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_navegacion_y_solicitud():
    app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py')).run()
    assert not app.exception
    for pagina in ['Base de conocimiento','Lógica difusa','Documentos','Apoyo de IA','Evaluar solicitud']:
        app.sidebar.radio[0].set_value(pagina).run()
        assert not app.exception, pagina
    app.button[0].click().run()
    assert not app.exception
    assert len(app.metric)==3
    assert 'analisis' in app.session_state
    # Navegar y regresar conserva el expediente, sin perder resultados.
    app.sidebar.radio[0].set_value('Proyecto').run()
    app.sidebar.radio[0].set_value('Evaluar solicitud').run()
    assert len(app.metric)==3
    app.number_input[1].set_value(1.).run()
    app.button[0].click().run()
    assert not app.exception
