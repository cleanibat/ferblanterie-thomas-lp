<?php
// Formulaire de devis — variante PHP (hébergement o2switch/cPanel). Voir references/forms-leads.md
header('Content-Type: application/json');
date_default_timezone_set('Europe/Paris');

$DEST     = 'contact@ferblanterie-thomas.fr';                            // destinataire visible : le client
$BCC      = 'aymeric@cleanibat.fr';                         // Aymeric toujours en copie CACHÉE, jamais en destinataire visible
$FROM     = 'La Ferblanterie de Thomas <no-reply@cleanibat.fr>';               // domaine avec SPF+DKIM valides, sinon Gmail supprime en silence
$SUBJECT  = 'Nouveau devis La Ferblanterie de Thomas - ';
$CSV      = dirname($_SERVER['DOCUMENT_ROOT']) . '/leads_ferblanterie-thomas.csv';  // hors docroot : filet de sécurité
$THANKS   = 'merci.html';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo json_encode(['success'=>false]); exit; }
if (!empty($_POST['_honey'])) { echo json_encode(['success'=>true]); exit; }

function v($keys){ foreach((array)$keys as $k){ if(isset($_POST[$k]) && trim($_POST[$k])!=='') return trim(strip_tags($_POST[$k])); } return ''; }
$nom=v(['Nom','nom','name']); $tel=v(['Téléphone','telephone','tel','phone']); $email=v(['Email','email']);
$ville=v(['Localité','ville','city']); $besoin=v(['Besoin','besoin','need']); $msg=v(['Message','message']); $src=v(['Source']);
if ($nom==='' || !filter_var($email, FILTER_VALIDATE_EMAIL)) { http_response_code(400); echo json_encode(['success'=>false,'message'=>'Données invalides.']); exit; }

// 1) Sauvegarde locale AVANT l'envoi
$fh=@fopen($CSV,'a');
if($fh){ if(filesize($CSV)===0) fputcsv($fh,['date','nom','telephone','email','localite','besoin','message','source','ip'],';');
  fputcsv($fh,[date('Y-m-d H:i:s'),$nom,$tel,$email,$ville,$besoin,str_replace(["\r","\n"],' ',$msg),$src,$_SERVER['REMOTE_ADDR']??''],';'); fclose($fh); @chmod($CSV,0600); }

// 2) E-mail
$body="Nouvelle demande de devis\n\nNom       : $nom\nTéléphone : $tel\nEmail     : $email\nLocalité  : $ville\nBesoin    : $besoin\nSource    : $src\n\nMessage :\n$msg\n";
$headers="From: $FROM\r\nReply-To: $email\r\nBcc: $BCC\r\nContent-Type: text/plain; charset=UTF-8\r\nX-Mailer: PHP/".phpversion();
@mail($DEST, $SUBJECT.$nom, $body, $headers);

// 3) Réponse : redirection (formulaire classique) ou JSON (fetch)
if (empty($_SERVER['HTTP_X_REQUESTED_WITH'])) { header('Location: '.$THANKS.'?lp='.urlencode($src)); exit; }
echo json_encode(['success'=>true]);
