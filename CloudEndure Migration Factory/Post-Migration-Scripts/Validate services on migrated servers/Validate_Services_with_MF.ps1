$check = Test-Path -Path "C:\Program Files (x86)\CloudEndure\post_launch"
if ($check -contains "True") {echo "Cloudendure agent cleanup not completed"}
else{
Get-Service Amazon*, CSFalconService*, Qua*
}
  
  