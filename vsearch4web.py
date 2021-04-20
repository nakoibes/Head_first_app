from threading import Thread
import os
from flask import Flask, render_template, request, session, copy_current_request_context
from jinja2 import Template
from dotenv import load_dotenv

from DBcm import UseDatabase, ConnectionError, CredentialsError, SQLError, OperationalError
from checker import check_logged_in
from vsearch import search4letters
app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('secret_key')
app.config['dbconfig'] = {'host': os.getenv('host'),
                          'user': os.getenv('user'),
                          'password': os.getenv('password'),
                          'database': os.getenv('database'), }


@app.route('/login')
def login() -> str:
    session['logged_in'] = True
    return 'You are now logged in'


@app.route('/logout')
def logout() -> str:
    session.pop('logged_in')
    return 'You have logged out'


@app.route('/search4', methods=['POST'])
def do_search() -> Template:
    @copy_current_request_context
    def log_request(req: 'flask_request', res: str) -> None:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = '''insert into log (phrase,letters,ip,browser_string,results) values (%s,%s,%s,%s,%s)'''
            cursor.execute(_SQL, (req.form['phrase'],
                                  req.form['letters'],
                                  req.remote_addr,
                                  req.user_agent.browser,
                                  res,))

    title = 'Here are your results:'
    phrase = request.form['phrase']
    letters = request.form['letters']
    results = str(search4letters(phrase, letters))
    try:
        t = Thread(target=log_request, args=(request, results))
        t.start()
    except Exception as err:
        print('ERROR___ERROR', str(err))
    return render_template('results.html',
                           the_title=title,
                           the_phrase=phrase,
                           the_letters=letters,
                           the_results=results)


@app.route('/')
@app.route('/entry')
def entry_page() -> Template:
    return render_template('entry.html', the_title='Welcome to search4letters on the web!')


@app.route('/viewlog')
@check_logged_in
def view_the_log() -> Template:
    titles = ('Phrase', 'Letters', 'Remote_addr', 'User_agent', 'Results')
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = '''select phrase, letters, ip, browser_string, results from log'''
            cursor.execute(_SQL)
            contents = cursor.fetchall()
        return render_template('viewlog.html',
                               the_title='View log',
                               the_row_titles=titles,
                               the_data=contents)
    except ConnectionError as err:
        print('Is your database switched on? Error:', str(err))
        return render_template('errors.html',
                               the_title='Error',
                               the_error=str(err))
    except CredentialsError as err:
        print('User-id/Password issues. Error:', str(err))
        return render_template('errors.html',
                               the_title='Error',
                               the_error=str(err))
    except SQLError as err:
        print('SQLError', str(err))
        return render_template('errors.html',
                               the_title='Error',
                               the_error=str(err))
    except OperationalError as err:
        print('OperationalError', str(err))
        return render_template('errors.html',
                               the_title='Error',
                               the_error=str(err))
    except Exception as err:
        print('ERROR', str(err))
        return render_template('errors.html',
                               the_title='Error',
                               the_error=str(err))


if __name__ == '__main__':
    app.run(debug=True)
