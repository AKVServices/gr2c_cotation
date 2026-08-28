from django import forms
from .models import Article, Categorie, Tiers, Mouvement, Cotation, LigneCotation, Facture, LigneFacture, Reglement

class ArticleForm(forms.ModelForm):
    class Meta:
        model=Article
        fields="__all__"
class CategorieForm(forms.ModelForm):
    class Meta: model=Categorie; fields="__all__"
class TiersForm(forms.ModelForm):
    class Meta: model=Tiers; fields="__all__"
class MouvementForm(forms.ModelForm):
    class Meta:
        model=Mouvement
        fields=["article","type","quantite","motif","tiers","doc_type"]
class CotationForm(forms.ModelForm):
    class Meta:
        model=Cotation
        fields=["tiers","objet","devis_festo","poids_kg","taux_majoration","taux_douane","taux_change","date_validite"]
class LigneCotationForm(forms.ModelForm):
    class Meta:
        model=LigneCotation
        fields=["article","quantite","taux_majoration"]
class ReglementForm(forms.ModelForm):
    class Meta: model=Reglement; fields=["date","montant","mode","reference"]
# class BonLivraisonForm(forms.ModelForm):
    #class Meta:
       # model = BonLivraison
        #fields = ["numero", "cotation", "tiers","date", "statut","signataire"]