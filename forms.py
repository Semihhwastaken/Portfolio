from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,FileField
from wtforms.validators import DataRequired,URL
from flask_ckeditor import CKEditorField


class ProjectForm(FlaskForm):
  project_name = StringField("Project Name")
  description = StringField("Description")
  project_img = FileField("Project img_url" , validators=[DataRequired()])
  submit = SubmitField("Done")
  
  
class experienceForm(FlaskForm):
  year = StringField("Work Year")
  status = StringField("Job Status")
  place = StringField("Job Place")
  address = StringField("Address")
  description = StringField("Description")
  submit = SubmitField("Submit")
  
class educationForm(FlaskForm):
  year = StringField("Year")
  college = StringField("Place Name")
  address = StringField("Address")
  license = StringField("License")
  job = StringField("Field")
  description = StringField("Description")
  submit = SubmitField("Submit")
  
