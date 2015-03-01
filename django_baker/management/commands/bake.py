from __future__ import print_function
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_app, get_models
from django.db.models.loading import get_model
from ...bakery import Baker


class Command(BaseCommand):
    args = "appname:modelname,modelname2,modelname3"
    help = ("Generates generic views (create, update, detail, list, and delete), urls, forms, and admin for model in an"
            "app.  Optionally can restrict which apps are generated on a per app basis.\n\nexample: python manage.py "
            "bake bread:Sesame,Pumpkernickel donut:Glazed,Chocolate")

    def handle(self, *args, **options):
        ingredients = self.parse_bake_options(*args)
        baker = Baker()
        baker.bake(ingredients)

    def parse_bake_options(self, *args):
        """
            Parses command line options to determine what apps and models for those apps we should bake.
        """
        apps_and_models_to_bake = {}
        for arg in args:
            app_and_model_names = arg.split(':')
            app_label = app_and_model_names[0]
            if len(app_and_model_names) == 2:
                selected_model_names = app_and_model_names[1].split(",")
            else:
                selected_model_names = None
            app, models = self.get_app_and_models(app_label, selected_model_names)
            apps_and_models_to_bake[app_label] = models
        return apps_and_models_to_bake

    def get_app_and_models(self, app_label, model_names):
        """
            Gets the app and models when given app_label and model names
        """
        try:
            app = get_app(app_label)
        except ImproperlyConfigured:
            raise CommandError("%s is ImproperlyConfigured - did you remember to add %s to settings.INSTALLED_APPS?" %
                               (app_label, app_label))
        models = self.get_selected_models(app, app_label, model_names)
        return (app, models)

    def get_selected_models(self, app, app_label, model_names):
        """
            Returns the model for a given app.  If given model_names, returns those so long as the model names are
            actually models in the given app.
        """
        if model_names:
            try:
                print(app_label, model_names)
                return [get_model(app_label, model_name) for model_name in model_names]
            except:
                raise CommandError("One or more of the models you entered for %s are incorrect." % app_label)
        else:
            return get_models(app)
