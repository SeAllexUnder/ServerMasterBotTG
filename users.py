import json


class Users:
    roles = [
        'admin',
        'user',
    ]
    exception_id = [6863515192]

    @staticmethod
    def get_users():
        with open("users_telegram.json", "r", encoding='utf-8') as users_json:
            users_ = json.load(users_json)
        return users_

    def get_role(self, user_id):
        users_ = self.get_users()
        try:
            role = users_[str(user_id)]['role']
            return role
        except KeyError:
            return None

    def get_users_list(self):
        i = 1
        users_ = self.get_users()
        user_list = []
        for u in users_:
            user_list.append(f'{i}. {users_[u]["name"]}, ID: {u}, роль: {users_[u]["role"]}')
            i += 1
        users_string = '\n'.join(user_list)
        return users_string

    def check_user_in_list(self, id_):
        users_ = self.get_users()
        users_id_list = [str(u) for u in users_]
        if str(id_) in users_id_list:
            return True
        else:
            return False

    def append_user(self, id_, name, role):
        try:
            int(id_)
        except ValueError:
            return False, f"ID пользователя может содержать только цифры."
        if self.check_user_in_list(id_):
            return False, f"ID {id_} зарегистрирован ранее."
        else:
            users_ = self.get_users()
            user_info = {
                    "name": name,
                    "role": role
            }
            users_[str(id_)] = user_info
            with open("users_telegram.json", "w", encoding='utf-8') as roles_settings:
                roles_settings.write(json.dumps(users_,
                                                ensure_ascii=False,
                                                separators=(',', ':'),
                                                sort_keys=False,
                                                indent=4))
                roles_settings.close()
            return True, f"Пользователь {id_} зарегистрирован."

    def delete_user(self, id_):
        try:
            if int(id_) in self.exception_id:
                return False, "Этого пользователя удалить нельзя!"
        except ValueError:
            return False, f"ID пользователя может содержать только цифры."
        if not self.check_user_in_list(id_):
            return False, f"ID {id_} не зарегистрирован ранее."
        else:
            users_ = self.get_users()
            users_.pop(str(id_))
            with open("users_telegram.json", "w", encoding='utf-8') as roles_settings:
                roles_settings.write(json.dumps(users_,
                                                ensure_ascii=False,
                                                separators=(',', ':'),
                                                sort_keys=False,
                                                indent=4))
                roles_settings.close()
            return True, f"Пользователь с ID {id_} удален."

    def update_role(self, id_, role):
        try:
            if int(id_) in self.exception_id:
                return False, "Этого пользователя редактировать нельзя!"
        except ValueError:
            return False, f"ID пользователя может содержать только цифры."
        if not self.check_user_in_list(id_):
            return False, f"ID {id_} не зарегистрирован ранее."
        else:
            users_ = self.get_users()
            old_role = users_[str(id_)]['role']
            users_[str(id_)]['role'] = role
            with open("users_telegram.json", "w", encoding='utf-8') as roles_settings:
                roles_settings.write(json.dumps(users_,
                                                ensure_ascii=False,
                                                separators=(',', ':'),
                                                sort_keys=False,
                                                indent=4))
                roles_settings.close()
            return True, f"Роль пользователя с ID {id_} изменена с {old_role} на {role}"


if __name__ == "__main__":
    users = Users()
    # print(users.get_role(6863515192))
    # print(users.get_users_list())
    # print(users.check_user_in_list(6863515192))
    # print(users.append_user(123, 'имя', 'admin'))
    # print(users.delete_user(123))
    # print(users.update_role(1562676986, 'admin'))