from flask import flash
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import db

class Schema:
    '''
    A class to that holds methods for basic sql queries.

    Classes that represent tables in your database should
    extend this class.

    Should only ever be extended and not instantiated on its own.
    '''
    @classmethod
    def order_by(cls,col="id",desc=False,rand=False):
        config = {
            "order_by" : col,
            "desc" : desc,
            "rand" : rand
        }
        setattr(cls,"config",config)
        return cls
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
        query = f"INSERT INTO `{cls.table}` ({', '.join(f'`{col}`' for col in data.keys())}) VALUES ({', '.join(f'%({col})s' for col in data.keys())})"
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
        config = getattr(cls,'config',None)
        if config:
            config = f"ORDER BY {'RAND()' if config['rand'] else config['col']} {'DESC' if config['desc'] else 'ASC'}"
            delattr(cls,"config")
        query = f"SELECT * FROM `{cls.table}` {'WHERE'+' AND'.join(f' `{col}`=%({col})s' for col in data.keys()) if data else ''} {config if config else ''}"
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
        config = getattr(cls,'config',None)
        if config:
            config = f"ORDER BY {config['rand'] if config['rand'] else config['col']} {'DESC' if config['desc'] else 'ASC'}"
            delattr(cls,"config")
        query = f"SELECT * FROM `{cls.table}` {'WHERE'+' AND'.join(f' `{col}`=%({col})s' for col in data.keys()) if data else ''} {config if config else ''} LIMIT 1"
        result = connectToMySQL(db).query_db(query,data)
        if result:
            result = cls(**result[0])
        return result
#-------------------Update---------------------#
    @classmethod
    def update(cls,id=None,**data):#TODO allow for filter dict paramater instead of id
        '''
        Updates the target instance in the database with the given data.

        Example usages:
        --------------
            ``User.update(1,name="Joe",age=24) -> updates user with id of 1 to have name of "Joe" and age of "24"

            ``User.update(name="John") -> updates ALL users to have the name "John"

            ``my_user.update(name="Joe",age=24) -> updates my_user to now have the name of "Joe" and age of 24``

            ``my_user.update(**request.form) -> updates my_user based on the data recieved from the form``

        Parameters
        ----------
            id (str) : Id of instance to update (implicit if called on instance)

            data (**str) : Key word arguments for each of the column names and the new values to update with.

        Returns
        -------
            None if successful or False if query failed.
        '''
        query = f"UPDATE `{cls.table}` SET {', '.join(f'`{col}`=%({col})s' for col in data.keys())} {f'WHERE `id`={id}' if id else ''}"
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

            ``my_user.delete() -> deletes user based on instance``

        Parameters
        ----------
            data (**str) : Key word arguments for each of the column names and the values to try and match.

        Returns
        -------
            None if successful or False if query failed.
        '''
        query = f"DELETE FROM `{cls.table}` WHERE {' AND '.join(f'`{col}`=%({col})s' for col in data.keys())}"
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
                    # break#limits to one validation per field at a time
        return is_valid

    @classmethod
    def validator(cls,msg,**kwargs):
        '''
        Decorator used to register validators to a given class.

        The method below the decorator should be named the exact same
        as the field you are trying to validate and should return a boolean
        which will be used to determine if the field is valid or not. Flashed
        message categories will be accessed as "Class.field" format.

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
        Create an instance of the MtM class. Foreign key names should be
        the table name lowercase and pluralized to work correctly (currently)

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

    def remove(self,*items):
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
        query = f"DELETE FROM `{self.middle}` WHERE `{self.left.table}_id`={self.left.id} AND `{self.right.table}_id` IN ({', '.join(str(item.id) for item in items)})"
        return connectToMySQL(db).query_db(query)

    def retrieve(self,**data):
        """
        Retrieves all instances with a relationship to the given instance that match the given data.

        Parameters
        ----------
        data (**str) : Key word arguments for each of the column names and the values to try and match.

        Example usages:
        -------------
            ``user1.replies.retrieve() -> retrieves all the replies associated with a user``

            ``post2.replies.retrieve(users_id=1) -> retrieves all replies on a post that were made by the user with an id of 1

        Returns
        -------
            List of instances with a relationship to the given instance if successful or False if query failed
        """
        query = f"SELECT `{self.right.table}`.* FROM `{self.right.table}` JOIN `{self.middle}` ON `{self.right.table}_id` = `{self.right.table}`.id WHERE `{self.left.table}_id`={self.left.id}"
        if data:
            for col in data.keys():
                query += f" AND `{col}`=%({col})s"
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