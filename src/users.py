import os


class Users(object):
    def __init__(self, users_path):
        self.user_id_counter = 0
        self.users_path = users_path
        self.accounts = {}
    
    def add_user(self):
        user = User(self._generate_user_id())
        user.account_folder = self._create_account_folder(user.account_folder)
        user.db_file = self._create_db_file(account_path, user.db_file)
        self.accounts[user.id] = user
    
    def delete_user(self, user_id):
        user = self.get_user(user_id)
        import shutil
        shutil.rmtree(user.account_folder)
        del self.accounts[user_id]
    
    def get_user(self, user_id):
        return self.accounts[user_id]
    
    def clear_all_users(self):
        for user_id in self.accounts:
            self.delete_user(user_id)

    def _create_db_file(self, account_path, db_file_name):
        db_file = os.path.join(account_path, db_file_name)
        with open(db_file, "w"): pass
        return db_file
    
    def _create_account_folder(self, account_folder):
        folder_path = os.path.join(user_path, account_folder)
        os.makedirs(folder_path)
        return folder_path
    
    def _generate_user_id(self):
        self.user_id_counter += 1
        return self.user_id_counter


class User(object):
    def __init__(self, user_id):
        self.id = user_id
        self.account_folder = str(user_id)
        self.db_file = "database.db"

