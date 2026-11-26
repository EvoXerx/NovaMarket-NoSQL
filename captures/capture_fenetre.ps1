param(
    [string]$Commande,      # commande PowerShell (ou argument du programme si -Exe)
    [string]$Sortie,        # chemin du PNG
    [int]$Attente = 6,
    [int]$Lignes = 45,
    [string]$Exe = ""       # si fourni : lance ce programme (ex. Compass) au lieu d'un terminal
)
Add-Type -AssemblyName System.Drawing, System.Windows.Forms

if ($Exe -ne "") {
    $p = Start-Process -FilePath $Exe -ArgumentList $Commande -WindowStyle Maximized -PassThru
} else {
    # UTF-8 : sinon les accents de la sortie Python s'affichent mal
    $cmd = "mode con: cols=150 lines=$Lignes; [Console]::OutputEncoding = [Text.Encoding]::UTF8; " +
           "`$OutputEncoding = New-Object Text.UTF8Encoding `$false; " + $Commande
    $enc = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($cmd))
    $p = Start-Process -FilePath "powershell.exe" `
        -ArgumentList "-NoExit -NoProfile -ExecutionPolicy Bypass -EncodedCommand $enc" `
        -WindowStyle Maximized -PassThru
}
Start-Sleep -Seconds $Attente

# Capture de tout l'écran principal
$zone = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap $zone.Width, $zone.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($zone.Left, $zone.Top, 0, 0, $bmp.Size)
$bmp.Save($Sortie, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()

if ($Exe -eq "") { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
Write-Output "OK $Sortie"
