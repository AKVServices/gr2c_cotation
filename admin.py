from django.contrib import admin
from .models import *
# BonLivraison et LigneLivraison temporairement désactivés.
admin.site.register([Parametre,UtilisateurProfil,Journal,Categorie,Tiers,Article,Mouvement,Cotation,LigneCotation,Facture,LigneFacture,Reglement])
