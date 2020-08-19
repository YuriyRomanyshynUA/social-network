import json
from uuid import uuid4
from random import choice
from random import randrange
from client import SocialNetwork


def generate_password(required_chars_list=None):
    required_chars_list = required_chars_list or "@#$%^*!~"
    password = uuid4().hex
    password_len = len(password)
    while True:
        random_index = choice(list(range(0, password_len)))
        if password[random_index].isdigit(): continue
        password = password[random_index].upper() + password
        break
    password = password + choice(required_chars_list)
    return password


class DataGenerator:
    
    def __init__(self, config, ignore_exception=True):
        self.ignore_exception = ignore_exception
        self.config = config
        self.users = []
        self.posts = []
        
        with open(config["input_file"], "r") as f:
            data = json.load(f)
            self.names_registry = data["people_names"]
            self.cities_registry = data["cities"]
        
    def generate_users(self):
        print("===Generating users==")
        for i in range(self.config["users_count"]):
            name = choice(self.names_registry).replace(" ", "")
            usr = {
                "email": f"{name}.index{i}@fmail.com",
                "password": generate_password(),
                "first_name": name,
                "last_name": choice(self.names_registry),
                "city": choice(self.cities_registry)[0],
                "country": choice(self.cities_registry)[1],
                "sex": choice(["MALE", "FEMALE"])
            }
            try:
                client = SocialNetwork.signup(usr)
                self.users.append({"user_data": usr, "client": client})
                print(f"User {usr['email']} created")
            except Exception as error:
                if not self.ignore_exception:
                    raise error from None
                print(f"Exception occurred: {str(error)}")
    
    def generate_posts(self):
        print("===Generating posts==")
        for usr in self.users:
            client = usr["client"]
            user_data = usr["user_data"]
            posts_count = randrange(self.config["max_posts_per_user"])
            print(f"Generating {posts_count} posts for user {user_data['email']}")
            for i in range(posts_count):
                try:
                    res = client.create_post(
                        title=f"USER {user_data['email']} POST NUMBER {i}",
                        content=f"USER {user_data['email']} POST CONTENT"
                    )
                    self.posts.append(res["value"])
                except Exception as error:
                    if not self.ignore_exception:
                        raise error from None
                    print(f"Exception occurred: {str(error)}")

    def generate_likes(self):
        print("===Generating likes==")
        for usr in self.users:
            client = usr["client"]
            user_data = usr["user_data"]
            likes_count = randrange(self.config["max_likes_per_user"])
            print(f"Generating {likes_count} likes by user {user_data['email']}")
            for i in range(likes_count):
                post_id = choice(self.posts)
                try:
                    client.like_post(post_id)
                except Exception as error:
                    if not self.ignore_exception:
                        raise error from None
                    print(f"Exception occurred: {str(error)}")
    
    def save_output(self):
        if self.config["output_file"]:
            users = [r["user_data"]for r in self.users]
            with open(self.config["output_file"], "w") as f:
                json.dump(users, f, indent=3)

    def run(self):
        self.generate_users()
        self.generate_posts()
        self.generate_likes()
        self.save_output()
    
