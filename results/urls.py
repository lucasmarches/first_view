from django.urls import path
from . import views

urlpatterns = [
    path('', views.analyze, name='results_page_end'),
    path('first', views.links_first, name='results_page_first'),
    path('second', views.links_second, name='results_page_second'),
    path('third', views.links_third, name='results_page_third'),
    path('public_jobs/', views.PublicJobsView.as_view(), name='public_jobs'),
    #path('updated_section2', views.section2, name='public_jobs'),
    path('cade_cases/', views.CadeCasesView.as_view(), name='cade_cases')
]
