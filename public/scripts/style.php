<?php
// style.php - minimalistischer Visitor-Tracker mit SQLite.
// Wird von jeder Seite als Stylesheet eingebunden (siehe src/page.sh) und
// liefert leeres CSS zurueck; gezaehlt wird der Abruf selbst.
$statsDir = __DIR__ . '/../conf';
$dbFile   = $statsDir . '/stats.sqlite';

// Antwort zuerst: leeres CSS, und niemals aus dem Cache - sonst zaehlt ein
// wiederkehrender Besucher nur beim ersten Mal.
header('Content-Type: text/css; charset=utf-8');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Pragma: no-cache');
print("/* qtdmm.de */\n");

// Ab hier nur noch zaehlen; Fehler duerfen die Seite nicht stoeren.
ignore_user_abort(true);
if (function_exists('fastcgi_finish_request')) {
    fastcgi_finish_request();
}

try {
    $pdo = new PDO('sqlite:' . $dbFile);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    $pdo->exec("
CREATE TABLE IF NOT EXISTS hits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,           -- YYYY-MM-DD
    ip_hash TEXT NOT NULL,        -- gehashte IP + Datum + Salt, unique pro Tag
    timestamp INTEGER NOT NULL    -- Unix-Timestamp
)
");
    $pdo->exec("CREATE INDEX IF NOT EXISTS hits_date ON hits (date)");

    // Geheimer Salt, damit aus dem Hash keine IP zurueckgerechnet werden kann
    // (IPv4 sind nur 4 Mrd. Moeglichkeiten - ohne Salt in Sekunden durch).
    // Liegt nicht im Repository, wird beim ersten Aufruf angelegt.
    $saltFile = $statsDir . '/salt.txt';
    if (!is_readable($saltFile)) {
        file_put_contents($saltFile, bin2hex(random_bytes(32)), LOCK_EX);
        @chmod($saltFile, 0600);
    }
    $salt = trim(file_get_contents($saltFile));

    $date = date('Y-m-d');
    $ip   = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
    $ipHash = hash('sha256', $salt . $ip . $date);

    $stmt = $pdo->prepare("INSERT INTO hits (date, ip_hash, timestamp) VALUES (?, ?, ?)");
    $stmt->execute([$date, $ipHash, time()]);

    // Aufbewahrung 12 Monate, so wie in der Datenschutzerklaerung angegeben.
    // Gelegentlich statt bei jedem Aufruf - das reicht voellig.
    if (random_int(1, 500) === 1) {
        $stmt = $pdo->prepare("DELETE FROM hits WHERE date < ?");
        $stmt->execute([date('Y-m-d', strtotime('-12 months'))]);
    }
} catch (Throwable $e) {
    // Statistik ist nie wichtig genug, um irgendetwas kaputtzumachen.
}
