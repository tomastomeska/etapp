<?php
/**
 * Generátor českých státních svátků do roku 2035
 * Generuje JSON soubor s českými svátky
 */

function generateCzechHolidays() {
    $holidays = [];
    
    for ($year = 2024; $year <= 2035; $year++) {
        // Pevné svátky
        $fixedHolidays = [
            "$year-01-01" => "Nový rok / Den obnovy samostatného českého státu",
            "$year-05-01" => "Svátek práce",
            "$year-05-08" => "Den vítězství",
            "$year-07-05" => "Den slovanských věrozvěstů Cyrila a Metoděje",
            "$year-07-06" => "Den upálení mistra Jana Husa",
            "$year-09-28" => "Den české státnosti",
            "$year-10-28" => "Den vzniku samostatného československého státu",
            "$year-11-17" => "Den boje za svobodu a demokracii",
            "$year-12-24" => "Štědrý den",
            "$year-12-25" => "1. svátek vánoční",
            "$year-12-26" => "2. svátek vánoční",
        ];
        
        // Velikonoční svátky (pohyblivé)
        $easter = getEasterDate($year);
        
        // Velikonoční pondělí (pondělí po Velikonocích)
        $easterMonday = date('Y-m-d', strtotime($easter . ' +1 day'));
        $fixedHolidays[$easterMonday] = "Velikonoční pondělí";
        
        // Velký pátek (pátek před Velikonocemi) - od 2016 státní svátek
        $goodFriday = date('Y-m-d', strtotime($easter . ' -2 days'));
        $fixedHolidays[$goodFriday] = "Velký pátek";
        
        $holidays = array_merge($holidays, $fixedHolidays);
    }
    
    ksort($holidays);
    return $holidays;
}

/**
 * Výpočet data Velikonoc podle Gaussova algoritmu
 */
function getEasterDate($year) {
    $a = $year % 19;
    $b = intval($year / 100);
    $c = $year % 100;
    $d = intval($b / 4);
    $e = $b % 4;
    $f = intval(($b + 8) / 25);
    $g = intval(($b - $f + 1) / 3);
    $h = (19 * $a + $b - $d - $g + 15) % 30;
    $i = intval($c / 4);
    $k = $c % 4;
    $l = (32 + 2 * $e + 2 * $i - $h - $k) % 7;
    $m = intval(($a + 11 * $h + 22 * $l) / 451);
    $month = intval(($h + $l - 7 * $m + 114) / 31);
    $day = (($h + $l - 7 * $m + 114) % 31) + 1;
    
    return sprintf('%04d-%02d-%02d', $year, $month, $day);
}

// Generování a uložení
$holidays = generateCzechHolidays();

$dataDir = __DIR__ . '/data';
if (!is_dir($dataDir)) {
    mkdir($dataDir, 0777, true);
}

$holidaysFile = $dataDir . '/czech_holidays.json';
file_put_contents($holidaysFile, json_encode($holidays, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));

echo "✓ Vygenerováno " . count($holidays) . " svátků do roku 2035\n";
echo "✓ Uloženo do: $holidaysFile\n";
