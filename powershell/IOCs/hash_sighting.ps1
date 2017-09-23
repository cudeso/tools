# IOCs in file "iocs.txt
# Param1 : startpath
# Param2 : file with file MD5x hashes 
#
# Exports to ²hostname.CSV"
#

Param(
  [Parameter(Mandatory=$true, Position=1)]
  [string]$StartPath,
  
  [Parameter(Mandatory=$true, Position=2)]
  [string]$FileHashes_IOC
)

try { 
    If (Test-Path $FileHashes_IOC) {
        $Hashes_IOC = Get-Content $FileHashes_IOC
        If ( -not $Hashes_IOC) { 
            Write-Host "No IOCs found"
            Exit
        }
    }
    Else {
        Write-Host "IOC file not found"
    }   
    
    If (Test-Path $StartPath) {
        $sightings_array = @();
        Get-ChildItem -Path  $StartPath -Recurse | where {! $_.PSIsContainer}  | 
        Foreach-Object {
            $hash_current_file = $(certutil.exe -hashfile $_.FullName MD5)[1] -replace " ",""
            If ($Hashes_IOC -contains $hash_current_file) {
                Write-Host $hash_current_file, $_.FullName
                $sightings_array += ,@($hash_current_file, $_.FullName);
            }
        }
        $csv_file = $env:computername + ".csv"
        foreach($item1 in $sightings_array) {
            $csv_string = "";
            foreach($item in $item1) {
                $csv_string = $csv_string + $item + ";";
            }
            Add-Content $csv_file $csv_string;
        }
    }
    Else {
        Write-Host "Not a valid path"
    }
}
catch {
    Write-Host "Invalid path or not an IOC file"
}