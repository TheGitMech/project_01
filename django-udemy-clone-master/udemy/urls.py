from django.urls import include, path
from .views import *

app_name = 'udemy'

urlpatterns = [
    path('', HomeListView.as_view(), name='home'),
    path('search', SearchView.as_view(), name='search'),
    #path('payments/', include('payments.urls')),



]
