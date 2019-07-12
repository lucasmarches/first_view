from django.urls import path
from . import views

urlpatterns = [
    path('', views.links_all, name='results_page_first'),
    path('public_jobs/', views.PublicJobsView.as_view(), name='public_jobs'),
    path('cade_cases/', views.CadeCasesView.as_view(), name='cade_cases')
]
