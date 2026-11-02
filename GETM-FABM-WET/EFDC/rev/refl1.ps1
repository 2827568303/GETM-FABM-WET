$ErrorActionPreference='Continue'
$paths = @("EFDC 商业版8.4\DSILIC0.dll","EFDC 商业版8.4\DSILIC1.dll")
foreach($p in $paths){
  "===== $p ====="
  $b=[IO.File]::ReadAllBytes((Resolve-Path $p))
  try{ $asm=[Reflection.Assembly]::Load($b) }catch{ "load err: $_"; continue }
  $asm.FullName
  try{ $ts=$asm.GetTypes() }catch [Reflection.ReflectionTypeLoadException]{ $ts=$_.Exception.Types | Where-Object {$_} }
  "types: $($ts.Count)"
  foreach($t in $ts){
    if($t.IsPublic -or $t.IsNestedPublic){
      $g = $t.Guid
      $attrs = ''
      foreach($a in $t.GetCustomAttributes($false)){ $attrs += $a.GetType().Name + ':' + $a.ToString() + '; ' }
      "$($t.FullName) [guid=$g] $attrs"
      foreach($m in $t.GetMethods([Reflection.BindingFlags]'Public,Static,Instance,DeclaredOnly')){
        "    .$($m.Name)(" + (($m.GetParameters() | ForEach-Object { $_.ParameterType.Name + ' ' + $_.Name }) -join ', ') + ") -> $($m.ReturnType.Name)"
      }
    }
  }
}
