###
# Variables can be adjusted
##
$mfHelperPath="c:\migrations"
$tmpPath="c:\tmp"
$pythonUri="https://www.python.org/ftp/python/3.7.9/python-3.7.9-amd64.exe"
$pythonModulesToInstall = @("requests", "paramiko", "boto3")
$mfHelperScriptsUri="https://github.com/awslabs/aws-cloudendure-migration-factory-solution/raw/master/source/automation-scripts.zip"
##

function Unzip($zipfile, $outdir)
{
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [System.IO.Compression.ZipFile]::OpenRead($zipfile)
    foreach ($entry in $archive.Entries)
    {
        $entryTargetFilePath = [System.IO.Path]::Combine($outdir, $entry.FullName)
        $entryDir = [System.IO.Path]::GetDirectoryName($entryTargetFilePath)
        
        #Ensure the directory of the archive entry exists
        if(!(Test-Path $entryDir )){
            New-Item -ItemType Directory -Path $entryDir | Out-Null 
        }
        
        #If the entry is not a directory entry, then extract entry
        if(!$entryTargetFilePath.EndsWith("\")){
            [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $entryTargetFilePath, $true);
        }
    }
}


Write-Output "Starting install of MigrationFactory Helper Scripts"
Write-Output "...Check if $tmpPath exists"
If(!(test-path $tmpPath))
{
     New-Item -ItemType Directory -Force -Path $tmpPath
}
Write-Output "...Check if $mfHelperPath exists"
If(!(test-path $mfHelperPath) -Or !(test-path $mfHelperPath\downloads) -Or !(test-path $mfHelperPath\scripts))
{
      New-Item -ItemType Directory -Force -Path $mfHelperPath
      New-Item -ItemType Directory -Force -Path $mfHelperPath\downloads
      New-Item -ItemType Directory -Force -Path $mfHelperPath\scripts
}

Write-Output "...Downloading $pythonUri to folder $mfHelperPath\downloads"
#[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
(New-Object System.Net.WebClient).DownloadFile($pythonUri, "$mfHelperPath\downloads\" + "python_installer.exe")
Write-Output "...Downloading $mfHelperScriptsUri to folder $mfHelperPath\downloads"
(New-Object System.Net.WebClient).DownloadFile($mfHelperScriptsUri, "$mfHelperPath\downloads\" + "automation-scripts.zip")
Unzip $mfHelperPath\downloads\automation-scripts.zip "$mfHelperPath\scripts\"
Write-Output "...Installing python"
if ((Get-Command "python" -ErrorAction SilentlyContinue) -eq $null)
{
    $Process=Start-Process  -Wait  -FilePath "$mfHelperPath\downloads\python_installer.exe" -ArgumentList "/passive /log $tmpPath\python-install.txt  InstallAllUsers=1 PrependPath=1 Include_test=0 " -RedirectStandardError $tmpPath\python-install-err.txt -RedirectStandardOutput $tmpPath\python-install-out.txt 
    Write-Output "...Reloading Path"
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User") 
}
else 
{
    $pythonVersion = (&{python -V})
    Write-Output "...Python already installed on version $pythonVersion"
}
Write-Output "...Upgrading pip and install modules"
Start-Process  -Wait  -FilePath "python" -ArgumentList "-m pip install --upgrade pip"
foreach ($m in $pythonModulesToInstall) {
	Start-Process  -Wait  -FilePath "python" -ArgumentList "-m pip install --upgrade $m"
}
 

