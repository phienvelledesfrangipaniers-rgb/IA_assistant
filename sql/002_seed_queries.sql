INSERT INTO catalog.saved_queries (name, description, tags, sql_text, source)
VALUES
  (
    'cron_ca_mensuel_pharmar',
    'CA mensuel du grossiste Pharmar sur l’année/mois courant.',
    ARRAY['COMGROS','FOURNIS'],
    $$SELECT round(sum(montantTTCrecu)) as ca
FROM COMGROS as a
left join FOURNIS as c on a.code_fourn=c.code
where year(FROM_UNIXTIME(DTime_Send)) = year(now())
  and month(FROM_UNIXTIME(DTime_Send)) = month(now())
  and c.nom = "pharmar"$$,
    'cron.php'
  ),
  (
    'cron_sync_stock_prix_ean13',
    'TVA, stock et prix pour une liste d’EAN13 afin de synchroniser le stock/prix.',
    ARRAY['produit','COMGROIT','comgros'],
    $$select TVA,ean13,convert(en_stock,char) as en_stock,prix_public,pahtnet
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
and ean13 in (...)$$,
    'cron.php'
  ),
  (
    'cron_homeo_doses',
    'Liste des produits homéo (doses) pour synchronisation.',
    ARRAY['produit'],
    $$SELECT nom,ean13 FROM produit WHERE nom like '%CH DO GL BOI' order by nom desc$$,
    'cron.php'
  ),
  (
    'cron_homeo_tubes',
    'Liste des produits homéo (tubes) pour synchronisation.',
    ARRAY['produit'],
    $$SELECT nom,ean13 FROM produit WHERE nom like '%CH TG BOI' order by nom desc$$,
    'cron.php'
  ),
  (
    'cron_ventes_operateur_total',
    'Totaux de ventes par opérateur (toutes ventes).',
    ARRAY['orders','orditem','produit'],
    $$SELECT oper_code,sum(convert(quantite,char)) as quantite
FROM orders as a
LEFT JOIN orditem as b on a.ti=b.order_ti
LEFT JOIN produit as c on c.cip=b.cip
WHERE a.code_subro not in ("RETF")
  and YEAR(date_order) = <année>
  and month(date_order) = <mois>
group by oper_code$$,
    'cron.php'
  ),
  (
    'cron_ventes_operateur_rembt4',
    'Totaux de ventes par opérateur (remboursement code 4).',
    ARRAY['orders','orditem','produit'],
    $$SELECT oper_code,sum(convert(quantite,char)) as quantite
FROM orders as a
LEFT JOIN orditem as b on a.ti=b.order_ti
LEFT JOIN produit as c on c.cip=b.cip
WHERE a.code_subro not in ("RETF")
  and a.Code_rembt = 4
  and YEAR(date_order) = <année>
  and month(date_order) = <mois>
group by oper_code$$,
    'cron.php'
  ),
  (
    'cron_ventes_operateur_ean13',
    'Totaux de ventes par opérateur sur une liste d’EAN13.',
    ARRAY['orders','orditem','produit'],
    $$SELECT oper_code,sum(convert(quantite,char)) as quantite
FROM orders as a
LEFT JOIN orditem as b on a.ti=b.order_ti
LEFT JOIN produit as c on c.cip=b.cip
WHERE a.code_subro not in ("RETF")
  and YEAR(date_order) = <année>
  and month(date_order) = <mois>
  and ean13 in (...)
group by oper_code$$,
    'cron.php'
  ),
  (
    'cron_ca_journalier_history',
    'CA journalier pour une date donnée.',
    ARRAY['HISTORY'],
    $$SELECT EspeceEUR, ChequeEUR, CB, (Centre+Mutuelle) as medoc, Virement,
       (Differe_positif+EnCompte_positif+EnCompte_Negatif+Differe_Negatif) as encompte,
       nb_De_Factures, (Marge_Rembt+Marge_NRembt) as marge
FROM HISTORY
WHERE date = "<YYYY-MM-DD>"$$,
    'cron.php'
  ),
  (
    'cron_history_gpp',
    'Historique CA GPP sur période (statistiques).',
    ARRAY['HISTORY'],
    $$SELECT DATE_FORMAT(date,"%Y-%m-%d") as date,(EspeceEUR) as esp_gpp,(ChequeEUR) as cheque_gpp,(CB) as cb_gpp,
       ((Centre+Mutuelle)) as secu_gpp,((Differe_positif+EnCompte_positif+EnCompte_Negatif+EnCompte_Positif)) as encompte_gpp,
       (nb_De_Factures) as client_gpp,((Marge_Rembt+Marge_NRembt)) as marge_gpp,
       (EspeceEUR+ChequeEUR+CB+Centre+Mutuelle+Differe_positif+EnCompte_Positif+Differe_Negatif+EnCompte_Negatif+Virement) as ca_gpp
FROM HISTORY
WHERE date BETWEEN ("2013-07-25") AND ("<YYYY-MM-DD>")$$,
    'cron.php'
  ),
  (
    'cron_history_frang',
    'Historique CA Frang sur période (statistiques).',
    ARRAY['HISTORY'],
    $$SELECT DATE_FORMAT(date,"%Y-%m-%d") as date,(EspeceEUR) as esp_frang,(ChequeEUR) as cheque_frang,(CB) as cb_frang,
       ((Centre+Mutuelle)) as secu_frang,((Differe_positif+EnCompte_positif+EnCompte_Negatif+EnCompte_Positif)) as encompte_frang,
       convert(nb_De_Factures,char) as client_frang,((Marge_Rembt+Marge_NRembt)) as marge_frang,
       (EspeceEUR+ChequeEUR+CB+Centre+Mutuelle+Differe_positif+Differe_Negatif+EnCompte_Negatif+EnCompte_Positif+Virement) as ca_frang
FROM HISTORY
WHERE date BETWEEN ("2013-07-25") AND ("<YYYY-MM-DD>")$$,
    'cron.php'
  ),
  (
    'cron_ca_web',
    'CA web journalier (règlement type "w").',
    ARRAY['REGORD','ORDERS'],
    $$Select Date_Format(ORDERS.Date_order, "%Y-%m-%d") As order_date,Sum((ORDERS.Total_general)) As web
From REGORD
Left Join ORDERS On REGORD.Order_TI = ORDERS.TI
Where REGORD.RegleType = "w"
  and Date_Format(ORDERS.Date_order, "%Y-%m-%d") BETWEEN ("2013-07-25") AND ("<YYYY-MM-DD>")
Group By Date_Format(ORDERS.Date_order, "%Y-%m-%d")$$,
    'cron.php'
  ),
  (
    'cron_export_produit_count',
    'Export par lots: compter les produits.',
    ARRAY['produit'],
    $$SELECT count(*) as total FROM produit$$,
    'cron.php'
  ),
  (
    'cron_export_produit_page',
    'Export par lots: page de produits.',
    ARRAY['produit'],
    $$SELECT * FROM produit limit <offset>,10000$$,
    'cron.php'
  ),
  (
    'cron_diff_prix',
    'Extraction pour comparaison de prix (diff_prix).',
    ARRAY['PRODUIT','COMGROIT','comgros'],
    $$SELECT a.cip as cip,a.ean13 as ean13,nom,prix_public,base_rembt, b.pahtnet as pahtnet,
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
and en_stock>0$$,
    'cron.php'
  ),
  (
    'bd_win_promo_operateur',
    'Ventes promo par opérateur sur des EAN13 ciblés.',
    ARRAY['orders','orditem','produit'],
    $$SELECT oper_code,sum(convert(quantite,char)) as quantite
FROM orders as a
LEFT JOIN orditem as b on a.ti=b.order_ti
LEFT JOIN produit as c on c.cip=b.cip
WHERE ean13 in ("3664798027419","3664798028195","3664798027914","3664798027556")
  and YEAR(date_order) = <année>
  and month(date_order) = <mois>
group by facture$$,
    'class/bd_win.php'
  ),
  (
    'bd_win_palmares_operateur',
    'Palmares par opérateur (code subro/rembt/ean13 filtre).',
    ARRAY['orders','orditem','produit'],
    $$SELECT oper_code,sum(convert(quantite,char)) as quantite
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
group by Facture$$,
    'class/bd_win.php'
  ),
  (
    'bd_win_palmares_detail',
    'Détail palmarès avec quantités, nom, prix.',
    ARRAY['orders','orditem','produit'],
    $$SELECT date_order,Facture, sum(convert(quantite,char)) as quantite ,nom, Prix_public
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
group by nom$$,
    'class/bd_win.php'
  ),
  (
    'bd_win_promotions_actives',
    'Liste des promotions actives.',
    ARRAY['PROMO','PROMITEM','produit'],
    $$SELECT *
FROM PROMO as a
left join PROMITEM as b on a.TI=b.HeaderTI
left join produit as c on b.itemti=c.cip
where a.nom not like '%@%'
  and a.Flags & 0x2 = 2
order by a.ti desc$$,
    'class/bd_win.php'
  ),
  (
    'bd_win_ca_grossistes',
    'CA grossistes (soredip/sipr/pharmar).',
    ARRAY['COMGROS','FOURNIS'],
    $$SELECT c.nom as fourn,year(FROM_UNIXTIME(DTime_Send)) as year,month(FROM_UNIXTIME(DTime_Send)) as month,
       round(sum(montantTTCrecu)) as ca
FROM COMGROS as a
left join FOURNIS as c on a.code_fourn=c.code
where year(FROM_UNIXTIME(DTime_Send)) IN (2022)
  and c.nom in ('soredip','sipr','pharmar')
group by month(FROM_UNIXTIME(DTime_Send)),code_fourn
order by year(FROM_UNIXTIME(DTime_Send)),month(FROM_UNIXTIME(DTime_Send)),round(sum(montantTTCrecu)) desc$$,
    'class/bd_win.php'
  ),
  (
    'bd_win_fournisseurs_actifs',
    'Fournisseurs actifs (commandes).',
    ARRAY['fournis'],
    $$select * from fournis where flags & 0x64<>64 and flags & 0x8<>8$$,
    'class/bd_win.php'
  ),
  (
    'html_stock_faible',
    'Produits à stock faible avec moyenne et délai réappro.',
    ARRAY['produit','stprod','COMHISTO','comgros','fournis'],
    $$Select produit.CIP, produit.Nom, produit.EAN13, produit.Dernier_Vente,
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
group by COMHISTO.NoComGros$$,
    'html/stock_faible/index.php'
  ),
  (
    'html_palmares_search_ean13',
    'Recherche produit par EAN13 (palmarès).',
    ARRAY['produit'],
    $$SELECT Nom,ean13,en_stock FROM produit WHERE ean13="<search>" order by nom desc$$,
    'html/palmares/action.php'
  ),
  (
    'html_palmares_search_nom',
    'Recherche produit par nom (palmarès).',
    ARRAY['produit'],
    $$SELECT Nom,ean13,en_stock FROM produit WHERE Nom like ("%<search>%") and en_stock>0 order by nom desc$$,
    'html/palmares/action.php'
  ),
  (
    'html_plan_livraison_facture',
    'Récupération du Cli_TI à partir d’une facture.',
    ARRAY['ORDERS'],
    $$Select ORDERS.Facture, ORDERS.Cli_TI From ORDERS Where ORDERS.Facture = '<facture>'$$,
    'html/plan_livraison/action.php'
  ),
  (
    'html_plan_livraison_historique_client',
    'Historique des achats d’un client (Cli_TI).',
    ARRAY['ORDERS','ORDITEM','produit'],
    $$Select ORDERS.Facture, ORDERS.Cli_TI, ORDITEM.CIP, ORDITEM.Quantite, produit.Nom, ORDERS.Date_order
From ORDERS
Inner Join ORDITEM On ORDITEM.Order_TI = ORDERS.TI
Inner Join produit On produit.CIP = ORDITEM.CIP
Where ORDERS.Cli_TI = '<cli_ti>'
Order By ORDERS.Facture DESC, ORDERS.Date_order DESC$$,
    'html/plan_livraison/action.php'
  ),
  (
    'html_injection_produit_monographie',
    'Monographie produit (texte via MQ_memo/BLOBS).',
    ARRAY['produit','MQ_form','MQ_monog','MQ_memo','BLOBS'],
    $$Select a.cip,ean13,a.nom,liste,Gross,allait,
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
WHERE ean13 = <ean13>$$,
    'html/injection_produit/action.php'
  ),
  (
    'html_injection_produit_alertes',
    'Alertes associées à un CIP.',
    ARRAY['MQ_ALERT','mq_commn'],
    $$SELECT Str
FROM MQ_ALERT as a
left join mq_commn as b on a.codsp=b.keyval
where a.cip = <cip>$$,
    'html/injection_produit/action.php'
  ),
  (
    'html_ca_medecin',
    'CA par médecin (date du jour).',
    ARRAY['ORDERS','MEDECIN'],
    $$Select (round(Sum(a.Total_general))) , a.Med_TI, a.Facture, b.No_Ident
From ORDERS As a
Left Join MEDECIN As b On b.Code = a.Med_TI
Where a.Date_order = Date_Format(Now(), '%Y/%m/%d') And b.No_Ident <> ''
Group By a.Med_TI
order by (round(Sum(a.Total_general))) desc$$,
    'html/ca_medecin/index.php'
  ),
  (
    'html_todo_list_pharmacies',
    'Liste des pharmacies (étape 1).',
    ARRAY['COMPHARM'],
    $$SELECT * FROM COMPHARM WHERE Etape=1$$,
    'html/todo_list/action.php'
  );
