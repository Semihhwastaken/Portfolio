from flask import Flask,render_template,url_for,redirect,request,flash,session
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase,Mapped, mapped_column
from sqlalchemy import Integer,String,Text
from flask_ckeditor import CKEditor
from forms import ProjectForm,experienceForm,educationForm
from werkzeug.utils import secure_filename
import os
import smtplib
from email.message import EmailMessage
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from functools import wraps
from flask_login import current_user


UPLOAD_FOLDER = 'static/assets/'


app = Flask(__name__)
app.config['SECRET_KEY'] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Bootstrap5(app)
CKEditor(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

class Base(DeclarativeBase):
  pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Projects(db.Model):
  __tablename__ = "projects"
  id: Mapped[int] = mapped_column(Integer,primary_key=True)
  title: Mapped[str] = mapped_column(String)
  description: Mapped[str] = mapped_column(String)
  img_url: Mapped[str] = mapped_column(String)

class experienceSection(db.Model):
  id: Mapped[int] = mapped_column(Integer,primary_key=True)
  year: Mapped[str] = mapped_column(String)
  status: Mapped[str] = mapped_column(String)
  job_place: Mapped[str] = mapped_column(String)
  address: Mapped[str] = mapped_column(String)
  description: Mapped[str] = mapped_column(String)
  
class educationSection(db.Model):
  id: Mapped[int] = mapped_column(Integer,primary_key=True)
  year: Mapped[str] = mapped_column(String)
  college: Mapped[str] = mapped_column(String)
  license: Mapped[str] = mapped_column(String)
  address: Mapped[str] = mapped_column(String)
  job: Mapped[str] = mapped_column(String)
  description: Mapped[str] = mapped_column(String)

with app.app_context():
  db.create_all()
  
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)
  
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("You do not have permission to access this page", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function  

@app.route("/login", methods=["GET", "POST"])
def login():
    # Check credentials (this is just an example, you should implement proper authentication)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        # Example authentication logic, replace with your actual logic
        if username == "admin" and password == "adminpassword":
            user = User(user_id=1)  # Assuming user ID 1 is the admin
            login_user(user)
            session['user_id'] = 1
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "error")
    return render_template("adminlogin.html")
  
@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("home"))

@app.route("/")
def home():
  return render_template("index.html")


  
@admin_required
@login_required
@app.route("/add_project",methods=["GET","POST"])
def add_project():
  form = ProjectForm()
  if form.validate_on_submit():
    f = form.project_img.data
    filename = secure_filename(f.filename)
    print(filename)
    full_path = os.path.join(app.config['UPLOAD_FOLDER'],filename)
    f.save(full_path)
    new_project = Projects(
      title = form.project_name.data,
      description = form.description.data,
      img_url = full_path
    )
    db.session.add(new_project)
    db.session.commit()
    return redirect(url_for('projects'))
  return render_template("make_project.html",form=form)

@admin_required
@app.route("/delete<int:project_id>")
def delete_project(project_id):
  project_to_delete = db.get_or_404(Projects,project_id)
  db.session.delete(project_to_delete)
  db.session.commit()
  return redirect(url_for('projects'))

@app.route("/resume")
def resume():
  results = db.session.execute(db.Select(experienceSection))
  experiences = results.scalars().all()
  results2 = db.session.execute(db.Select(educationSection))
  educations = results2.scalars().all()
  return render_template("resume.html",experiences=experiences,educations=educations,current_user=session)


@app.route("/projects",methods=["GET","POST"])
def projects():
  result = db.session.execute(db.select(Projects))
  projects = result.scalars().all()
  return render_template("projects.html",projects = projects,current_user=session)

@admin_required
@app.route("/add_experience",methods=["GET","POST"])
def add_experience():
  form = experienceForm()
  print(form.validate_on_submit())
  if form.validate_on_submit():
    new_experience = experienceSection(
      year = form.year.data,
      status = form.status.data,
      job_place = form.place.data,
      address = form.address.data,
      description = form.description.data
    )
    db.session.add(new_experience)
    db.session.commit()
    return redirect(url_for('resume'))
  return render_template("experience.html",form=form,current_user=current_user)

@admin_required
@app.route('/delete_exp/<int:experience_id>')
def delete_experience(experience_id):
  experience_to_delete = db.get_or_404(experienceSection,experience_id)
  db.session.delete(experience_to_delete)
  db.session.commit()
  return redirect(url_for("resume"),current_user=current_user)

@admin_required
@app.route("/add_education",methods=["GET","POST"])
def add_education():
  form = educationForm()
  if form.validate_on_submit():
    new_education = educationSection(
      year = form.year.data,
      college = form.college.data,
      address = form.address.data,
      license = form.license.data,
      job = form.job.data,
      description = form.description.data
    )
    db.session.add(new_education)
    db.session.commit()
    return redirect(url_for('resume'))
  return render_template("experience.html",form=form,current_user=current_user)

@admin_required
@app.route("/delete_edu/<int:educ_id>")
def delete_education(educ_id):
  educ_to_delete = db.get_or_404(educationSection,educ_id)
  db.session.delete(educ_to_delete)
  db.session.commit()
  return redirect(url_for('resume'),current_user=current_user)

@app.route("/contact",methods=["GET","POST"])
def contact():
  if request.method == "POST":
    email = request.form['email']
    name = request.form['name']
    phone = request.form['phone']
    msg_content = request.form['message']
    msg = EmailMessage()
    msg.set_content(f"Name: {name}\nE-mail: {email}\nPhone: {phone}\nMessage: {msg_content}")

    msg['Subject'] = 'Subject of your email' 
    msg['From'] = 'semihglssn@gmail.com' 
    msg['To'] = 'semihglssn@gmail.com'  

    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login("semihglssn@gmail.com", "xwkapyhvgydplrtk")
        connection.send_message(msg)
    return render_template("contact.html",msg_sent=True)
  return render_template("contact.html",msg_sent=False)


if __name__ == "__main__":
  app.run(debug=True)