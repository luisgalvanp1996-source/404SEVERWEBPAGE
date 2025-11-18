from wtforms import Form, StringField, DecimalField, DateTimeField, IntegerField, TextAreaField
from wtforms.validators import DataRequired

class MovimientoForm(Form):
    fecha = DateTimeField('Fecha', format="%Y-%m-%d %H:%M:%S")
    tipo = StringField('Tipo', validators=[DataRequired()])
    categoria_id = IntegerField('Categoria')
    monto = DecimalField('Monto', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción')
    metodo_id = IntegerField('Método')
