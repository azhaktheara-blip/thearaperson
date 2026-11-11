from django.urls import path
from . import views
urlpatterns=[
    path('',views.HomeView.as_view(),name='home'),
    path('work/',views.PortfolioView.as_view(),name='portfolio'),
    path('work/<slug:slug>/',views.ProjectDetailView.as_view(),name='project_detail'),
    path('about/',views.AboutView.as_view(),name='about'),
    path('journal/',views.BlogListView.as_view(),name='blog'),
    path('journal/<slug:slug>/',views.PostDetailView.as_view(),name='post_detail'),
    path('contact/',views.ContactView.as_view(),name='contact'),
    path('api/contact/',views.contact_api,name='contact_api')]
