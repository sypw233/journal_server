from django.urls import path
from .views import EntryListCreateView, EntryRetrieveUpdateDestroyView, SyncDataView

urlpatterns = [
    path('entries/', EntryListCreateView.as_view(), name='entry-list-create'),
    path('entries/<int:pk>/', EntryRetrieveUpdateDestroyView.as_view(), name='entry-detail'),
    path('sync/', SyncDataView.as_view(), name='sync-data'),
]