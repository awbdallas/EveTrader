from wtforms import Form, StringField, validators


class ReportForm(Form):
    report_name = StringField('Name of Report', [validators.Length(min=5, max=30), validators.DataRequired()])
    first_system_id = StringField('First System ID', [validators.Length(min=8, max=8), validators.DataRequired()])
    second_system_id = StringField('Second System ID', [validators.Length(min=8, max=8), validators.DataRequired()])
    items = StringField('Items', [validators.Length(min=2, max=10), validators.DataRequired()])
