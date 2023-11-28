# Checking the services are existing and running
# Developed by Capella87

# Check PowerShell Version
$PSVersion = $PSVersionTable.PSVersion
$exeName = ""

if ($PSVersion.Major -le 5)
{
    Write-Host "This script requires PowerShell version 5 or higher"
    exit
}

# Check OS is Windows
if ($PSVersion.Major -ge 6)
{
    if ($IsWindows -eq $false)
    {
        Write-Host "This script is only for Windows"
        exit
    }
    $exeName = "pwsh.exe"
}
elseif ($PSVersion.Major -eq 5)
{
    if ($env:OS -ne "Windows_NT")
    {
        Write-Host "This script is only for Windows"
        exit
    }
    $exeName = "powershell.exe"
}

# Check the services are existing


$services = "RabbitMQ", "MariaDB"
Write-Host $services

# Run the service with administrator privileges
for ($i = 0; $i -lt $services.Length; $i++)
{
    $serviceName = $services[$i]
    $service = Get-Service -Name $serviceName
    if ($null -eq $service)
    {
        Write-Host "The service $serviceName is not exist. Check out the service name or install the program"
        exit
    }

    if ($service.Status -eq "Stopped")
    {
        Write-Host "The service $serviceName is stopped"
        Write-Host "Starting the service $serviceName"
        # Start the service with administrator privileges
        Start-Process -FilePath $exeName -ArgumentList "Start-Service -Name $serviceName" -Verb RunAs
    }
    else
    {
        Write-Host "The service $serviceName is running"
        continue
    }
}
