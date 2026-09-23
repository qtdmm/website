<?php
// stats.php - einfache Auswertung. Liegt hinter dem .htaccess-Schutz.
$dbFile = __DIR__ . '/stats.sqlite';
if (!is_readable($dbFile)) {
    exit("<h1>Statistiken</h1><p>Noch keine Daten.</p>");
}
$pdo = new PDO('sqlite:' . $dbFile);
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Zaehlt Abrufe (total) und verschiedene Besucher pro Tag (unique) ab $from.
function counts(PDO $pdo, string $from): array
{
    $stmt = $pdo->prepare(
        "SELECT COUNT(*) AS total, COUNT(DISTINCT ip_hash) AS uniq
           FROM hits WHERE date >= ?");
    $stmt->execute([$from]);
    return $stmt->fetch(PDO::FETCH_ASSOC);
}

$today = counts($pdo, date('Y-m-d'));
$month = counts($pdo, date('Y-m-01'));
$year  = counts($pdo, date('Y-m-01', strtotime('-11 months')));

// Die letzten 30 Tage als Liste.
$days = $pdo->query(
    "SELECT date, COUNT(*) AS total, COUNT(DISTINCT ip_hash) AS uniq
       FROM hits GROUP BY date ORDER BY date DESC LIMIT 30")->fetchAll(PDO::FETCH_ASSOC);

header('Content-Type: text/html; charset=utf-8');
?>
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>qtdmm.de – Statistik</title>
<style>
  body { font-family: system-ui, sans-serif; background: #1d1f22; color: #e8e8e6;
         margin: 0; padding: 32px; }
  h1 { color: #dadc77; font-size: 1.4rem; }
  table { border-collapse: collapse; margin-top: 8px; }
  th, td { padding: 4px 16px 4px 0; text-align: left; border-bottom: 1px solid #35393e; }
  th { color: #9a9d9f; font-weight: 600; }
  td.n { font-variant-numeric: tabular-nums; text-align: right; }
  .big { font-size: 1.6rem; color: #dadc77; font-variant-numeric: tabular-nums; }
</style>
</head>
<body>
<h1>Statistik qtdmm.de</h1>
<table>
  <tr><th>Zeitraum</th><th>Besucher</th><th>Abrufe</th></tr>
<?php foreach ([["Heute", $today], ["Dieser Monat", $month], ["Letzte 12 Monate", $year]] as [$label, $c]): ?>
  <tr><td><?= $label ?></td>
      <td class="n big"><?= (int) $c['uniq'] ?></td>
      <td class="n"><?= (int) $c['total'] ?></td></tr>
<?php endforeach; ?>
</table>

<h1>Letzte 30 Tage</h1>
<table>
  <tr><th>Tag</th><th>Besucher</th><th>Abrufe</th></tr>
<?php foreach ($days as $d): ?>
  <tr><td><?= htmlspecialchars($d['date']) ?></td>
      <td class="n"><?= (int) $d['uniq'] ?></td>
      <td class="n"><?= (int) $d['total'] ?></td></tr>
<?php endforeach; ?>
</table>
<p style="color:#9a9d9f">„Besucher" sind verschiedene IP-Hashes pro Tag, „Abrufe" alle Seitenaufrufe.</p>
</body>
</html>
