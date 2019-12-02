# Get DNS data, logged via Sysmon
# 
# Koen Van Impe     20191202
#
# Query error codes https://docs.microsoft.com/en-us/windows/win32/debug/system-error-codes--9000-11999-
# Script inspired by http://www.darkartistry.com/2019/08/create-insert-and-query-sqlite-with-powershell/
# Requires SQLite - https://system.data.sqlite.org/index.html/doc/trunk/www/downloads.wiki
# Requires Get-WinEventData https://gallery.technet.microsoft.com/scriptcenter/Get-WinEventData-Extract-344ad840


Add-Type -Path "C:\Program Files\System.Data.SQLite\2012\bin\System.Data.SQLite.dll"
. "./Get-WinEventData.ps1"  


# Create SQLite database
#
Function createDataBase([string]$db) {
    Try {
        If (!(Test-Path $db)) {
        
            $CONN = New-Object -TypeName System.Data.SQLite.SQLiteConnection
  
            $CONN.ConnectionString = "Data Source=$db"
            $CONN.Open()
  
            # TEXT as ISO8601 strings ('YYYY-MM-DD HH:MM:SS.SSS')
            # ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, INSERT NULL to increment.
            $createTableQuery = "CREATE TABLE dns (
                                        query        TEXT    NULL,
                                        type        TEXT    NULL,
                                        answer    TEXT    NULL,
                                        count    INTEGER NULL,
                                        ttl  INTEGER NULL,
                                        first     TEXT    NULL,
                                        last   TEXT    NULL,
                                        hostname     TEXT    NULL,
                                        status   INTEGER NULL,
                                        image TEXT NULL
                                        );"
  
            $CMD = $CONN.CreateCommand()
            $CMD.CommandText = $createTableQuery
            $CMD.ExecuteNonQuery()
    
            $CMD.Dispose()
            $CONN.Close()
            Log-It "Create database and table: Ok"
  
        } Else {
            Log-It "DB Exists: Ok"
        }
  
    } Catch {
        Log-It "Could not create database: Error"
    }
}

# Query the SQLite database
#
Function queryDatabase([string]$db, [string]$sql) {
  
    Try {
        If (Test-Path $db) {
  
            $CONN = New-Object -TypeName System.Data.SQLite.SQLiteConnection
            $CONN.ConnectionString = "Data Source=$db"
            $CONN.Open()
  
            $CMD = $CONN.CreateCommand()
            $CMD.CommandText = $sql
  
            $ADAPTER = New-Object  -TypeName System.Data.SQLite.SQLiteDataAdapter $CMD
            $DATA = New-Object System.Data.DataSet
  
            $ADAPTER.Fill($DATA)
  
            $TABLE = $DATA.Tables
  
            ForEach ($t in $TABLE){
                Write-Output $t
            }
  
            $CMD.Dispose()
            $CONN.Close()
  
        } Else {
            Log-It "Unable to find database: Query Failed"
        }
  
    } Catch {
        Log-It "Unable to query database: Error"
    }
}
 
# Insert a row in the database
# 
Function insertDatabase([string]$db, [System.Collections.ArrayList]$rows) {
  
    Try {
        If (Test-Path $db) {
        
            $CONN = New-Object -TypeName System.Data.SQLite.SQLiteConnection

            $CONN.ConnectionString = "Data Source=$db"
            $CONN.Open() 
  
            $CMD = $CONN.CreateCommand() 

            ForEach($row in $rows) {
        
                $sql = "INSERT OR REPLACE INTO dns (query, type, answer, count, ttl, first, last, hostname, status, image)"
                $sql += " VALUES (@dnsquery, @dnstype, @dnsanswer, @dnscount, @dnsttl, @dnsfirst, @dnslast, @dnshostname, @dnsstatus, @dnsimage );"
                                 
                $CMD.Parameters.AddWithValue("@dnsquery", $row.dnsquery) | Out-Null 
                $CMD.Parameters.AddWithValue("@dnstype", $row.dnstype) | Out-Null 
                $CMD.Parameters.AddWithValue("@dnsanswer", $row.dnsanswer) | Out-Null 
                $CMD.Parameters.AddWithValue("@dnscount", $row.dnscount) | Out-Null 
                $CMD.Parameters.AddWithValue("@dnsttl", $row.dnsttl) | Out-Null 
                $CMD.Parameters.AddWithValue("@dnsfirst", $row.dnsfirst) | Out-Null 
                $CMD.Parameters.AddWithValue("@dnslast", $row.dnslast) | Out-Null 
                $CMD.Parameters.AddWithValue("@dnshostname", $row.dnshostname) | Out-Null 
                $CMD.Parameters.AddWithValue("@dnsstatus", $row.dnsstatus) | Out-Null
                $CMD.Parameters.AddWithValue("@dnsimage", $row.dnsimage) | Out-Null
  
                $CMD.CommandText = $sql 
                $CMD.ExecuteNonQuery() | Out-Null

            }
  
            $CMD.Dispose() | Out-Null
            $CONN.Close() | Out-Null
  
            # Log-It "Inserted records successfully: Ok"
  
        } Else {
            Log-It "Unable to find database: Insert Failed"
        }
  
    } Catch {
        Log-It "Unable to insert into database: Error"
    }
}
 
# Internal logger
# 
Function Log-It([string]$logLine)
{
    $LogPath = "c:\Users\Administrator\sqlite.log" # Change path
    $NewLine = "`r`n"
  
    $Line = "{0}{1}" -f $logLine, $NewLine
    if ($logPath) {
        write-output $Line
        $Line | Out-File $logPath -Append
    } else {
        write-output $Line
    }
}
  

# Fetch events from Eventlog and store in database
#
Function fetchEvents()
{
    $Rows = New-Object System.Collections.ArrayList
    $Today = ((Get-Date).AddDays(-1)).DateTime

    Get-WinEvent -FilterHashtable @{logname="Microsoft-Windows-Sysmon/Operational";id=22} |
    Where-Object {$_.TimeCreated -lt $Today } |
    Get-WinEventData | 
    Select-Object MachineName, TimeCreated, EventDataQueryName, EventDataQueryResults, EventDataQueryStatus, EventDataImage  | 
    # Select  -last 15  | 

    foreach  {
        $dnsfirst = $_.TimeCreated
        $dnslast = $_.TimeCreated        
        $dnstype = "A"
        $result = $_.EventDataQueryResults
        $dnsquery = $_.EventDataQueryName
        $dnshostname = $_.MachineName
        $dnsstatus = $_.EventDataQueryStatus
        $dnsimage = $_.EventDataImage

        if ($result -like '*;*') {
            $result.split(";") | foreach {
                if ($_ -like 'type:  5*') {
                    $dnstype = 5 # CNAME
                    $dnstype = "CNAME"
                    $dnsresult = $_.substring('type:  5'.Length).trim()

                }
                elseif ($_ -like 'type:  2*') {
                    $dnstype = 2 # NS
                    $dnstype = "NS"
                    $dnsresult = $_.substring('type:  2'.Length).trim()
                }
                else {
                    $dnsresult = $_.trim()
                }

                if ($dnsresult) {
                    $Rows.Add(@{'dnsquery'=$dnsquery; 'dnstype'= $dnstype; 'dnsanswer'=$dnsresult; 'dnsttl'=0; 'dnsfirst'=$dnsfirst; 'dnslast'=$dnslast; 'dnshostname'=$dnshostname ; 'dnsstatus'=$dnsstatus ; 'dnsimage'=$dnsimage})
                }
            }
        }
    } # | Out-Null

    insertDatabase $DBPath $Rows       
    
}

# ******** MAIN ********
  
$DBPath = "c:\Users\Administrator\passivedns.sqlite" # Change path
  
# Create Db and Table.
createDataBase $DBPath
  
# Insert records.
fetchEvents
  
# Fetch records.
#queryDatabase $DBPath "Select * From dns"