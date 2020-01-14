from .views import SearchResultsView, ProfDataView, CalendarView
from django.urls import path
app_name="search"

urlpatterns = [
    path('', SearchResultsView.as_view(), name='search'),
	path('profinfo/', ProfDataView.as_view(), name='profinfo'),
	path('calendar/', CalendarView.as_view(), name='calendar'),
]
