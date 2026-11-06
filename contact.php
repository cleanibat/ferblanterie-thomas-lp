<?php
// Formulaire de devis — formulaire HTML classique traité ici (hébergement IONOS). Voir references/forms-leads.md du skill.
header('Content-Type: application/json');
date_default_timezone_set('Europe/Paris');

$DEST     = 'aymeric@cleanibat.fr';                         // À REMPLACER par l'adresse de Thomas (inconnue au 06/11/2026)
$BCC      = 'aymeric@cleanibat.fr';                         // Aymeric toujours en copie CACHÉE, jamais en destinataire visible
$SENDER   = 'no-reply@laferblanteriedethomas.com';          // domaine du contrat IONOS (SPF : include:_spf-eu.ionos.com)
$FROM     = 'La Ferblanterie de Thomas <' . $SENDER . '>';
$SUBJECT  = 'Nouvelle demande de devis - ';
$PRIV     = dirname($_SERVER['DOCUMENT_ROOT']) . '/prive_ferblanterie';  // hors docroot : filet de sécurité + config
$CSV      = $PRIV . '/leads_ferblanterie-thomas.csv';
$THANKS   = 'merci.html';

// ?test=1 : envoi à Aymeric uniquement, pour vérifier la chaîne sans déranger le client
if (isset($_GET['test'])) { $DEST = $BCC; $BCC = ''; }
if ($DEST === $BCC) $BCC = '';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo json_encode(['success'=>false]); exit; }
if (!empty($_POST['_honey'])) { echo json_encode(['success'=>true]); exit; }

function v($keys){ foreach((array)$keys as $k){ if(isset($_POST[$k]) && trim($_POST[$k])!=='') return trim(strip_tags($_POST[$k])); } return ''; }
function oneline($s){ return str_replace(["\r","\n"], ' ', $s); }
$nom=v(['Nom','nom','name']); $tel=v(['Téléphone','telephone','tel','phone']); $email=v(['Email','email']);
$ville=v(['Localité','ville','city']); $besoin=v(['Besoin','besoin','need']); $msg=v(['Message','message']); $src=v(['Source']);
if ($nom==='' || !filter_var($email, FILTER_VALIDATE_EMAIL)) { http_response_code(400); echo json_encode(['success'=>false,'message'=>'Données invalides.']); exit; }

// Origine du lead (champs cachés remplis par main.js, modèle « dernier clic non direct » sur 90 jours)
$A = [];
foreach (['gclid','gbraid','wbraid','fbclid','msclkid','utm_source','utm_medium','utm_campaign','utm_term','utm_content','referrer','landing_page'] as $k) $A[$k] = substr(v([$k]), 0, 300);
$us = strtolower($A['utm_source']); $um = strtolower($A['utm_medium']);
$refHost = $A['referrer'] !== '' ? strtolower((string)parse_url($A['referrer'], PHP_URL_HOST)) : '';
$moteurs = ['google','bing','qwant','duckduckgo','ecosia','yahoo','yandex','startpage','lilo','brave','baidu','ask'];
$moteur = '';
foreach ($moteurs as $m) { if ($refHost !== '' && preg_match('/(^|\.)'.$m.'\./', $refHost)) { $moteur = $m; break; } }
$page = $A['landing_page'] !== '' ? $A['landing_page'] : '?';
if ($A['gclid'] !== '' || $A['gbraid'] !== '' || $A['wbraid'] !== '' || ($us === 'google' && in_array($um, ['cpc','ppc','paid','paid_search','sea']))) {
  $origine = 'Google Ads';
  $id = $A['gclid'] !== '' ? 'gclid:'.$A['gclid'] : ($A['gbraid'] !== '' ? 'gbraid:'.$A['gbraid'] : ($A['wbraid'] !== '' ? 'wbraid:'.$A['wbraid'] : 'utm'));
  $detail = trim(($A['utm_campaign'] !== '' ? $A['utm_campaign'].' · ' : '').$id);
} elseif ($A['fbclid'] !== '' || in_array($us, ['facebook','fb','instagram','ig','meta'])) {
  $origine = 'Meta Ads'; $detail = $A['utm_campaign'] !== '' ? $A['utm_campaign'] : 'fbclid';
} elseif ($moteur !== '' && $A['utm_source'] === '' && $A['msclkid'] === '') {
  $origine = 'SEO'; $detail = 'recherche '.$refHost;
} elseif ($A['msclkid'] !== '' || $A['utm_source'] !== '') {
  $origine = 'Autre'; $detail = $A['msclkid'] !== '' ? 'Microsoft Ads' : 'utm '.$A['utm_source'].'/'.$A['utm_medium'];
} elseif ($refHost !== '') {
  $origine = 'Autre'; $detail = 'lien depuis '.$refHost;
} else {
  $origine = 'Site'; $detail = 'accès direct';
}
$campagne = $src.' · '.$detail.' · arrivée '.$page;

// 1) Sauvegarde locale AVANT l'envoi (dossier privé hors docroot, interdit au web)
if (!is_dir($PRIV)) { @mkdir($PRIV, 0700, true); @file_put_contents($PRIV.'/.htaccess', "Require all denied\nDeny from all\n"); }
$new = !file_exists($CSV) || filesize($CSV) === 0;
$fh=@fopen($CSV,'a');
if($fh){ if($new) fputcsv($fh,array_merge(['date','nom','telephone','email','localite','besoin','message','formulaire','origine','detail'],array_keys($A),['ip']),';');
  fputcsv($fh,array_merge([date('Y-m-d H:i:s'),$nom,$tel,$email,$ville,$besoin,oneline($msg),$src,$origine,$detail],array_values($A),[$_SERVER['REMOTE_ADDR']??'']),';'); fclose($fh); @chmod($CSV,0600); }

// 1 bis) Envoi au CRM via Make, si configuré. Configuration hors docroot, jamais dans le dépôt.
$cfg = @json_decode(@file_get_contents($PRIV . '/agence.json'), true);
if (is_array($cfg) && !empty($cfg['make_url']) && function_exists('curl_init')) {
  $lead = ['client'=>$cfg['client']??'', 'cle'=>$cfg['cle']??'', 'nom'=>$nom, 'telephone'=>$tel, 'email'=>$email, 'localite'=>$ville, 'besoin'=>$besoin,
    'message'=>oneline($msg), 'source'=>$origine, 'campagne'=>$campagne, 'gclid'=>$A['gclid'], 'id'=>'site-'.date('YmdHis').'-'.substr(md5($email.$tel),0,6)];
  $ch = curl_init($cfg['make_url']);
  curl_setopt_array($ch, [CURLOPT_POST=>true, CURLOPT_RETURNTRANSFER=>true, CURLOPT_CONNECTTIMEOUT=>2, CURLOPT_TIMEOUT=>4,
    CURLOPT_HTTPHEADER=>['Content-Type: application/json'], CURLOPT_POSTFIELDS=>json_encode($lead)]);
  @curl_exec($ch); @curl_close($ch);
}

// 2) E-mail (expéditeur d'enveloppe aligné sur le domaine pour le SPF IONOS)
$body="Nouvelle demande de devis\n\nNom       : $nom\nTéléphone : $tel\nEmail     : $email\nCommune   : $ville\nBesoin    : $besoin\nPage      : $src\n\nMessage :\n$msg\n\n--\nOrigine   : $origine ($detail)\nArrivée   : $page\n".($A['referrer']!=='' ? "Référent  : {$A['referrer']}\n" : '');
$headers="From: $FROM\r\nReply-To: ".oneline($email)."\r\n".($BCC!=='' ? "Bcc: $BCC\r\n" : '')."MIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: 8bit";
$subject = '=?UTF-8?B?'.base64_encode($SUBJECT.$origine.' - '.($src!=='' ? $src.' - ' : '').oneline($nom)).'?=';
@mail($DEST, $subject, $body, $headers, '-f'.$SENDER);

// 3) Réponse : redirection (formulaire classique) ou JSON (fetch)
if (empty($_SERVER['HTTP_X_REQUESTED_WITH'])) { header('Location: '.$THANKS.'?lp='.urlencode($src), true, 303); exit; }
echo json_encode(['success'=>true]);
