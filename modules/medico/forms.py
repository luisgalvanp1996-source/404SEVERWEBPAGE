from wtforms import Form, StringField, DateTimeField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired

class ConsultaMedicaForm(Form):
    fecha = DateTimeField('Fecha', format="%Y-%m-%d %H:%M:%S", validators=[DataRequired()])
    evento_id = SelectField('Evento', coerce=int, validators=[DataRequired()])
    importancia_id = SelectField('Importancia', coerce=int, validators=[DataRequired()])
    unidad_medica_id = SelectField('Clínica / Unidad Médica', coerce=int)
    medico_id = SelectField('Médico', coerce=int)
    observaciones = TextAreaField('Observaciones')
