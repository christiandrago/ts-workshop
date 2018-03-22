from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^render_checkout$', views.render_checkout, name='render_checkout'),
    url(r'^push$', views.handle_push_notification, name='push'),
    url(r'^validate$', views.validate_order, name='validate')
]