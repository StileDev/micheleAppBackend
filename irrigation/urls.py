from django.urls import path
from .views import (
    ParcelleListCreateView,
    ParcelleDeleteView,
    ParcelleDetailView,
    MaterielListCreateView,
    MaterielDeleteView,
    MesureCreateView,
    MesureTempsReelUpdateView,
    PompeEtatView,
    DemarrerIrrigationView,
    ArreterIrrigationView,
    IrrigationModeView,
    HistoriqueView,
    PrevisionView,
)

urlpatterns = [
    path('parcelles/', ParcelleListCreateView.as_view(), name='parcelle-list-create'),
    path('parcelles/<int:parcelle_id>/', ParcelleDeleteView.as_view(), name='parcelle-delete'),
    path('parcelles/<int:parcelle_id>/detail/', ParcelleDetailView.as_view(), name='parcelle-detail'),

    path('parcelles/<int:parcelle_id>/materiels/', MaterielListCreateView.as_view(), name='materiel-list-create'),
    path('parcelles/<int:parcelle_id>/materiels/<int:materiel_id>/', MaterielDeleteView.as_view(), name='materiel-delete'),

    path('parcelles/<int:parcelle_id>/mesures/', MesureCreateView.as_view(), name='mesure-create'),
    path('parcelles/<int:parcelle_id>/mesures/temps-reel/', MesureTempsReelUpdateView.as_view(), name='mesure-temps-reel'),
    path('parcelles/<int:parcelle_id>/pompe/etat/', PompeEtatView.as_view(), name='pompe-etat'),

    path('parcelles/<int:parcelle_id>/irrigation/demarrer/', DemarrerIrrigationView.as_view(), name='irrigation-demarrer'),
    path('parcelles/<int:parcelle_id>/irrigation/arreter/', ArreterIrrigationView.as_view(), name='irrigation-arreter'),
    path('parcelles/<int:parcelle_id>/irrigation/mode/', IrrigationModeView.as_view(), name='irrigation-mode'),

    path('parcelles/<int:parcelle_id>/historique/', HistoriqueView.as_view(), name='historique'),
    path('parcelles/<int:parcelle_id>/prevision/', PrevisionView.as_view(), name='prevision'),
]