from wtforms import Form, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired


class AprendizajeBibliaForm(Form):
    tipo_id = SelectField('Tipo de aprendizaje', coerce=int, validators=[DataRequired()])
    libro_id = SelectField('Libro de la Biblia', coerce=int, validators=[DataRequired()])
    capitulo = IntegerField('Capítulo')
    versiculo_inicio = IntegerField('Versículo inicio')
    versiculo_fin = IntegerField('Versículo fin')
    modulo_id = SelectField('Módulo', coerce=int)
    texto = TextAreaField('Texto o reflexión', validators=[DataRequired()])

