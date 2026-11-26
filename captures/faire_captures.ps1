# Fait les captures d'écran du terminal (vraies fenêtres PowerShell) et de Compass.
# Lancement depuis TP2611 :  pwsh -File captures\faire_captures.ps1
Start-Transcript -Path (Join-Path $PSScriptRoot "journal.txt") -Force | Out-Null
$ErrorActionPreference = "Continue"
$D = Split-Path $PSScriptRoot -Parent
$C = Join-Path $PSScriptRoot "capture_fenetre.ps1"
$Py = "'$D\.venv\Scripts\python.exe' -X utf8"

function Capturer($nom, $commande, $lignes = 45, $attente = 7) {
    & $C -Commande "cd '$D'; $commande" -Sortie (Join-Path $PSScriptRoot $nom) -Lignes $lignes -Attente $attente
}

Capturer "01_installation.png" "& $Py -m pip show pymongo; Get-Service MongoDB | Format-Table -AutoSize; & 'C:\Program Files\MongoDB\Server\9.0\bin\mongod.exe' --version | Select-Object -First 3" 30
Capturer "02_librairie.png" "& $Py tp_librairie.py | Select-Object -Last 40" 48
Capturer "03_chargement.png" "cd 04_Python; & $Py charger_donnees.py" 20
Capturer "04_mongosh_requetes.png" "& '.\.tools\node_modules\.bin\mongosh.cmd' --quiet --file 03_Mongosh\requetes.js | Select-Object -Last 45; cd 04_Python; & $Py charger_donnees.py | Out-Null" 50 12
Capturer "05_analyses.png" "cd 04_Python; & $Py analyses.py | Select-Object -First 40" 45
Capturer "06_analyses_suite.png" "cd 04_Python; & $Py analyses.py | Select-Object -Skip 30" 45
Capturer "07_tests.png" "cd 04_Python; & $Py tests.py" 40 10
# Application : une commande valide puis un refus, puis remise à zéro
Capturer "08_app_commande.png" "cd 04_Python; '5','C004','P013','1','P022','2','','5','C004','P004','10','','0' | & $Py app.py | Select-Object -Skip 12; & $Py charger_donnees.py | Out-Null" 45 9

# Compass connecté au serveur local (liste des bases)
& $C -Exe "C:\Program Files\MongoDB Compass\MongoDBCompass.exe" -Commande "mongodb://localhost:27017/" -Sortie (Join-Path $PSScriptRoot "09_compass.png") -Attente 15
Write-Output "Captures enregistrées dans $PSScriptRoot"
Stop-Transcript | Out-Null
