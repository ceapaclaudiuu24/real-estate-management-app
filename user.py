class User:
    def __init__(self, user_id, first_name, last_name, password, role, email, phone):
        self.user_id = user_id
        self.role = role
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.password = password
