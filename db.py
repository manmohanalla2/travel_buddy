''' db for travel buddy'''
import pymysql.cursors
import uuid

class LoginPage(object):

    def open_connection(self):
        '''creating connection'''
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     passwd='MyNewPass',
                                     db='travel_buddy',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        return connection


    def sign_up(self, f_name, l_name, username, email, password, p_number, city):
        '''create user'''
        username_lookup = self.look_up(username=username)
        email_lookup = self.look_up(email=email)

        if username_lookup is not None:
            return 'Sorry username taken'
        elif email_lookup is not None:
            return 'Your email address is already register.'
       # Connect to the database
        connection = self.open_connection()
        with connection.cursor() as cursor:
            # Create a new record
            _id = self.generate_random_id()
            sql = "INSERT INTO `user_login` VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            try:
                cursor.execute(sql, (_id, f_name, l_name, username, email, password, city, p_number))
            except Exception as e:
                connection.close()
                return e
            connection.commit()
            connection.close()
        return True

    def generate_random_id(self):
        '''
        generated random unique ID
        '''
        _id = str(uuid.uuid4())
        return _id

    def look_up(self, username='', email=''):
        '''looking for username'''
        # Connect to the database
        connection = self.open_connection()
        if email:
            check = email
            condition = "email = %s"
        else:
            check = username
            condition = "username = %s"
        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT username, email, password FROM `user_login` WHERE " + condition
            cursor.execute(sql, (check))
            result = cursor.fetchone()
            connection.close()
            return result
        return None

    def sign_in(self, username, password):
        '''validating credentials'''
        db_lookup = self.look_up(username=username)
        if db_lookup is not None:
            if db_lookup['password'] == password:
                return True
            else:
                return 'Please check your username, password'
        else:
            return 'Please check your username, password'

    def get_common_travellers(self, city, username):
        '''
        getting common travellers by running sql query
        '''
        try:
            connection = self.open_connection()
            with connection.cursor() as cursor:
                # Read all record travelling to same city
                condition = "(city = %s) and (username != %s)"
                sql = "SELECT * FROM `user_login` WHERE " + condition
                cursor.execute(sql, (city, username))
                result = cursor.fetchall()
                connection.close()
        except Exception as e:
                connection.close()
        if result:
            self.remove_password(result)
            return result
        return None

    def remove_password(self, data):
        '''
        delete password from data
        '''
        for i in xrange(len(data)):
            del data[i]['password']
            del data[i]['username']
        return data
