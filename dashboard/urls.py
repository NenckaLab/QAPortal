from django.urls import path

from .views import HomePageView, SearchResultsView

urlpatterns = [
    path("plot/", SearchResultsView.as_view(), name="plot"),
    path("", HomePageView.as_view(), name="home"),

]