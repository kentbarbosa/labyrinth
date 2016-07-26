from flask_wtf import Form
from wtforms.fields import DecimalField
from wtforms.validators import Required

class LightParamsForm(Form):
    cycle_time = DecimalField('cycle_time')
    num_steps = DecimalField('num_steps')
    
