import os
import secrets
from PIL import Image
from flask import Flask, render_template, url_for, flash, redirect, request,  abort
from sadm import app, db, bcrypt,  mail
from sadm.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, AddCommentForm,  RequestResetForm, ResetPasswordForm
from sadm.models import User, Post, Comment, followers
from flask_login import login_user, current_user,  logout_user, login_required
from flask_mail import Message
from datetime import datetime




@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts, title='Explorer')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, firstname=form.firstname.data, nai_date=form.nai_date.data, adresse=form.adresse.data, num_pro=form.num_pro.data, email=form.email.data, password=hashed_password, specialite=form.specialite.data)
        db.session.add(user)
        db.session.commit()
        if form.specialite.data == 'value':
          s='neurologie'
        else :
         s='radiologie'  
        flash(f' Dr: {form.name.data} en {s}  votre compte a étais crée avec succés !' , 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='inscrire', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Connexion a échoué . Veuillez vérifier votre email  et le mot de passe', 'danger')
    return render_template('login.html', title='connexion', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics2', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn



@app.route("/upaccount", methods=['GET', 'POST'])
@login_required
def upaccount():
    form=  UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.name = form.name.data
        current_user.firstname = form.firstname.data
        current_user.adresse = form.adresse.data
        current_user.num_pro = form.num_pro.data
        current_user.email = form.email.data
        db.session.commit()
        flash('ton profile a etais mise a jour !', 'success')
        return redirect(url_for('account',name=current_user.name))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.firstname.data = current_user.firstname
        form.adresse.data = current_user.adresse 
        form.num_pro.data = current_user.num_pro 
        form.email.data = current_user.email 
    image_file = url_for('static', filename='profile_pics2/' + current_user.image_file)
    return render_template('upaccount.html', title='Account', image_file=image_file, form=form)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
@app.route("/account/<name>")
@login_required
def account(name):
    user = User.query.filter_by(name=name).first()
    image_file = url_for('static', filename='profile_pics2/' + current_user.image_file)
    return render_template('account.html', title='Profil', image_file=image_file, user=user)

@app.route('/follow/<name>')
@login_required
def follow(name):
    user = User.query.filter_by(name=name).first()
    if user is None:
        flash('Utilisateur {} non trouvé.'.format(name))
        return redirect(url_for('home'))
    if user == current_user:
        flash('!')
        return redirect(url_for('account', name=name))
    current_user.follow(user)
    db.session.commit()
    flash('vous etes abonné a  {}!'.format(name))
    return redirect(url_for('account', name=name))


@app.route('/unfollow/<name>')
@login_required
def unfollow(name):
    user = User.query.filter_by(name=name).first()
    if user is None:
        flash('Utisateur {} non trouvé.'.format(name))
        return redirect(url_for('home'))
    if user == current_user:
        flash('!')
        return redirect(url_for('account', name=name))
    current_user.unfollow(user)
    db.session.commit()
    flash('vous etes désabonné a  {}.'.format(name))
    return redirect(url_for('account', name=name))

def save_picture1(form_picture1):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture1.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/post_pics2', picture_fn)

    output_size = (512, 512)
    i = Image.open(form_picture1)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        if form.picture1.data:
            picture_file = save_picture1(form.picture1.data)
          
        post = Post(title=form.title.data, image_post=picture_file ,content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Votre post a été créé!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='Nouveau Post',
                           form=form, legend='Nouveau Post')
@app.route("/post/<int:post_id>")
def post(post_id):
    form = AddCommentForm()
    if request.method == 'POST': # this only gets executed when the form is submitted and not when the page loads
        if form.validate_on_submit():
            comment = Comment(body=form.body.data, post_id=post.id, author1=current_user)
            db.session.add(comment)
            db.session.commit()
    post = Post.query.get_or_404(post_id)
    coms = Comment.query.all()
    return render_template('post.html', form=form,title=post.title, post=post, coms=coms )

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        if form.picture1.data:
            picture_file = save_picture1(form.picture1.data)
            post.image_post = picture_file
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Votre post a été mis à jour!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    #image_file = url_for('static', filename='post_pics2/' + post.image_post)
    return render_template('create_post.html', title='Modifier Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Votre post a été supprimé!', 'success')
    return redirect(url_for('home'))

@app.route("/post/<int:post_id>/comment", methods=["GET", "POST"])
@login_required
def comment_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = AddCommentForm()
    if request.method == 'POST': # this only gets executed when the form is submitted and not when the page loads
        if form.validate_on_submit():
            comment = Comment(body=form.body.data, post_id=post.id, author1=current_user)
            db.session.add(comment)
            db.session.commit()
            flash("Votre commentaire a été ajouté au poste", "success")
            return redirect(url_for("post", post_id=post.id))
    return render_template("comment_post.html", title="Commenter",form=form, post_id=post_id)

@app.route("/user/<string:name>")
def user_posts(name):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(name=name).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

@app.route('/explore')
@login_required
def explore():
     page = request.args.get('page', 1, type=int)
     posts = current_user.followed_posts().all()
     posts1 = Post.query.order_by(Post.date_posted.desc())
     return render_template("explore.html", title='Accueil', posts=posts, ps=posts1)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Demande de réinitialisation de mot de passe',
                  sender='btd13sadm@gmail.com',
                  recipients=[user.email])
    msg.body = f'''Pour réinitialiser votre mot de passe, visitez le lien suivant:
{url_for('reset_token', token=token, _external=True)}
Si vous n’avez pas fait cette demande, il suffit d’ignorer ce email et aucune modification ne sera apportée.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Un e-mail a été envoyé avec des instructions pour réinitialiser votre mot de passe.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Il s’agit d’un lien invalide ou expiré', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Votre mot de passe a été mis à jour! Vous êtes maintenant en mesure de vous connecter', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route('/search/')
def search():
    todayDate = datetime.today().strftime('%B %Y')
    per_page = 5
    page = request.args.get('page', type=int, default=1)
    offset = (page - 1) * per_page
    keyword = request.args.get('query')
    posts = Post.query.msearch(keyword,fields=['title', 'content']).paginate(page=page, per_page=per_page)
    return render_template("home.html",title='Searching..' + keyword, posts=posts)

