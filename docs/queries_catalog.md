# Requêtes SQL passées à `requete()`

Ce fichier liste toutes les requêtes SQL passées à la fonction `requete` (ou `$win->requete()` / `$this->requete()`), avec une courte description et des hashtags contenant les noms de tables utilisées.

## `cron.php`
- CA mensuel du grossiste Pharmar sur l’année/mois courant. #COMGROS #FOURNIS
  ```sql
  SELECT round(sum(montantTTCrecu)) as ca
  FROM COMGROS as a
  left join FOURNIS as c on a.code_fourn=c.code
  where year(FROM_UNIXTIME(DTime_Send)) = year(now())
    and month(FROM_UNIXTIME(DTime_Send)) = month(now())
    and c.nom = "pharmar"
  ```
- Récupère TVA, stock et prix pour une liste d’EAN13 afin de synchroniser le stock/prix. #produit #COMGROIT #comgros
  ```sql
  select TVA,ean13,convert(en_stock,char) as en_stock,prix_public,pahtnet
  from produit as a
  left join COMGROIT as b on a.cip = b.cip
  left join comgros as c on b.nocomgros = c.nocomgros
  WHERE b.nocomgros = (
    SELECT e.nocomgros
    FROM COMGROIT as e
    left join comgros as f on f.nocomgros = e.nocomgros
    Where a.cip=e.cip
    order by DTlivraisonreel desc
    limit 1
  )
  and ean13 in (...)
  ```
- Liste des produits homéo (doses) pour synchronisation. #produit
  ```sql
  SELECT nom,ean13 FROM produit WHERE nom like '%CH DO GL BOI' order by nom desc
  ```
- Liste des produits homéo (tubes) pour synchronisation. #produit
  ```sql
  SELECT nom,ean13 FROM produit WHERE nom like '%CH TG BOI' order by nom desc
  ```
- Totaux de ventes par opérateur (toutes ventes). #orders #orditem #produit
  ```sql
  SELECT oper_code,sum(convert(quantite,char)) as quantite
  FROM orders as a
  LEFT JOIN orditem as b on a.ti=b.order_ti
  LEFT JOIN produit as c on c.cip=b.cip
  WHERE a.code_subro not in ("RETF")
    and YEAR(date_order) = <année>
    and month(date_order) = <mois>
  group by oper_code
  ```
- Totaux de ventes par opérateur (remboursement code 4). #orders #orditem #produit
  ```sql
  SELECT oper_code,sum(convert(quantite,char)) as quantite
  FROM orders as a
  LEFT JOIN orditem as b on a.ti=b.order_ti
  LEFT JOIN produit as c on c.cip=b.cip
  WHERE a.code_subro not in ("RETF")
    and a.Code_rembt = 4
    and YEAR(date_order) = <année>
    and month(date_order) = <mois>
  group by oper_code
  ```
- Totaux de ventes par opérateur sur une liste d’EAN13. #orders #orditem #produit
  ```sql
  SELECT oper_code,sum(convert(quantite,char)) as quantite
  FROM orders as a
  LEFT JOIN orditem as b on a.ti=b.order_ti
  LEFT JOIN produit as c on c.cip=b.cip
  WHERE a.code_subro not in ("RETF")
    and YEAR(date_order) = <année>
    and month(date_order) = <mois>
    and ean13 in (...)
  group by oper_code
  ```
- CA journalier pour une date donnée. #HISTORY
  ```sql
  SELECT EspeceEUR, ChequeEUR, CB, (Centre+Mutuelle) as medoc, Virement,
         (Differe_positif+EnCompte_positif+EnCompte_Negatif+Differe_Negatif) as encompte,
         nb_De_Factures, (Marge_Rembt+Marge_NRembt) as marge
  FROM HISTORY
  WHERE date = "<YYYY-MM-DD>"
  ```
- Historique CA GPP sur période (statistiques). #HISTORY
  ```sql
  SELECT DATE_FORMAT(date,"%Y-%m-%d") as date,(EspeceEUR) as esp_gpp,(ChequeEUR) as cheque_gpp,(CB) as cb_gpp,
         ((Centre+Mutuelle)) as secu_gpp,((Differe_positif+EnCompte_positif+EnCompte_Negatif+EnCompte_Positif)) as encompte_gpp,
         (nb_De_Factures) as client_gpp,((Marge_Rembt+Marge_NRembt)) as marge_gpp,
         (EspeceEUR+ChequeEUR+CB+Centre+Mutuelle+Differe_positif+EnCompte_Positif+Differe_Negatif+EnCompte_Negatif+Virement) as ca_gpp
  FROM HISTORY
  WHERE date BETWEEN ("2013-07-25") AND ("<YYYY-MM-DD>")
  ```
- Historique CA Frang sur période (statistiques). #HISTORY
  ```sql
  SELECT DATE_FORMAT(date,"%Y-%m-%d") as date,(EspeceEUR) as esp_frang,(ChequeEUR) as cheque_frang,(CB) as cb_frang,
         ((Centre+Mutuelle)) as secu_frang,((Differe_positif+EnCompte_positif+EnCompte_Negatif+EnCompte_Positif)) as encompte_frang,
         convert(nb_De_Factures,char) as client_frang,((Marge_Rembt+Marge_NRembt)) as marge_frang,
         (EspeceEUR+ChequeEUR+CB+Centre+Mutuelle+Differe_positif+Differe_Negatif+EnCompte_Negatif+EnCompte_Positif+Virement) as ca_frang
  FROM HISTORY
  WHERE date BETWEEN ("2013-07-25") AND ("<YYYY-MM-DD>")
  ```
- CA web journalier (règlement type "w"). #REGORD #ORDERS
  ```sql
  Select Date_Format(ORDERS.Date_order, "%Y-%m-%d") As order_date,Sum((ORDERS.Total_general)) As web
  From REGORD
  Left Join ORDERS On REGORD.Order_TI = ORDERS.TI
  Where REGORD.RegleType = "w"
    and Date_Format(ORDERS.Date_order, "%Y-%m-%d") BETWEEN ("2013-07-25") AND ("<YYYY-MM-DD>")
  Group By Date_Format(ORDERS.Date_order, "%Y-%m-%d")
  ```
- Export par lots: compter les produits. #produit
  ```sql
  SELECT count(*) as total FROM produit
  ```
- Export par lots: page de produits. #produit
  ```sql
  SELECT * FROM produit limit <offset>,10000
  ```
- Export par lots: compter MQ_form. #MQ_form
  ```sql
  SELECT count(*) as total FROM MQ_form
  ```
- Export par lots: page MQ_form. #MQ_form
  ```sql
  SELECT * FROM MQ_form limit <offset>,10000
  ```
- Export par lots: compter MQ_monog. #MQ_monog
  ```sql
  SELECT count(*) as total FROM MQ_monog
  ```
- Export par lots: page MQ_monog. #MQ_monog
  ```sql
  SELECT * FROM MQ_monog limit <offset>,10000
  ```
- Export par lots: compter MQ_memo. #MQ_memo
  ```sql
  SELECT count(*) as total FROM MQ_memo
  ```
- Export par lots: page MQ_memo. #MQ_memo
  ```sql
  SELECT * FROM MQ_memo limit <offset>,10000
  ```
- Export par lots: compter MQ_COMMN. #MQ_COMMN
  ```sql
  SELECT count(*) as total FROM MQ_COMMN
  ```
- Export par lots: page MQ_COMMN. #MQ_COMMN
  ```sql
  SELECT * FROM MQ_COMMN limit <offset>,10000
  ```
- Export par lots: compter BLOBS. #BLOBS
  ```sql
  SELECT count(*) as total FROM BLOBS
  ```
- Export par lots: page BLOBS. #BLOBS
  ```sql
  SELECT * FROM BLOBS limit <offset>,10000
  ```
- Extraction pour comparaison de prix (diff_prix). #PRODUIT #COMGROIT #comgros
  ```sql
  SELECT a.cip as cip,a.ean13 as ean13,nom,prix_public,base_rembt, b.pahtnet as pahtnet,
         (prix_public / pahtnet) as coeff,en_stock , DTlivraisonreel
  FROM PRODUIT as a
  left join COMGROIT as b on a.cip = b.cip
  left join comgros as c on b.nocomgros = c.nocomgros
  WHERE b.nocomgros = (
    SELECT e.nocomgros
    FROM COMGROIT as e
    left join comgros as f on f.nocomgros = e.nocomgros
    Where a.cip=e.cip
    order by DTlivraisonreel desc
    limit 1
  )
  and code_rembt in (4)
  and wflag & 8192 = 0
  and en_stock>0
  ```
- Vérification d’un CIP avant mise à jour de prix. #produit
  ```sql
  select cip from produit where cip = <cip>
  ```
- Dernière livraison par client (liste de cli_ti). #ORDERS
  ```sql
  Select ORDERS.Cli_TI, MAX(ORDERS.Date_order) AS derniere_facture
  From ORDERS
  Where ORDERS.Cli_TI IN ('...')
  Group By ORDERS.Cli_TI
  ```

## `class/bd_win.php`
- Ventes promo par opérateur sur des EAN13 ciblés. #orders #orditem #produit
  ```sql
  SELECT oper_code,sum(convert(quantite,char)) as quantite
  FROM orders as a
  LEFT JOIN orditem as b on a.ti=b.order_ti
  LEFT JOIN produit as c on c.cip=b.cip
  WHERE ean13 in ("3664798027419","3664798028195","3664798027914","3664798027556")
    and YEAR(date_order) = <année>
    and month(date_order) = <mois>
  group by facture
  ```
- Palmares par opérateur (code subro / rembt / ean13 filtre). #orders #orditem #produit
  ```sql
  SELECT oper_code,sum(convert(quantite,char)) as quantite
  FROM orders as a
  LEFT JOIN orditem as b on a.ti=b.order_ti
  LEFT JOIN produit as c on c.cip=b.cip
  WHERE a.code_subro in ("AT","FPAY","FSEI","FSES")
    and Code_fourn <> 1018
    and c.code_rembt in (4)
    and YEAR(date_order) = <année>
    and month(date_order) = <mois>
    and ean13 <> "1234567890123"
    and order_ti in (
      SELECT order_ti FROM ORDitem as a left join produit as b on a.cip=b.cip WHERE b.ean13="1234567890123"
    )
  group by Facture
  ```
- Détail palmarès avec quantités, nom, prix. #orders #orditem #produit
  ```sql
  SELECT date_order,Facture, sum(convert(quantite,char)) as quantite ,nom, Prix_public
  FROM orders as a
  LEFT JOIN orditem as b on a.ti=b.order_ti
  LEFT JOIN produit as c on c.cip=b.cip
  WHERE a.code_subro in ("AT","FPAY","FSEI","FSES")
    and Code_fourn <> 1018
    and c.code_rembt in (4)
    and YEAR(date_order) = <année>
    and month(date_order) = <mois>
    and ean13 <> "1234567890123"
    and order_ti in (
      SELECT order_ti FROM ORDitem as a left join produit as b on a.cip=b.cip WHERE b.ean13="1234567890123"
    )
  group by nom
  ```
- Liste des promotions actives. #PROMO #PROMITEM #produit
  ```sql
  SELECT *
  FROM PROMO as a
  left join PROMITEM as b on a.TI=b.HeaderTI
  left join produit as c on b.itemti=c.cip
  where a.nom not like '%@%'
    and a.Flags & 0x2 = 2
  order by a.ti desc
  ```
- CA grossistes (soredip/sipr/pharmar). #COMGROS #FOURNIS
  ```sql
  SELECT c.nom as fourn,year(FROM_UNIXTIME(DTime_Send)) as year,month(FROM_UNIXTIME(DTime_Send)) as month,
         round(sum(montantTTCrecu)) as ca
  FROM COMGROS as a
  left join FOURNIS as c on a.code_fourn=c.code
  where year(FROM_UNIXTIME(DTime_Send)) IN (2022)
    and c.nom in ('soredip','sipr','pharmar')
  group by month(FROM_UNIXTIME(DTime_Send)),code_fourn
  order by year(FROM_UNIXTIME(DTime_Send)),month(FROM_UNIXTIME(DTime_Send)),round(sum(montantTTCrecu)) desc
  ```
- Fournisseurs actifs (commandes). #fournis
  ```sql
  select * from fournis where flags & 0x64<>64 and flags & 0x8<>8
  ```
- Vérification d’un CIP avant mise à jour de prix. #produit
  ```sql
  select cip from produit where cip = <cip>
  ```
- Extraction pour comparaison de prix (diff_prix). #PRODUIT #COMGROIT #comgros
  ```sql
  SELECT a.cip as cip,a.ean13 as ean13,nom,prix_public,base_rembt, b.pahtnet as pahtnet,
         (prix_public / pahtnet) as coeff,en_stock , DTlivraisonreel
  FROM PRODUIT as a
  left join COMGROIT as b on a.cip = b.cip
  left join comgros as c on b.nocomgros = c.nocomgros
  WHERE b.nocomgros = (
    SELECT e.nocomgros
    FROM COMGROIT as e
    left join comgros as f on f.nocomgros = e.nocomgros
    Where a.cip=e.cip
    order by DTlivraisonreel desc
    limit 1
  )
  and code_rembt in (4)
  and wflag & 8192 = 0
  and en_stock>0
  ```
- Stock/prix Winpharma pour EAN13 du site (maj_stock_wp_2 & maj_stock_wp). #produit #COMGROIT #comgros
  ```sql
  select TVA,ean13,convert(en_stock,char) as en_stock,prix_public,pahtnet
  from produit as a
  left join COMGROIT as b on a.cip = b.cip
  left join comgros as c on b.nocomgros = c.nocomgros
  WHERE b.nocomgros = (
    SELECT e.nocomgros
    FROM COMGROIT as e
    left join comgros as f on f.nocomgros = e.nocomgros
    Where a.cip=e.cip
    order by DTlivraisonreel desc
    limit 1
  )
  and ean13 in (...)
  ```
- Liste de produits “panier” (codeacte=16). #PRODUIT #COMGROIT #comgros
  ```sql
  SELECT a.cip,nom,prix_public,base_rembt, pahtnet, (prix_public / pahtnet) as coeff,en_stock , DTlivraisonreel
  FROM PRODUIT as a
  left join COMGROIT as b on a.cip = b.cip
  left join comgros as c on b.nocomgros = c.nocomgros
  WHERE b.nocomgros = (
    SELECT e.nocomgros
    FROM COMGROIT as e
    left join comgros as f on f.nocomgros = e.nocomgros
    Where a.cip=e.cip
    order by DTlivraisonreel desc
    limit 1
  )
  and a.codeacte=16
  and en_stock>0
  and prix_public/pahtnet<1.1
  ```
- Extraction stock pour rétrocession Frang. #PRODUIT #stprod #COMGROIT #comgros #FOURNIS
  ```sql
  SELECT a.cip,a.nom, pahtnet, (prix_public / pahtnet) as coeff,Prix_Public,Dernier_Vente,
         case when ean13 = "" then a.cip else ean13 end as ean13,
         convert(en_stock,char) as en_stock,lastmonth,v1,v2,v3,
         case when wflag & 0x2 = 2 then 1 else 0 end as commande,
         case when (( en_stock > 0 ) ) then 1 else 0 end as tenu,
         (case when (round(datediff(curdate(),"1980-01-01")/30.47) - lastmonth) = 0 then (v1+...+v12)/12
               ...
               else 0 end) as moyenne,
         c.Code_Fourn as fournisseur
  FROM PRODUIT as a
  left join stprod on a.cip = stprod.cip
  left join COMGROIT as b on a.cip = b.cip
  left join comgros as c on b.nocomgros = c.nocomgros
  WHERE b.nocomgros = (
    SELECT e.nocomgros
    FROM COMGROIT as e
    LEFT JOIN comgros as f on f.nocomgros = e.nocomgros
    LEFT JOIN FOURNIS as g ON f.Code_Fourn = g.code
    WHERE g.Code <> "000002" and g.Code <> "261218" and a.cip=e.cip and pahtnet<> 0
    order by DTlivraisonreel desc
    limit 1
  )
  and code_rembt in (4)
  and wflag & 8192 = 0
  and lastmonth <> ""
  ```
- Extraction stock pour rétrocession GPP. #PRODUIT #stprod #COMGROIT #comgros #FOURNIS
  ```sql
  SELECT a.cip,a.nom, pahtnet, (prix_public / pahtnet) as coeff,Prix_Public,Dernier_Vente,
         case when ean13 = "" then a.cip else ean13 end as ean13,
         convert(en_stock,char) as en_stock,lastmonth,v1,v2,v3,
         case when wflag & 0x2 = 2 then 1 else 0 end as commande,
         case when (( en_stock > 0 ) ) then 1 else 0 end as tenu,
         (case when (round(datediff(curdate(),"1980-01-01")/30.47) - lastmonth) = 0 then (v1+...+v12)/12
               ...
               else 0 end) as moyenne,
         c.Code_Fourn as fournisseur
  FROM PRODUIT as a
  left join stprod on a.cip = stprod.cip
  left join COMGROIT as b on a.cip = b.cip
  left join comgros as c on b.nocomgros = c.nocomgros
  WHERE b.nocomgros = (
    SELECT e.nocomgros
    FROM COMGROIT as e
    LEFT JOIN comgros as f on f.nocomgros = e.nocomgros
    LEFT JOIN FOURNIS as g ON f.Code_Fourn = g.code
    WHERE g.Code <> "000002" and g.Code <> "261218" and a.cip=e.cip and pahtnet<> 0
    order by DTlivraisonreel desc
    limit 1
  )
  and code_rembt in (4)
  and wflag & 8192 = 0
  order by en_stock desc
  ```
- Extraction stock pour rétrocession BIGPARA. #PRODUIT #stprod #COMGROIT #comgros #FOURNIS
  ```sql
  SELECT a.cip,a.nom, pahtnet, (prix_public / pahtnet) as coeff,Prix_Public,Dernier_Vente,
         case when ean13 = "" then a.cip else ean13 end as ean13,
         convert(en_stock,char) as en_stock,lastmonth,v1,v2,v3,
         case when wflag & 0x2 = 2 then 1 else 0 end as commande,
         case when (( en_stock > 0 ) ) then 1 else 0 end as tenu,
         (case when (round(datediff(curdate(),"1980-01-01")/30.47) - lastmonth) = 0 then (v1+...+v12)/12
               ...
               else 0 end) as moyenne,
         c.Code_Fourn as fournisseur
  FROM PRODUIT as a
  left join stprod on a.cip = stprod.cip
  left join COMGROIT as b on a.cip = b.cip
  left join comgros as c on b.nocomgros = c.nocomgros
  WHERE b.nocomgros = (
    SELECT e.nocomgros
    FROM COMGROIT as e
    LEFT JOIN comgros as f on f.nocomgros = e.nocomgros
    LEFT JOIN FOURNIS as g ON f.Code_Fourn = g.code
    WHERE g.Code <> "000002" and g.Code <> "261218" and a.cip=e.cip and pahtnet<> 0
    order by DTlivraisonreel desc
    limit 1
  )
  and code_rembt in (4)
  and wflag & 8192 = 0
  order by en_stock desc
  ```
- Libellé de fournisseur (conversion). #fournis
  ```sql
  SELECT Code,Nom FROM fournis where Code = '<code>'
  ```
- Informations d’un produit par EAN13. #produit #stprod
  ```sql
  SELECT *,convert(en_stock,char) as en_stock,
         round(datediff(curdate(),"1980-01-01")/30.47) - lastmonth as depart
  FROM produit as a
  left join stprod as b on a.cip = b.cip
  WHERE a.ean13 = "<ean13>"
  order by en_stock desc
  ```
- Recherche produit par nom (autocomplete). #produit
  ```sql
  SELECT Nom,ean13 FROM produit WHERE en_stock > 0 and Nom like "<nom>%" order by nom desc
  ```
- Liste de produits (filtres labo/stock/oubli), avec jointures dynamiques. #produit #MQ_FORM #comgroit #COMGROS #fournis
  ```sql
  SELECT * FROM produit as a <join dynamiques> WHERE <filtres> order by en_stock desc
  ```
- Liste des fournisseurs (gpp). #FOURNIS
  ```sql
  SELECT code,nom FROM FOURNIS
  ```

## `html/stock_faible/index.php`
- Produits à stock faible avec moyenne et délai réappro. #produit #stprod #COMHISTO #comgros #fournis
  ```sql
  Select produit.CIP, produit.Nom, produit.EAN13, produit.Dernier_Vente,
         (Case ... End) As moyenne,
         produit.En_stock, comgros.DT_Livraison, fournis.Nom As Nom1, fournis.Delai_Reappro
  From produit
  Inner Join stprod On stprod.CIP = produit.CIP
  Inner Join COMHISTO On COMHISTO.Pro_CIP = produit.CIP
  Inner Join comgros On comgros.NoComGros = COMHISTO.NoComGros
  Inner Join fournis On fournis.Code = comgros.Code_Fourn
  Where produit.En_stock > 0
    And produit.En_stock < (((Case ... End)/30)*(fournis.Delai_Reappro/10))
    And (Select COMHISTO.NoComGros From COMHISTO Where produit.CIP = COMHISTO.Pro_CIP Order By COMHISTO.NoComGros Desc Limit 1) = COMHISTO.NoComGros
  group by COMHISTO.NoComGros
  ```

## `html/vente_kote_sante/index.php`
- Détail des ventes pour une date (kote santé). #orders #orditem #produit #memores
  ```sql
  SELECT a.facture,date_order,oper_code,(convert(quantite,char)) as quantite ,b.cip,c.nom,b.prix,memo
  FROM orders as a
  LEFT JOIN orditem as b on a.ti=b.order_ti
  LEFT JOIN produit as c on c.cip=b.cip
  left join memores as d on (b.memo_ti=d.ti and d.TBLN=7)
  WHERE a.code_subro in ("AT","FPAY","FSEI","FSES")
    and Code_fourn <> 1018
    and c.code_rembt in (4)
    and YEAR(date_order) = <année>
    and month(date_order) = <mois>
    and ean13 <> "1234567890123"
    and order_ti in (
      SELECT order_ti FROM ORDitem as a left join produit as b on a.cip=b.cip WHERE b.ean13="1234567890123"
    )
  order by a.facture DESC
  ```

## `html/ca_grossiste/index.php`
- CA grossistes sur 3 ans (frang/gpp). #COMGROS #FOURNIS
  ```sql
  SELECT c.nom as fourn,year(FROM_UNIXTIME(DTime_Send)) as year,month(FROM_UNIXTIME(DTime_Send)) as month,
         round(sum(montantTTCrecu)) as ca
  FROM COMGROS as a
  left join FOURNIS as c on a.code_fourn=c.code
  WHERE DTime_Send >= UNIX_TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 3 YEAR))
    and c.nom in ('soredip','sipr','pharmar')
  group by c.nom,YEAR(FROM_UNIXTIME(a.DTime_Send)), MONTH(FROM_UNIXTIME(a.DTime_Send))
  order by year(FROM_UNIXTIME(DTime_Send)),month(FROM_UNIXTIME(DTime_Send)),round(sum(montantTTCrecu)) desc
  ```

## `html/palmares/action.php`
- Recherche produit par EAN13 (palmarès). #produit
  ```sql
  SELECT Nom,ean13,en_stock FROM produit WHERE ean13="<search>" order by nom desc
  ```
- Recherche produit par nom (palmarès). #produit
  ```sql
  SELECT Nom,ean13,en_stock FROM produit WHERE Nom like ("%<search>%") and en_stock>0 order by nom desc
  ```

## `html/Recap_heure_Supp/action.php`
- Recherche produit par EAN13 (récap heures supp). #produit
  ```sql
  SELECT Nom,ean13,en_stock FROM produit WHERE ean13="<search>" order by nom desc
  ```
- Recherche produit par nom (récap heures supp). #produit
  ```sql
  SELECT Nom,ean13,en_stock FROM produit WHERE Nom like ("%<search>%") and en_stock>0 order by nom desc
  ```

## `html/f_eval/action.php`
- Recherche produit par EAN13 (f_eval). #produit
  ```sql
  SELECT Nom,ean13,en_stock FROM produit WHERE ean13="<search>" order by nom desc
  ```
- Recherche produit par nom (f_eval). #produit
  ```sql
  SELECT Nom,ean13,en_stock FROM produit WHERE Nom like ("%<search>%") and en_stock>0 order by nom desc
  ```

## `html/palmares/index.php`
- Détail palmarès GPP (EAN13 ciblés). #orders #orditem #produit
  ```sql
  SELECT date_order,Facture, (convert(quantite,char)) as quantite ,nom, Prix_public
  FROM orders as a
  LEFT JOIN orditem as b on a.ti=b.order_ti
  LEFT JOIN produit as c on c.cip=b.cip
  WHERE a.code_subro not in ("RETF")
    and YEAR(date_order) = <année>
    and month(date_order) = <mois>
    and ean13 in (...)
  ```
- Détail palmarès Frang (EAN13 ciblés). #orders #orditem #produit
  ```sql
  SELECT date_order,Facture, (convert(quantite,char)) as quantite ,nom, Prix_public
  FROM orders as a
  LEFT JOIN orditem as b on a.ti=b.order_ti
  LEFT JOIN produit as c on c.cip=b.cip
  WHERE a.code_subro not in ("RETF")
    and YEAR(date_order) = <année>
    and month(date_order) = <mois>
    and ean13 in (...)
  ```
- Totaux de ventes par opérateur (boîtes). #orders #orditem #produit
  ```sql
  SELECT oper_code,sum(convert(quantite,char)) as quantite
  FROM orders as a
  LEFT JOIN orditem as b on a.ti=b.order_ti
  LEFT JOIN produit as c on c.cip=b.cip
  WHERE a.code_subro not in ("RETF")
    and YEAR(date_order) = <année>
    and month(date_order) = <mois>
  group by oper_code
  ```
- Totaux de ventes par opérateur (boîtes rembt 4). #orders #orditem #produit
  ```sql
  SELECT oper_code,sum(convert(quantite,char)) as quantite
  FROM orders as a
  LEFT JOIN orditem as b on a.ti=b.order_ti
  LEFT JOIN produit as c on c.cip=b.cip
  WHERE a.code_subro not in ("RETF")
    and a.Code_rembt = 4
    and YEAR(date_order) = <année>
    and month(date_order) = <mois>
  group by oper_code
  ```
- Totaux de ventes par opérateur (EAN13 ciblés GPP). #orders #orditem #produit
  ```sql
  SELECT oper_code,sum(convert(quantite,char)) as quantite
  FROM orders as a
  LEFT JOIN orditem as b on a.ti=b.order_ti
  LEFT JOIN produit as c on c.cip=b.cip
  WHERE a.code_subro not in ("RETF")
    and YEAR(date_order) = <année>
    and month(date_order) = <mois>
    and ean13 in (...)
  group by oper_code
  ```
- Totaux de ventes par opérateur (EAN13 ciblés Frang). #orders #orditem #produit
  ```sql
  SELECT oper_code,sum(convert(quantite,char)) as quantite
  FROM orders as a
  LEFT JOIN orditem as b on a.ti=b.order_ti
  LEFT JOIN produit as c on c.cip=b.cip
  WHERE a.code_subro not in ("RETF")
    and YEAR(date_order) = <année>
    and month(date_order) = <mois>
    and ean13 in (...)
  group by oper_code
  ```

## `html/plan_livraison/action.php`
- Récupération du Cli_TI à partir d’une facture. #ORDERS
  ```sql
  Select ORDERS.Facture, ORDERS.Cli_TI From ORDERS Where ORDERS.Facture = '<facture>'
  ```
- Historique des achats d’un client (Cli_TI). #ORDERS #ORDITEM #produit
  ```sql
  Select ORDERS.Facture, ORDERS.Cli_TI, ORDITEM.CIP, ORDITEM.Quantite, produit.Nom, ORDERS.Date_order
  From ORDERS
  Inner Join ORDITEM On ORDITEM.Order_TI = ORDERS.TI
  Inner Join produit On produit.CIP = ORDITEM.CIP
  Where ORDERS.Cli_TI = '<cli_ti>'
  Order By ORDERS.Facture DESC, ORDERS.Date_order DESC
  ```

## `html/plan_livraison/view/clients.php`
- Historique achats client (vue). #ORDERS #ORDITEM #produit
  ```sql
  Select ORDERS.Facture, ORDERS.Cli_TI, ORDITEM.CIP, ORDITEM.Quantite, produit.Nom, ORDERS.Date_order
  From ORDERS
  Inner Join ORDITEM On ORDITEM.Order_TI = ORDERS.TI
  Inner Join produit On produit.CIP = ORDITEM.CIP
  Where ORDERS.Cli_TI = '<cli_ti>'
  Order By ORDERS.Facture DESC, ORDERS.Date_order DESC
  ```

## `html/injection_produit/action.php`
- Monographie produit (texte via MQ_memo/BLOBS). #produit #MQ_form #MQ_monog #MQ_memo #BLOBS
  ```sql
  Select a.cip,ean13,a.nom,liste,Gross,allait,
    case when c.poso > 1000000000 then (select Str from MQ_memo where Ti=c.poso) else (select offset from BLOBS where Ti=c.poso) end as poso,
    case when c.pharmacol > 1000000000 then (select Str from MQ_memo where Ti=c.pharmacol) else (select offset from BLOBS where Ti=c.pharmacol) end as pharmacol,
    case when c.cinetique > 1000000000 then (select Str from MQ_memo where Ti=c.cinetique) else (select offset from BLOBS where Ti=c.cinetique) end as cinetique,
    case when c.surdosage > 1000000000 then (select Str from MQ_memo where Ti=c.surdosage) else (select offset from BLOBS where Ti=c.surdosage) end as surdosage,
    case when c.effets_ad > 1000000000 then (select Str from MQ_memo where Ti=c.effets_ad) else (select offset from BLOBS where Ti=c.effets_ad) end as effets_ad,
    case when c.grouparis > 1000000000 then (select Str from MQ_memo where Ti=c.grouparis) else (select offset from BLOBS where Ti=c.grouparis) end as grouparis,
    case when c.misengard > 1000000000 then (select Str from MQ_memo where Ti=c.misengard) else (select offset from BLOBS where Ti=c.misengard) end as misengard,
    case when c.indicat > 1000000000 then (select Str from MQ_memo where Ti=c.indicat) else (select offset from BLOBS where Ti=c.indicat) end as indicat
  from produit as a
  left join MQ_form as b on a.cip = b.cip
  LEFT JOIN MQ_monog as c on b.RefMon = c.RefMon
  WHERE ean13 = <ean13>
  ```
- Alertes associées à un CIP. #MQ_ALERT #mq_commn
  ```sql
  SELECT Str
  FROM MQ_ALERT as a
  left join mq_commn as b on a.codsp=b.keyval
  where a.cip = <cip>
  ```

## `html/injection_produit/index.php`
- Liste produits pour injection (filtres dynamiques). #produit #MQ_FORM #comgroit #COMGROS #fournis #FORMES
  ```sql
  SELECT * FROM produit as a <join dynamiques> WHERE <filtres> order by a.nom desc
  ```

## `html/ca_mad/index.php`
- CA MAD (fauteuils, déambulateurs, etc.). #ORDERS #ORDITEM #produit #COMGROIT #COMGROS
  ```sql
  Select Year(date_order) As Annee, Month(date_order) As Mois, ...
  From ORDERS As a
  Left Join ORDITEM As b On a.ti = b.order_ti
  Left Join produit As c On c.cip = b.cip
  Left Join COMGROIT As d On c.cip = d.cip
  Left Join COMGROS As e On d.nocomgros = e.nocomgros
  Where d.nocomgros = (...)
    and a.code_subro Not In ('RETF')
    and (Nom Like '%fauteuil%' Or ...)
    and a.Flags2 & 4096 = 0 and a.Flags2 & 2048 = 0
  Group By Year(date_order), Month(date_order), nom
  ```

## `html/ca_laboratoire/index.php`
- CA mensuel par labos hors exclusions. #COMGROS #FOURNIS
  ```sql
  SELECT month(FROM_UNIXTIME(DTime_Send)) as month, round(sum(montantTTCrecu)) as ca
  FROM COMGROS as a
  LEFT JOIN FOURNIS as c on a.code_fourn=c.code
  WHERE year(FROM_UNIXTIME(DTime_Send)) = <année>
    AND LOWER(c.nom) NOT IN (<liste>)
  GROUP BY month(FROM_UNIXTIME(DTime_Send))
  ORDER BY month(FROM_UNIXTIME(DTime_Send))
  ```
- CA total par labo (hors exclusions). #COMGROS #FOURNIS
  ```sql
  SELECT c.nom as fourn, round(sum(montantTTCrecu)) as ca
  FROM COMGROS as a
  LEFT JOIN FOURNIS as c on a.code_fourn=c.code
  WHERE year(FROM_UNIXTIME(DTime_Send)) = <année>
    AND LOWER(c.nom) NOT IN (<liste>)
  GROUP BY code_fourn
  ORDER BY ca DESC
  ```

## `html/generique/index.php`
- Produits codeacte=16 (génériques). #PRODUIT #COMGROIT #comgros
  ```sql
  SELECT a.cip,a.ean13,nom,prix_public,base_rembt, pahtnet, (prix_public / pahtnet) as coeff,en_stock , DTlivraisonreel
  FROM PRODUIT as a
  left join COMGROIT as b on a.cip = b.cip
  left join comgros as c on b.nocomgros = c.nocomgros
  WHERE b.nocomgros = (
    SELECT e.nocomgros
    FROM COMGROIT as e
    left join comgros as f on f.nocomgros = e.nocomgros
    Where a.cip=e.cip
    order by DTlivraisonreel desc
    limit 1
  )
  and a.codeacte=16
  and en_stock>0
  and prix_public/pahtnet<1.2
  ```

## `html/pan/index.php`
- Produits codeacte=16 (pan). #PRODUIT #COMGROIT #comgros
  ```sql
  SELECT a.cip,a.ean13,nom,prix_public,base_rembt, pahtnet, (prix_public / pahtnet) as coeff,en_stock , DTlivraisonreel
  FROM PRODUIT as a
  left join COMGROIT as b on a.cip = b.cip
  left join comgros as c on b.nocomgros = c.nocomgros
  WHERE b.nocomgros = (
    SELECT e.nocomgros
    FROM COMGROIT as e
    left join comgros as f on f.nocomgros = e.nocomgros
    Where a.cip=e.cip
    order by DTlivraisonreel desc
    limit 1
  )
  and a.codeacte=16
  and en_stock>0
  and prix_public/pahtnet<1.2
  ```

## `html/ca_medecin/index.php`
- CA par médecin (date du jour). #ORDERS #MEDECIN
  ```sql
  Select (round(Sum(a.Total_general))) , a.Med_TI, a.Facture, b.No_Ident
  From ORDERS As a
  Left Join MEDECIN As b On b.Code = a.Med_TI
  Where a.Date_order = Date_Format(Now(), '%Y/%m/%d') And b.No_Ident <> ''
  Group By a.Med_TI
  order by (round(Sum(a.Total_general))) desc
  ```

## `html/f_eval/index.php`
- Détail palmarès GPP (EAN13 ciblés). #orders #orditem #produit
  ```sql
  SELECT date_order,Facture, (convert(quantite,char)) as quantite ,nom, Prix_public
  FROM orders as a
  LEFT JOIN orditem as b on a.ti=b.order_ti
  LEFT JOIN produit as c on c.cip=b.cip
  WHERE a.code_subro not in ("RETF")
    and YEAR(date_order) = <année>
    and month(date_order) = <mois>
    and ean13 in (...)
  ```
- Détail palmarès BIG (EAN13 ciblés). #orders #orditem #produit
  ```sql
  SELECT date_order,Facture, (convert(quantite,char)) as quantite ,nom, Prix_public
  FROM orders as a
  LEFT JOIN orditem as b on a.ti=b.order_ti
  LEFT JOIN produit as c on c.cip=b.cip
  WHERE a.code_subro not in ("RETF")
    and YEAR(date_order) = <année>
    and month(date_order) = <mois>
    and ean13 in (...)
  ```
- Détail palmarès Frang (EAN13 ciblés). #orders #orditem #produit
  ```sql
  SELECT date_order,Facture, (convert(quantite,char)) as quantite ,nom, Prix_public
  FROM orders as a
  LEFT JOIN orditem as b on a.ti=b.order_ti
  LEFT JOIN produit as c on c.cip=b.cip
  WHERE a.code_subro not in ("RETF")
    and YEAR(date_order) = <année>
    and month(date_order) = <mois>
    and ean13 in (...)
  ```
- Ratio remboursé vs total sur 6 mois. #ORDERS #ORDITEM #produit
  ```sql
  Select ORDERS.Oper_Code, ORDERS.Date_order, produit.Nom, produit.Code_rembt, ORDITEM.Quantite, ORDITEM.Prix,
         ROUND(SUM(CASE WHEN produit.Code_rembt = 4 THEN ORDITEM.Quantite * ORDITEM.Prix ELSE 0 END),2) AS Somme_rembt_4,
         ROUND(SUM(ORDITEM.Quantite * ORDITEM.Prix),2) AS Somme_total,
         ROUND(SUM(CASE WHEN produit.Code_rembt = 4 THEN ORDITEM.Quantite * ORDITEM.Prix ELSE 0 END) / SUM(ORDITEM.Quantite * ORDITEM.Prix), 2) * 100 AS ratio
  From ORDERS
  Inner Join ORDITEM On ORDITEM.Order_TI = ORDERS.TI
  Inner Join produit On produit.CIP = ORDITEM.CIP
  Where ORDERS.Date_order Between Date_Sub(Now(), Interval 6 Month) And Now()
  GROUP BY ORDERS.Oper_Code
  ```

## `html/maj_prix/action.php`
- Liste des produits par code géo. #produit
  ```sql
  select Nom, En_Stock, Prix_Public, EAN13 from produit where Code_Geo='<codegeo>'
  ```
- Mise à jour du prix public (EAN13). #produit
  ```sql
  update produit set Prix_Public = <prix> where EAN13='<ean13>'
  ```
- Sélection des prix pour mise à jour en masse. #produit
  ```sql
  select Prix_Public, EAN13 from produit where codegeo='<codegeo>'
  ```

## `html/maj_prix/index.php`
- Codes géographiques disponibles. #CODEGEO
  ```sql
  select Code_Geo, Nom_Geo from CODEGEO
  ```

## `html/todo_list/action.php`
- Liste des pharmacies (étape 1). #COMPHARM
  ```sql
  SELECT * FROM COMPHARM WHERE Etape=1
  ```
