$pairs = @(
 @('2334d2b2-713e-11cf-8ae5-00aa00c00905','DataObject'),
 @('2334d2b4-713e-11cf-8ae5-00aa00c00905','DataObjectFiles'),
 @('1efb6596-857c-11d1-b16a-00c0f0283628','TabStrip'),
 @('1efb6598-857c-11d1-b16a-00c0f0283628','Tabs'),
 @('1efb659a-857c-11d1-b16a-00c0f0283628','Tab'),
 @('66833fe6-8583-11d1-b16a-00c0f0283628','Toolbar'),
 @('66833fe8-8583-11d1-b16a-00c0f0283628','Buttons'),
 @('66833fea-8583-11d1-b16a-00c0f0283628','Button'),
 @('66833fec-8583-11d1-b16a-00c0f0283628','ButtonMenus'),
 @('66833fee-8583-11d1-b16a-00c0f0283628','ButtonMenu'),
 @('8e3867a3-8586-11d1-b16a-00c0f0283628','StatusBar'),
 @('8e3867a5-8586-11d1-b16a-00c0f0283628','Panels'),
 @('8e3867ab-8586-11d1-b16a-00c0f0283628','Panel'),
 @('35053a22-8589-11d1-b16a-00c0f0283628','ProgressBar'),
 @('c74190b6-8589-11d1-b16a-00c0f0283628','TreeView'),
 @('0713e8c0-850a-101b-afc0-4210102a8da7','Nodes'),
 @('c74190b9-8589-11d1-b16a-00c0f0283628','Node'),
 @('bdd1f04b-858b-11d1-b16a-00c0f0283628','ListView'),
 @('bdd1f04d-858b-11d1-b16a-00c0f0283628','ListItems'),
 @('bdd1f04f-858b-11d1-b16a-00c0f0283628','ListItem'),
 @('0713e8c6-850a-101b-afc0-4210102a8da7','ColumnHeaders'),
 @('bdd1f052-858b-11d1-b16a-00c0f0283628','ColumnHeader'),
 @('bdd1f054-858b-11d1-b16a-00c0f0283628','ListSubItems'),
 @('bdd1f056-858b-11d1-b16a-00c0f0283628','ListSubItem'),
 @('2c247f23-8591-11d1-b16a-00c0f0283628','ImageList'),
 @('2c247f25-8591-11d1-b16a-00c0f0283628','ListImages'),
 @('2c247f27-8591-11d1-b16a-00c0f0283628','ListImage'),
 @('f08df954-8592-11d1-b16a-00c0f0283628','Slider'),
 @('c8a3dc01-8593-11d1-b16a-00c0f0283628','Controls'),
 @('dd9da661-8594-11d1-b16a-00c0f0283628','ComboItem'),
 @('dd9da663-8594-11d1-b16a-00c0f0283628','ComboItems'),
 @('dd9da666-8594-11d1-b16a-00c0f0283628','ImageCombo')
)
$ocx='C:\EFDC84_LIC\mscomctl.ocx'; $lib='{831FDD16-0C5C-11D2-A9FC-0000F8754DA1}'
foreach($p in $pairs){
  $g=$p[0].ToUpper(); $name=$p[1]
  foreach($pre in @('HKCU:\Software\Classes\CLSID','HKCU:\Software\Classes\WOW6432Node\CLSID')){
    $base="$pre\{$g}"
    New-Item -Path "$base\InprocServer32" -Force | Out-Null
    Set-ItemProperty -Path "$base\InprocServer32" -Name '(default)' -Value $ocx
    Set-ItemProperty -Path "$base\InprocServer32" -Name 'ThreadingModel' -Value 'Apartment'
    New-Item -Path "$base\Control" -Force | Out-Null
    Set-ItemProperty -Path $base -Name '(default)' -Value $name
    New-ItemProperty -Path $base -Name 'Version' -Value '2.0' -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $base -Name 'ProgID' -Value ("MSComctlLib."+$name) -PropertyType String -Force | Out-Null
    New-Item -Path "$base\TypeLib" -Force | Out-Null
    Set-ItemProperty -Path "$base\TypeLib" -Name '(default)' -Value $lib
    Set-ItemProperty -Path "$base\TypeLib" -Name 'Version' -Value '2.0'
  }
  foreach($pre in @('HKCU:\Software\Classes','HKCU:\Software\Classes\WOW6432Node')){
    $pk="$pre\MSComctlLib.$name"
    New-Item -Path $pk -Force | Out-Null
    Set-ItemProperty -Path $pk -Name '(default)' -Value $name
    New-Item -Path "$pk\CLSID" -Force | Out-Null
    Set-ItemProperty -Path "$pk\CLSID" -Name '(default)' -Value "{$(($g))}"
  }
}
Write-Output "registered $($pairs.Count) coclasses with ProgID"
