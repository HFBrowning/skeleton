

function Main {
    param (
        
    )

    # Rename contents of files first
    # Credit to Russell Munro at: https://stackoverflow.com/questions/11368786
    Get-ChildItem -Recurse *.* |
    ForEach-Object { $a = $_.fullname; (Get-Content $a ) |
        ForEach-Object { $_ -Replace $oldname, $newname }  | 
        Set-Content $a }

    # Rename directories:
    $folders = Get-ChildItem -Recurse -Directory
    # Reverse array to start at deepest nested folders, if we rename the top level folders, the rename won't find the deeper folders later on
    [Array]::Reverse($folders)

    # Go through all the folders
    foreach ($item in $folders) {
        switch ($item.Name) {
            # If folder is PROJ_NAME, change it
            $oldname { Rename-Item $item.FullName -NewName $newname }
            # Otherwise, do nothing
            default {}
        } 
    }

    # Rename files:
    Get-ChildItem -File -Recurse | % { Rename-Item -Path $_.PSPath -NewName $_.Name.replace($oldname, $newname) }

        
}




$oldname = "PROJ_NAME"
$newname = # Add something or get an error!

