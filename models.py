from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Parametre(models.Model):
    libelle = models.CharField(max_length=100, unique=True)
    valeur = models.CharField(max_length=255)
    date_modification = models.DateTimeField(auto_now=True)
    auteur = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    commentaire = models.CharField(max_length=255,default="",blank=True)
    def __str__(self): return f"{self.cle}={self.valeur}"

class Profil(models.TextChoices):
    DIRECTION="direction","Direction"
    COMMERCIAL="commercial","Chargé d'affaires"
    MAGASINIER="magasinier","Magasinier"
    CONSULTATION="consultation","Consultation"

class UtilisateurProfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profil = models.CharField(max_length=30, choices=Profil.choices, default=Profil.CONSULTATION)
    #actif = models.BooleanField(default=True)
    derniere_connexion = models.DateTimeField(null=True, blank=True)
    def __str__(self): return f"{self.user.username} — {self.get_profil_display()}"

class Journal(models.Model):
    date_action = models.DateTimeField(auto_now_add=True)
    auteur = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=80)
    objet = models.CharField(max_length=100)
    objet_id = models.PositiveBigIntegerField(null=True, blank=True)
    details = models.TextField(blank=True)

class Categorie(models.Model):
    libelle = models.CharField(max_length=150, unique=True)
    position = models.PositiveIntegerField(default=0)
    def __str__(self): return self.libelle

class Tiers(models.Model):
    CLIENT="client"; FOURNISSEUR="fournisseur"; MIXTE="mixte"
    TYPES=[(CLIENT,"Client"),(FOURNISSEUR,"Fournisseur"),(MIXTE,"Mixte")]
    raison_sociale=models.CharField(max_length=200)
    type=models.CharField(max_length=20,choices=TYPES)
    adresse=models.CharField(max_length=255,blank=True); ville=models.CharField(max_length=100,blank=True)
    pays=models.CharField(max_length=100,default="Togo"); telephone=models.CharField(max_length=50,blank=True)
    email=models.EmailField(blank=True); conditions_paiement=models.CharField(max_length=255,blank=True)
    nom=models.CharField(max_length=150); fonction=models.CharField(max_length=100,blank=True)
    telephone=models.CharField(max_length=50,blank=True); email=models.EmailField(blank=True); principal=models.BooleanField(default=False)
    notes=models.TextField(blank=True)
    def __str__(self): return self.raison_sociale

class Article(models.Model):
    UNITS=[("pce","pce"),("m","m"),("kit","kit"),("lot","lot")]
    reference=models.CharField(max_length=100,unique=True); designation=models.CharField(max_length=255)
    categorie=models.ForeignKey(Categorie,on_delete=models.PROTECT,related_name="articles")
    unite=models.CharField(max_length=10,choices=UNITS,default="pce"); origine=models.CharField(max_length=100,blank=True)
    code_douanier=models.CharField(max_length=50,blank=True); prix_achat=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    #date_prix=models.DateField(null=True,blank=True); 
    taux_majoration=models.DecimalField(max_digits=6,decimal_places=3,null=True,blank=True)
    qte_stock=models.DecimalField(max_digits=12,decimal_places=2,default=0); seuil_alerte=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    emplacement=models.CharField(max_length=120,blank=True); #actif=models.BooleanField(default=True)
    def __str__(self): return f"{self.reference} — {self.designation}"

class Mouvement(models.Model):
    TYPES=[("entree","Entrée"),("sortie","Sortie"),("ajustement","Ajustement")]
    DOCS=[("bon_livraison","Bon de livraison"),("achat","Achat"),("inventaire","Inventaire")]
    article=models.ForeignKey(Article,on_delete=models.PROTECT,related_name="mouvements")
    type=models.CharField(max_length=20,choices=TYPES); quantite=models.DecimalField(max_digits=12,decimal_places=2)
    date_mvt=models.DateTimeField(default=timezone.now); motif=models.TextField(blank=True)
    tiers=models.ForeignKey(Tiers,null=True,blank=True,on_delete=models.SET_NULL)
    doc_type=models.CharField(max_length=30,choices=DOCS,blank=True); doc_id=models.PositiveBigIntegerField(null=True,blank=True)
    auteur=models.ForeignKey(User,null=True,on_delete=models.SET_NULL)
    def save(self,*args,**kwargs):
        if not self.pk:
            if self.type=="sortie" and self.article.qte_stock < self.quantite:
                raise ValueError("Stock insuffisant pour cette sortie.")
            if self.type=="entree": self.article.qte_stock += self.quantite
            elif self.type=="sortie": self.article.qte_stock -= self.quantite
            elif self.type=="ajustement": self.article.qte_stock += self.quantite
            self.article.save(update_fields=["qte_stock"])
        return super().save(*args,**kwargs)

class Cotation(models.Model):
    STATUTS=[("brouillon","Brouillon"),("envoyee","Envoyée"),("relancee","Relancée"),("acceptee","Acceptée"),("refusee","Refusée"),("expiree","Expirée")]
    numero=models.CharField(max_length=120,unique=True); indice=models.PositiveIntegerField(default=1)
    tiers=models.ForeignKey(Tiers,on_delete=models.PROTECT,related_name="cotations"); date_cot=models.DateField(default=timezone.now)
    objet=models.CharField(max_length=255,blank=True); devis_festo=models.CharField(max_length=120,blank=True)
    poids_kg=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    taux_majoration=models.DecimalField(max_digits=6,decimal_places=3,default=0.30)
    taux_douane=models.DecimalField(max_digits=6,decimal_places=3,default=0.075)
    taux_change=models.DecimalField(max_digits=12,decimal_places=3,default=655.957)
    montant_marchandises=models.DecimalField(max_digits=14,decimal_places=2,default=0)
    transport=models.DecimalField(max_digits=14,decimal_places=2,default=0); douane=models.DecimalField(max_digits=14,decimal_places=2,default=0)
    total_ht=models.DecimalField(max_digits=14,decimal_places=2,default=0); cout_achat=models.DecimalField(max_digits=14,decimal_places=2,default=0)
    date_validite=models.DateField(null=True,blank=True); statut=models.CharField(max_length=20,choices=STATUTS,default="brouillon")
    auteur=models.ForeignKey(User,null=True,on_delete=models.SET_NULL)
    date_envoi=models.DateField(null=True,blank=True); date_relance_14=models.DateField(null=True,blank=True); date_relance_30=models.DateField(null=True,blank=True)
    def recalculer(self):
        from decimal import Decimal
        self.montant_marchandises=sum((l.total for l in self.lignes.all()),Decimal("0"))
        self.cout_achat=sum((l.prix_achat_unitaire*l.quantite for l in self.lignes.all()),Decimal("0"))
        self.transport=Decimal("120")+max(Decimal("0"),self.poids_kg-Decimal("1"))*Decimal("30")
        self.douane=(self.montant_marchandises+self.transport)*self.taux_douane
        self.total_ht=self.montant_marchandises+self.transport+self.douane
        self.save(update_fields=["montant_marchandises","cout_achat","transport","douane","total_ht"])
    @property
    def marge(self): return (self.total_ht-self.cout_achat) if self.total_ht else 0
    @property
    def taux_marge(self): return float(self.marge/self.total_ht*100) if self.total_ht else 0

class LigneCotation(models.Model):
    cotation=models.ForeignKey(Cotation,on_delete=models.CASCADE,related_name="lignes")
    article=models.ForeignKey(Article,on_delete=models.PROTECT)
    designation=models.CharField(max_length=255); quantite=models.DecimalField(max_digits=12,decimal_places=2)
    prix_achat_unitaire=models.DecimalField(max_digits=12,decimal_places=2); taux_majoration=models.DecimalField(max_digits=6,decimal_places=3)
    prix_vente_unitaire=models.DecimalField(max_digits=12,decimal_places=2,default=0); total=models.DecimalField(max_digits=14,decimal_places=2,default=0)
    def save(self,*args,**kwargs):
        self.prix_vente_unitaire=self.prix_achat_unitaire*(1+self.taux_majoration); self.total=self.prix_vente_unitaire*self.quantite
        return super().save(*args,**kwargs)

class BonLivraison(models.Model):
    STATUTS=[("brouillon","Brouillon"),("valide","Validé")]
    numero=models.CharField(max_length=50,unique=True); cotation=models.ForeignKey(Cotation,on_delete=models.PROTECT,related_name="bons_livraison")
    tiers=models.ForeignKey(Tiers,on_delete=models.PROTECT); date=models.DateField(default=timezone.now); statut=models.CharField(max_length=20,choices=STATUTS,default="brouillon")
    signataire=models.CharField(max_length=150,blank=True); auteur=models.ForeignKey(User,null=True,on_delete=models.SET_NULL)
    def valider(self):
        if self.statut=="valide": return
        for l in self.lignes.all():
            Mouvement.objects.create(article=l.article,type="sortie",quantite=l.quantite,tiers=self.tiers,doc_type="bon_livraison",doc_id=self.id,auteur=self.auteur)
        self.statut="valide"; self.save(update_fields=["statut"])

class LigneLivraison(models.Model):
    bon=models.ForeignKey(BonLivraison,on_delete=models.CASCADE,related_name="lignes")
    article=models.ForeignKey(Article,on_delete=models.PROTECT); quantite=models.DecimalField(max_digits=12,decimal_places=2)

class Facture(models.Model):
    # Facture directement liée à une cotation.
    cotation=models.ForeignKey(Cotation,null=True,blank=True,on_delete=models.PROTECT,related_name="factures")
    STATUTS=[("emise","Émise"),("partiellement_reglee","Partiellement réglée"),("reglee","Réglée"),("en_retard","En retard"),("annulee","Annulée")]
    numero=models.CharField(max_length=50,unique=True); tiers=models.ForeignKey(Tiers,on_delete=models.PROTECT,related_name="factures")
    date_fac=models.DateField(default=timezone.now); echeance=models.DateField(null=True,blank=True)
    total_ht=models.DecimalField(max_digits=14,decimal_places=2,default=0); taux_tva=models.DecimalField(max_digits=5,decimal_places=3,default=0.18)
    tva=models.DecimalField(max_digits=14,decimal_places=2,default=0); total_ttc=models.DecimalField(max_digits=14,decimal_places=2,default=0)
    montant_regle=models.DecimalField(max_digits=14,decimal_places=2,default=0); statut=models.CharField(max_length=30,choices=STATUTS,default="emise")
    auteur=models.ForeignKey(User,null=True,on_delete=models.SET_NULL)
    def recalculer(self):
        self.tva=self.total_ht*self.taux_tva; self.total_ttc=self.total_ht+self.tva
        self.save(update_fields=["tva","total_ttc"])

class LigneFacture(models.Model):
    facture=models.ForeignKey(Facture,on_delete=models.CASCADE,related_name="lignes")
    # bon=models.ForeignKey(BonLivraison,null=True,blank=True,on_delete=models.PROTECT)  # Module livraison désactivé
    article=models.ForeignKey(Article,on_delete=models.PROTECT); designation=models.CharField(max_length=255)
    quantite=models.DecimalField(max_digits=12,decimal_places=2); prix_unitaire=models.DecimalField(max_digits=12,decimal_places=2)
    total=models.DecimalField(max_digits=14,decimal_places=2,default=0)
    def save(self,*args,**kwargs):
        self.total=self.quantite*self.prix_unitaire
        return super().save(*args,**kwargs)

class Reglement(models.Model):
    facture=models.ForeignKey(Facture,on_delete=models.PROTECT,related_name="reglements")
    date=models.DateField(default=timezone.now); montant=models.DecimalField(max_digits=14,decimal_places=2); mode=models.CharField(max_length=50,default="Espèces")
    reference=models.CharField(max_length=100,blank=True); auteur=models.ForeignKey(User,null=True,on_delete=models.SET_NULL)
    def save(self,*args,**kwargs):
        from django.db import transaction
        with transaction.atomic():
            f=Facture.objects.select_for_update().get(pk=self.facture_id)
            if f.montant_regle+self.montant > f.total_ttc: raise ValueError("Le règlement dépasse le solde dû.")
            result=super().save(*args,**kwargs)
            f.montant_regle += self.montant
            f.statut="reglee" if f.montant_regle >= f.total_ttc else "partiellement_reglee"
            f.save(update_fields=["montant_regle","statut"])
            return result
