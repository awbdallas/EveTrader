from wtforms import Form, StringField, validators

class ReportForm(Form):
    reportname = StringField('Name of Report', [validators.Length(min=5, max=30), validators.DataRequired()])
    first_system_id = StringField('First System ID', [validators.Length(min=10, max=10), validators.DataRequired()])
    second_system_id = StringField('Second System ID', [validators.Length(min=10, max=10), validators.DataRequired()])
    items = StringField('Items', [validators.Length(min=10, max=10), validators.DataRequired()])
