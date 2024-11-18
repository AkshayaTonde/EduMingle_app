from django.contrib import admin
from django.apps import apps

# Specify the app name explicitly to get all models in the app
app = apps.get_app_config('users')  # Replace 'chat_app_django' with your app's name

for model_name, model in app.models.items():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass  # Skip if the model is already registered
