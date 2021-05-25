# AWS Migration Automation Library
AWS Migration Automation Library is an collection of tools and automation scripts to automate and acclerate AWS migrations, we encourage everyone in AWS to contribute and share.

## Install Python, libraries and Migration Factory Scripts
This automation script on powershell help to install python, needed libraries and execution server scripts on execution server

## Usage
Run powershell as administrator
Set-ExecutionPolicy Bypass
.\install-mf-helper-scripts.ps1

## Variables can be customized
$mfHelperPath  -> Path to extract migration factory scripts
$tmpPath       -> TMP Folder to be created
$pythonUri     -> Python install package URI, it should be "Windows Exe Installer"
$pythonModulesToInstall -> Python needed modules for CEMF Scripts
$mfHelperScriptsUri     -> URI of Automation Scripts of CEMF