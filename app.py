from flask import Flask,render_template,flash,request,session,redirect,url_for
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from flask_ckeditor import CKEditor
import yaml

app=Flask(__name__)
Bootstrap(app)
CKEditor(app)

db=yaml.load(open('db.yaml'))
app.config['MYSQL_HOST']=db['mysql_host']
app.config['MYSQL_USER']=db['mysql_user']
app.config['MYSQL_PASSWORD']=db['mysql_password']
app.config['MYSQL_DB']=db['mysql_db']
app.config['SECRET_KEY']='Super key'
mysql=MySQL(app)

@app.route('/')
def index():
    cur=mysql.connection.cursor()
    res=cur.execute('select * from blog order by blog_id desc')
    if res>0:
        blogs=cur.fetchall()
        cur.close()
        return render_template('index.html',blogs=blogs)
    cur.close()
    return render_template('index.html')

@app.route('/search',methods=['GET','POST'])
def search():
    if request.method=='POST':
        form=request.form
        search=form['search'].lower()
        cur=mysql.connection.cursor()
        res=cur.execute('select *from blog order by blog_id desc')
        if res>0:
            blogs=cur.fetchall()
            sel=[]
            for b in blogs:
                if search in b[1].lower():
                    sel.append(b)
            cur.close()
            if len(sel)==0:
                flash('notfound')
                return render_template('search.html')
            return render_template('search.html',blogs=sel)
        cur.close()
    return render_template('search.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blogs/<int:id>/',methods=['GET','POST'])
def blog(id):
    cur=mysql.connection.cursor()
    res = cur.execute("select * from blog where blog_id={}".format(id))
    if res>0:
        blog=cur.fetchone()
        cur.close()
        return render_template('blogs.html',blog=blog)
    return render_template('blogs.html',blog_id=id)

@app.route('/register/',methods=['GET','POST'])
def register():
    if request.method=='POST':
        form=request.form
        fname=form['first_name']
        lname=form['last_name']
        uname=form['username']
        email=form['email']
        password=form['password']
        cpassword=form['confirm_password']
        if password!=cpassword:
            flash('passworddoesntmatch')
        else:
            cur=mysql.connection.cursor()
            cur.execute("insert into user(first_name,last_name,username,email,password) values(%s,%s,%s,%s,%s)",(fname,lname,uname,email,password))
            cur.connection.commit()
            cur.close()
            flash('successful')
            return redirect('/login')
    return render_template('register.html')

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method=='POST':
        form=request.form
        uname=form['username']
        password=form['password']
        cur=mysql.connection.cursor()
        res=cur.execute("select *from user where username = %s",([uname]))
        if res>0:
            user=cur.fetchone()
            if user[3]==uname:
                if user[5]==password:
                    session['login']='yes'
                    session['firstname']=user[1]
                    session['lastname']=user[2]
                    flash('loginsuccess')
                    cur.close()
                    return redirect('/')
                else:
                    flash('passwordfail')
                    cur.close()
                    return render_template('login.html')
            else:
                flash('loginfail')
                cur.close()
                return  render_template('login.html')
        else:
            flash('nouser')
            cur.close()
            return  render_template('login.html')

    return render_template('login.html')

@app.route('/write-blog/',methods=['GET','POST'])
def write_blog():
    if request.method == 'POST':
        form=request.form
        title=form['title']
        content=form['editor']
        if session['login']=='yes':
            author=session['firstname']+' '+session['lastname']
            cur = mysql.connection.cursor()
            cur.execute('insert into blog(title,author,body) values(%s,%s,%s)',(title,author,content))
            cur.connection.commit()
            cur.close()
            flash('blogposted')
            return redirect('/')
        else:
            flash('logintopost')
    try:
        if session['login']!='yes':
            flash('logintopost')
            return redirect('/')
    except:
        flash('logintopost')
        return redirect('/')
    return render_template('write-blog.html')

@app.route('/my-blogs/',methods=['GET','POST'])
def my_blog():
    try:
        cur=mysql.connection.cursor()
        name=session['firstname']+' '+session['lastname']
        res=cur.execute('select *from blog where author= "{}" '.format(name))
        if res>0:
            blogs=cur.fetchall()
            cur.close()
            return render_template('my-blogs.html',blogs=blogs)
        cur.close()
        return render_template('my-blogs.html')
    except:
        flash('logintoview')
        return redirect('/')
@app.route('/edit-blog/<int:id>/',methods=['GET','POST'])
def edit_blog(id):
    cur=mysql.connection.cursor()
    res=cur.execute('select *from blog where blog_id = {}'.format(id))
    val=cur.fetchone()
    session['tit']=val[1]
    session['current']=val[3]    
    if request.method=='POST':
        form=request.form
        content=form['editor']
        if res>0:
            cur.execute('update blog set body="{}" where blog_id={}'.format(content,id))    
            mysql.connection.commit()
            cur.close()
        cur.close()
        return redirect('/') 
    cur.close()
    return render_template('edit-blog.html')

@app.route('/delete-blog/<int:id>/',methods=['GET','POST'])
def delete_blog(id):
    cur=mysql.connection.cursor()
    cur.execute(' delete from blog where blog_id = {} '.format(id))    
    mysql.connection.commit()
    cur.close()
    return redirect('/my-blogs')

@app.route('/logout')
def logout():
    session['login']='no'
    session.clear()
    return render_template('logout.html')

if __name__ == '__main__':
    app.run(debug=True)