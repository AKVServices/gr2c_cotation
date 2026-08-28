from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from .models import *
from .forms import *

def profile(request):
    return getattr(request.user,"utilisateurprofil",None)

@login_required
def dashboard(request):
    articles=list(Article.objects.all())
    stock_value=sum(a.prix_achat*a.qte_stock for a in articles)
    alerts=[a for a in articles if a.qte_stock <= a.seuil_alerte]
    cotations=Cotation.objects.exclude(statut__in=["refusee","expiree"])
    return render(request,"core/dashboard.html",{"stock_value":stock_value,"article_count":len(articles),"alerts":alerts,"cotations":cotations,"factures_retard":Facture.objects.filter(statut="en_retard"),"profile":profile(request)})

@login_required
def articles(request):
    q=request.GET.get("q","")
    qs=Article.objects.all().select_related("categorie")
    if q: qs=qs.filter(Q(reference__icontains=q)|Q(designation__icontains=q)|Q(categorie__libelle__icontains=q))
    return render(request,"core/articles.html",{"articles":qs,"q":q})
@login_required
def article_create(request):
    if request.method=="POST":
        f=ArticleForm(request.POST)
        if f.is_valid(): obj=f.save(); Journal.objects.create(auteur=request.user,action="création",objet="article",objet_id=obj.id); messages.success(request,"Article créé."); return redirect("articles")
    else: f=ArticleForm()
    return render(request,"core/form.html",{"form":f,"title":"Nouvel article"})

@login_required
def tiers(request):
    q=request.GET.get("q",""); qs=Tiers.objects.all()
    if q: qs=qs.filter(raison_sociale__icontains=q)
    return render(request,"core/tiers.html",{"tiers":qs,"q":q})
@login_required
def tier_create(request):
    if request.method=="POST":
        f=TiersForm(request.POST)
        if f.is_valid(): f.save(); return redirect("tiers")
    else: f=TiersForm()
    return render(request,"core/form.html",{"form":f,"title":"Nouveau tiers"})

@login_required
def mouvements(request):
    qs=Mouvement.objects.select_related("article","tiers","auteur").order_by("-date_mvt")
    return render(request,"core/mouvements.html",{"mouvements":qs})
@login_required
def mouvement_create(request):
    if request.method=="POST":
        f=MouvementForm(request.POST)
        if f.is_valid():
            try:
                obj=f.save(commit=False); obj.auteur=request.user; obj.save(); messages.success(request,"Mouvement enregistré."); return redirect("mouvements")
            except ValueError as e: f.add_error("quantite",str(e))
    else: f=MouvementForm()
    return render(request,"core/form.html",{"form":f,"title":"Nouveau mouvement"})

@login_required
def cotations(request):
    return render(request,"core/cotations.html",{"cotations":Cotation.objects.select_related("tiers","auteur").order_by("-date_cot")})
@login_required
def cotation_create(request):
    if request.method=="POST":
        f=CotationForm(request.POST)
        if f.is_valid():
            c=f.save(commit=False); c.auteur=request.user
            c.numero=f"COT-{c.tiers.raison_sociale[:12].upper()}-{c.devis_festo or 'REF'}-01"; c.save()
            return redirect("cotation_detail",c.id)
    else: f=CotationForm(initial={"taux_majoration":"0.30","taux_douane":"0.075","taux_change":"655.957"})
    return render(request,"core/form.html",{"form":f,"title":"Nouvelle cotation"})

@login_required
def cotation_detail(request,pk):
    c=get_object_or_404(Cotation,pk=pk)
    if request.method=="POST" and c.statut=="brouillon":
        lf=LigneCotationForm(request.POST)
        if lf.is_valid():
            l=lf.save(commit=False); l.cotation=c; l.designation=l.article.designation; l.prix_achat_unitaire=l.article.prix_achat
            l.save(); c.recalculer(); return redirect("cotation_detail",pk=pk)
    else: lf=LigneCotationForm()
    return render(request,"core/cotation_detail.html",{"cotation":c,"form":lf})

@login_required
def cotation_emit(request,pk):
    c=get_object_or_404(Cotation,pk=pk)
    if c.statut!="brouillon": messages.error(request,"Cette cotation est déjà émise.")
    elif c.taux_marge < 15 and profile(request).profil != Profil.DIRECTION: messages.error(request,"Marge inférieure à 15 % : validation Direction requise.")
    else:
        c.statut="envoyee"; c.date_envoi=timezone.now().date(); c.date_relance_14=c.date_envoi+timedelta(days=14); c.date_relance_30=c.date_envoi+timedelta(days=30); c.save()
        messages.success(request,"Cotation émise.")
    return redirect("cotation_detail",pk=pk)

# === MODULE LIVRAISONS / BONS DE LIVRAISON TEMPORAIREMENT DESACTIVE ===
#@login_required
#def livraisons(request):
#    return render(request,"core/livraisons.html",{"bons":BonLivraison.objects.select_related("tiers","cotation").order_by("-date")})
#@login_required
#def livraison_create(request, cotation_id):
#    c=get_object_or_404(Cotation,pk=cotation_id,statut="acceptee")
#    if request.method=="POST":
#        b=BonLivraison.objects.create(numero=f"BL-{timezone.now():%Y%m%d%H%M%S}",cotation=c,tiers=c.tiers,auteur=request.user)
#        for l in c.lignes.all(): LigneLivraison.objects.create(bon=b,article=l.article,quantite=l.quantite)
#        b.valider(); messages.success(request,"Bon de livraison validé et stock décrémenté."); return redirect("livraisons")
#    return render(request,"core/form_confirm.html",{"title":"Valider la livraison","text":f"Créer et valider la livraison de {c.numero} ?","action":"Confirmer"})
#
#
#@login_required
#def bon_livraison_create(request):
#
#    if request.method == "POST":
#        form = BonLivraisonForm(request.POST)
#
#        if form.is_valid():
#            bon = form.save(commit=False)
#            bon.auteur = request.user
#            bon.save()
#
#            messages.success(
#                request,
#                "Bon de livraison créé avec succès."
#            )
#
#            return redirect("livraisons")
#
#    else:
#        form = BonLivraisonForm()
#
#    return render(
#        request,
#        "core/form.html",
#        {
#            "form": form,
#            "title": "Nouveau bon de livraison"
#        }
#    )
#

@login_required
def factures(request):
    factures_qs = Facture.objects.select_related("tiers", "cotation").order_by("-date_fac")
    return render(request, "core/factures.html", {"factures": factures_qs})

@login_required
def facture_nouvelle(request):
    cotations_qs = Cotation.objects.select_related("tiers").exclude(statut__in=["refusee", "expiree"]).order_by("-date_cot")
    return render(request, "core/facture_nouvelle.html", {"cotations": cotations_qs})

@login_required
def facture_create(request, cotation_id):
    c = get_object_or_404(Cotation, pk=cotation_id)
    numero = f"FAC-{timezone.now():%Y}-" + f"{Facture.objects.filter(date_fac__year=timezone.now().year).count()+1:04d}"
    f = Facture.objects.create(numero=numero, cotation=c, tiers=c.tiers, auteur=request.user)
    total = 0
    for l in c.lignes.all():
        lf = LigneFacture.objects.create(facture=f, article=l.article, designation=l.designation, quantite=l.quantite, prix_unitaire=l.prix_vente_unitaire)
        total += lf.total
    f.total_ht = total
    f.recalculer()
    messages.success(request, f"Facture {f.numero} créée à partir de la cotation {c.numero}.")
    return redirect("factures")

@login_required
def reglement_create(request, facture_id):
    f=get_object_or_404(Facture,pk=facture_id)
    if request.method=="POST":
        form=ReglementForm(request.POST)
        if form.is_valid():
            r=form.save(commit=False); r.facture=f; r.auteur=request.user
            try: r.save(); messages.success(request,"Règlement enregistré."); return redirect("factures")
            except ValueError as e: form.add_error("montant",str(e))
    else: form=ReglementForm()
    return render(request,"core/form.html",{"form":form,"title":f"Règlement {f.numero}"})

@login_required
def pdf_cotation(request,pk):
    from reportlab.pdfgen import canvas
    c=get_object_or_404(Cotation,pk=pk)
    response=HttpResponse(content_type="application/pdf"); response["Content-Disposition"]=f'attachment; filename="{c.numero}.pdf"'
    p=canvas.Canvas(response); p.setFont("Helvetica-Bold",16); p.drawString(50,800,"GR2C — PARTENAIRE FESTO")
    p.setFont("Helvetica",10); p.drawString(50,780,f"Cotation : {c.numero}"); p.drawString(50,765,f"Client : {c.tiers.raison_sociale}")
    y=730
    for l in c.lignes.all():
        p.drawString(50,y,f"{l.article.reference} | {l.designation[:40]} | {l.quantite} | {l.prix_vente_unitaire:.2f} € | {l.total:.2f} €"); y-=18
    p.drawString(50,y-10,f"Marchandises : {c.montant_marchandises:.2f} €"); p.drawString(50,y-28,f"Transport : {c.transport:.2f} €"); p.drawString(50,y-46,f"Douane : {c.douane:.2f} €")
    p.setFont("Helvetica-Bold",11); p.drawString(50,y-70,f"TOTAL HT : {c.total_ht:.2f} €"); p.drawString(50,y-88,f"Indicatif FCFA : {c.total_ht*c.taux_change:.0f} FCFA")
    p.save(); return response

@login_required
def pdf_facture(request,pk):
    from reportlab.pdfgen import canvas
    f=get_object_or_404(Facture,pk=pk)
    response=HttpResponse(content_type="application/pdf"); response["Content-Disposition"]=f'attachment; filename="{f.numero}.pdf"'
    p=canvas.Canvas(response); p.setFont("Helvetica-Bold",16); p.drawString(50,800,"GR2C — FACTURE")
    p.setFont("Helvetica",10); p.drawString(50,780,f"{f.numero} | Client : {f.tiers.raison_sociale}")
    y=750
    for l in f.lignes.all(): p.drawString(50,y,f"{l.designation[:50]} | {l.quantite} | {l.prix_unitaire:.2f} € | {l.total:.2f} €"); y-=18
    p.setFont("Helvetica-Bold",11); p.drawString(50,y-15,f"HT : {f.total_ht:.2f} €"); p.drawString(50,y-33,f"TVA 18 % : {f.tva:.2f} €"); p.drawString(50,y-51,f"TTC : {f.total_ttc:.2f} €")
    p.save(); return response
