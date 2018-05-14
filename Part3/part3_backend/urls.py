from django.conf.urls import url
from . import views

urlpatterns = [
    url('^$', views.index, name='index'),
    url('^job/.+', views.job, name='add_new_project'),
    url('^query/.+', views.query, name='add_new_project')
]
