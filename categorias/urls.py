from django.urls import path
from .views import (
    CategoriaListCreateView,
    CategoriaDetailView,
    CategoriaBuscarView,
)

app_name = 'categorias'

urlpatterns = [
    path('buscar/', CategoriaBuscarView.as_view(), name='categoria-buscar'),
    path('', CategoriaListCreateView.as_view(), name='categoria-list-create'),
    path('<int:id_categoria>/', CategoriaDetailView.as_view(), name='categoria-detail'),
]
