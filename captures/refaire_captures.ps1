# Refait les captures 05 (analyses 31 à 33) et 08 (application).
# Lancement depuis TP2611 :  pwsh -File captures\refaire_captures.ps1
Start-Transcript -Path (Join-Path $PSScriptRoot "journal_refaire.txt") -Force | Out-Null
$D = Split-Path $PSScriptRoot -Parent
$C = Join-Path $PSScriptRoot "capture_fenetre.ps1"
$Py = "$D\.venv\Scripts\python.exe"

& $C -Commande "cd '$D\04_Python'; & '$Py' -X utf8 analyses.py | Select-Object -First 40" `
     -Sortie (Join-Path $PSScriptRoot "05_analyses.png") -Lignes 45 -Attente 7

# Saisies lues dans un fichier ; capture_fenetre.ps1 envoie de l'UTF-8 sans caractère invisible (BOM)
$scenario = "Write-Host 'Scenario : commande C004 (P013 x1, P022 x2), puis P004 x10 (refus), puis historique de C004' -ForegroundColor Yellow; " +
            "Get-Content ..\captures\saisies_app.txt | & '$Py' -X utf8 app.py | Where-Object { `$_ -notmatch '^[0-8]\. |=====' }; " +
            "& '$Py' -X utf8 charger_donnees.py | Out-Null"
& $C -Commande "cd '$D\04_Python'; $scenario" `
     -Sortie (Join-Path $PSScriptRoot "08_app_commande.png") -Lignes 40 -Attente 9

Stop-Transcript | Out-Null
