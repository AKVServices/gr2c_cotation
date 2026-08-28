from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import *
from decimal import Decimal
class Command(BaseCommand):
    help="Initialise les paramètres, catégories, compte admin et quelques articles de démonstration."
    def handle(self,*args,**kwargs):
        u,_=User.objects.get_or_create(username="admin",defaults={"first_name":"GR2C","is_staff":True,"is_superuser":True})
        u.set_password("admin123"); u.is_staff=True; u.is_superuser=True; u.save()
        UtilisateurProfil.objects.update_or_create(user=u,defaults={"profil":Profil.DIRECTION})
        params={"taux_majoration":"0.30","seuil_marge":"0.15","taux_change":"655.957","forfait_transport":"120","tarif_kg":"30","taux_douane":"0.075","taux_tva":"0.18","validite_cotation_jours":"60"}
        for k,v in params.items(): Parametre.objects.get_or_create(cle=k,defaults={"valeur":v,"auteur":u})
        cats=["Automatisation","Capteurs","Actionneurs","Pneumatique","Électrique","Contrôle","Vannes","Raccords","Tuyaux","Filtres","Régulateurs","Distributeurs","Vérins","Moteurs","Accessoires","Kits","Autres"]
        for i,n in enumerate(cats,1): Categorie.objects.get_or_create(libelle=n,defaults={"position":i})
        cat=Categorie.objects.first()
        samples=[("FESTO-001","Article Festo de démonstration"),("FESTO-002","Capteur industriel de démonstration"),("FESTO-003","Vérin pneumatique de démonstration")]
        for ref,des in samples: Article.objects.get_or_create(reference=ref,defaults={"designation":des,"categorie":cat,"prix_achat":Decimal("100"),"qte_stock":Decimal("10"),"seuil_alerte":Decimal("2"),"origine":"Allemagne"})
        self.stdout.write(self.style.SUCCESS("GR2C initialisé. Compte admin/admin123"))
