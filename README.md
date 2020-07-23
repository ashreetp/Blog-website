# Blog-website
I have created a personal blogging website using flask.

#Dependencies to install
1. flask
2. flask_mysqldb
3. yaml

#Designing Database
  
   ->create a database blog_db using mysql
   
   ->create two tables:
   
      ->user with (user_id AUTOINCREMENT,firstname,lastname,userid,email,password)
      
      ->blog with (blog_id AUTOINCREMENT,title,author,body)
      
#How it works 

User can register and login only then he can post a blog.he can edit or delete the blog .In the home page all blogs will be listed,we can also search for a particular blog
