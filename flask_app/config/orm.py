from flask import flash
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import db

class Schema():
    '''
    A class to that holds methods for basic sql queries.

    Classes that represent tables in your database should
    extend this class.

    Should only ever be extended and not instantiated on its own.
    '''
    @staticmethod
    def format_data(columns):
        """
        Formats given data in a way that is safe to pass into a sql query without risk of sql injection.

        Parameters
        ----------
            columns (list[str]): List of column/variable names.

        Returns
        -------
            Tuple containing a list of escaped column names and a list of formatted variable names.
        """
        cols = [f'`{col}`' for col in columns]
        vals = [f'%({col})s' for col in columns]
        return cols,vals
#-------------------Create---------------------#
    @classmethod
    def create(cls, **data):
        '''
        Creates a new row in the database built from the given data.

        Example usages:
        --------------
            ``User.create(name="John",age=35) -> creates a new user with name "John" and age of 35``

            ``User.create(**request.form) -> creates a new user based on the data recieved from the form``

        Parameters
        ----------
            data (str): Key word arguments for each of the columns and the values to create.

        Returns
        -------
            Id of the newly created row or False if query failed.
        '''
        cols,vals = cls.format_data(data.keys())
        query = f"INSERT INTO `{cls.table}` ({', '.join(cols)}) VALUES ({', '.join(vals)})"
        return connectToMySQL(db).query_db(query,data)
#-------------------Retrieve-------------------#
    @classmethod
    def retrieve_all(cls, **data):
        '''
        Retrieves everything from the database that matches the given data in the form of a list.

        If no parameters are given, everything from that table will be returned.

        Example usages:
        --------------
            ``User.retrieve() -> returns a list of all users``

            ``User.retrieve(id=1) -> returns a single user matching the id``

            ``User.retrieve(name="John") -> returns a list of all users with the name "John"``

        Parameters
        ----------
            data (**str) : Key word arguments for each of the column names and the values to try and match.

        Returns
        -------
            List of class instances created from the matching rows in the database.
        '''
        cols,vals = cls.format_data(data.keys())
        query = f"SELECT * FROM `{cls.table}` {'WHERE'+' AND'.join(f' {col}={val}' for col,val in zip(cols,vals)) if data else ''}"
        return [cls(**item) for item in  connectToMySQL(db).query_db(query,data)]

    @classmethod
    def retrieve_one(cls, **data):
        '''
        Retrieves everything from the database that matches the given data in the form of a list.

        If no parameters are given, everything from that table will be returned.

        Example usages:
        --------------
            ``User.retrieve() -> returns a list of all users``

            ``User.retrieve(id=1) -> returns a single user matching the id``

            ``User.retrieve(name="John") -> returns a list of all users with the name "John"``

        Parameters
        ----------
            data (**str) : Key word arguments for each of the column names and the values to try and match.

        Returns
        -------
            List of class instances created from the matching rows in the database or False if query failed.
        '''
        cols,vals = cls.format_data(data.keys())
        query = f"SELECT * FROM `{cls.table}` {'WHERE'+' AND'.join(f' {col}={val}' for col,val in zip(cols,vals)) if data else ''} LIMIT 1"
        result = connectToMySQL(db).query_db(query,data)
        if result:
            result = cls(**result[0])
        return result
#-------------------Update---------------------#
    @classmethod
    def update(cls,id, **data):
        '''
        Updates the target instance in the database with the given data.

        Example usages:
        --------------
            ``my_user.update(name="Joe",age=24) -> updates my_user to now have the name of "Joe" and age of 24``

            ``my_user.update(**request.form) -> updates my_user based on the data recieved from the form``

        Parameters
        ----------
            data (**str) : Key word arguments for each of the column names and the new values to update with.

        Returns
        -------
            None if successful or False if query failed.
        '''
        cols,vals = cls.format_data(data.keys())
        query = f"UPDATE `{cls.table}` SET {', '.join(f'{col}={val}' for col,val in zip(cols,vals))} WHERE id={id}"
        return connectToMySQL(db).query_db(query,data)
#-------------------Delete---------------------#
    @classmethod
    def delete(cls, **data):
        '''
        Deletes all rows from the database that match the given data.

        Example usages:
        --------------
            ``User.delete(id=1) -> deletes user with the id of 1``

            ``User.delete(name="John") -> deletes all users with the name "John"``

        Parameters
        ----------
            data (**str) : Key word arguments for each of the column names and the values to try and match.

        Returns
        -------
            None if successful or False if query failed.
        '''
        cols,vals = cls.format_data(data.keys())
        query = f"DELETE FROM `{cls.table}` WHERE {' AND '.join(f'{col}={val}' for col,val in zip(cols,vals))}"
        return connectToMySQL(db).query_db(query,data)
#------------------Validate--------------------#
    @classmethod
    def validate(cls, **data):
        '''
        Validates the given data by applying any validators registered to the class via the validator decorator.

        If no validators are registered, then the data will always be considered valid.

        Example usages:
        --------------
            ``User.validate(**request.form) -> validates data from form``

            ``User.validate(name="abc",age="24") -> validates the given attributes``

        Parameters
        ----------
            data (**str) : Key word arguments for each of the field names and the values to be validated.

        Returns
        -------
            Boolean determining whether all of the data is valid or not
        '''
        is_valid = True
        for field,val in data.items():
            for valid,msg,kwargs in cls.validators.get(field,[]):
                kwargs = {k:data.get(v) for k,v in kwargs.items()}
                if not valid(val,**kwargs):
                    flash(msg,f"{cls.__name__}.{field}")
                    is_valid = False
                    break#currently limits to one validation per field at a time but could be changed
        return is_valid

    @classmethod
    def validator(cls,msg,**kwargs):
        '''
        Decorator used to register validators to a given class.

        The method below the decorator should be named the exact same
        as the field you are trying to validate and should return a boolean
        which will be used to determine if the field is valid or not.

        Parameters
        ----------
            msg (str): Error message for the specific validation

            kwargs (**str): Key word arguments for any extra fields that should be passed into the validation function
        '''
        def register(func):
            cls.validators = getattr(cls,"validators",{})
            cls.validators[func.__name__] = cls.validators.get(func.__name__,[])
            cls.validators[func.__name__].append((func,msg,kwargs))
        return register
#----------------------------------------------#
    def __new__(cls,*args,**kwargs):#delete and update implictly pass id when called from instance
        inst = super().__new__(cls)
        inst.delete = lambda : cls.delete(id=inst.id)
        inst.update = lambda **data : cls.update(id=inst.id,**data)
        return inst

    def __repr__(self):#more readable representation
        return f"<{self.table} obj: id={self.id}>"

    def __lt__(self,other):#allows sorting by id
        return self.id < other.id

    def __eq__(self,other):#allows checking equality
        return self.id == other.id

class MtM:
    def __init__(self, left, right, middle):
        '''
        Create an instance of the MtM class.

        Example usages:
        --------
            ``self.favorites = MtM(left = self, right = User, middle = "favorites") -> creates a many-to-many relationship with User called favorites``

        Attributes:
        ----------
            left (Schema): Instance of class representing a given row in a table.
            
            right (Class): Class associated with the table to create the relationship with.
            
            middle (str): Table name of the middle table in the relationship.
        '''
        self.left = left
        self.right = right
        self.middle = middle

    def add(self, *items):#TODO maybe allow for passing in ids instead of class instances
        """
        Creates a new relationship between the given instance and any instances passed in as arguments.

        Example usages:
        -------------
            ``my_user.favorites.add(my_book) -> adds relationship to given book``

            ``my_user.favorites.add(book1,book2,book3) -> adds relationship to all 3 given books``

        Parameters
        ----------
            items (Schema): Items passed as arguments to have a relationship with the given instance.

        Returns
        -------
            Id of the new relationship created in the database if successful or False if query failed.
        """
        query = f"INSERT INTO `{self.middle}` (`{self.left.table}_id`,`{self.right.table}_id`) VALUES {', '.join(f'({self.left.id},{item.id})' for item in items)}"
        return connectToMySQL(db).query_db(query)

    def remove(self, *items):
        """
        Removes relationship from given instance and any instances passed in as arguments.

        Example usages:
        -------------
            ``my_user.favorites.remove(my_book) -> removes relationship to given book``

            ``my_user.favorites.remove(book1,book2,book3) -> removes relationship to all 3 given books``

        Parameters
        ----------
        items (Schema): Items to have relationship with the given instance removed.

        Returns
        -------
            None if successful or False if query failed
        """
        query = f"DELETE FROM `{self.middle}` WHERE {'AND '.join(f'`{self.left.table}_id`={self.left.id} AND `{self.right.table}_id`={item.id} ' for item in items)}"
        return connectToMySQL(db).query_db(query)

    def retrieve(self):
        """
        Retrieves all instances with a relationship to the given instance.

        SELECT \`right_table\`.* FROM \`right_table\` JOIN \`middle_table\` ON \`right_table_id\` = \`right_table\`.id WHERE \`left_table_id\` = %(id)s;

        Does not take any parameters.

        Example usages:
        -------------
            ``User.favorites.retrieve() -> retrieves all instances with a relationship to the user table via the favorites table``

        Returns
        -------
            List of instances with a relationship to the given instance if successful or False if query failed
        """
        query = f"SELECT `{self.right.table}`.* FROM `{self.right.table}` JOIN `{self.middle}` ON `{self.right.table}_id` = `{self.right.table}`.id WHERE `{self.left.table}_id`={self.left.id}"
        results = connectToMySQL(db).query_db(query)
        if results:
            return [self.right(**item) for item in results]
        return results
    
    def __repr__(self):#more readable representation
        return f"<MtM obj: table={self.middle}>"

def table(table):
    '''
    If used without passing any parameters, it will choose a table name based off of the decorated class name (lower-case pluralized)

    Can optionally pass a table name as string which will be used instead

    Example usages
    --------------
        \n::
        
        @table #users
        class User(Schema):
            pass

        @table('people') #people
        class Person(Schema):
            pass

    '''
    if type(table) is str:
        def inner(cls):
            setattr(cls,"table",table)
            return cls
        return inner
    setattr(table,"table",table.__name__.lower()+"s")
    return table