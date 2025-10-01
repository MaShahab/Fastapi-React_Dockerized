from locust import HttpUser, task, between

class QuickstartUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        response = self.client.post("/login", json={
            "username": "admin",
            "password": "admin",
        })
        access_token = response.json()["access_token"]
        self.client.headers = {'Authorization': f'Bearer {access_token}'}

    # @task
    # def login(self):
    #     self.client.post("/login", json={
    #         "username": "admin",
    #         "password": "admin",
    #     })

    @task
    def private(self):
        self.client.get("/private")

    @task
    def hello_world(self):
        self.client.get("/hello")

    @task
    def not_found(self):
        self.client.get("/sdjflj")
