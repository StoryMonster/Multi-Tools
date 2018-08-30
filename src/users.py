import os


class Users(object):
    def __init__(self, users_data_dir):
        self.user_id_counter = 0
        self.users_data_dir = os.path.abspath(users_data_dir)
        self.accounts = {}
    
    def add_user(self, user_ip):
        user_id = self._generate_user_id()
        user = User(user_id, user_ip)
        user.data_dir = os.path.join(self.users_data_dir, str(user_id))
        self._create_user_data_dir(user.data_dir)
        self.accounts[user_id] = user
    
    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        import shutil
        shutil.rmtree(user.data_dir)
        del self.accounts[user_id]
    
    def get_user_by_id(self, user_id): 
        return self.accounts[user_id] if user_id in self.accounts else None
    
    def get_user_by_ip(self, user_ip):
        for user_id in self.accounts:
            if self.accounts[user_id].ip == user_ip:
                return self.accounts[user_id]
        return None
    
    def clear_all_users(self):
        for user_id in self.accounts:
            self.delete_user(user_id)
    
    def _create_user_data_dir(self, user_data_dir):
        os.makedirs(user_data_dir)
    
    def _generate_user_id(self):
        self.user_id_counter += 1
        return self.user_id_counter


class User(object):
    def __init__(self, user_id, user_ip):
        self.id = user_id
        self.ip = user_ip
        self.data_dir = None
        self.asn1codec = None
        self.asn1codec_data_dir = None
        self.asn1codec_files = {}
    
    def create_asn1codec_data_dir(self):
        self.asn1codec_data_dir = os.path.join(self.data_dir, "asn1codec")
        os.makedirs(self.asn1codec_data_dir)
        self.asn1codec_files['py_file'] = os.path.join(self.asn1codec_data_dir, "target.py")
        self.asn1codec_files['log_file'] = os.path.join(self.asn1codec_data_dir, "run.log")


