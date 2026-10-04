param(
    [Parameter(Mandatory=$true)]
    [string]$ConfigJsonPath
)

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

if (!(Test-Path $ConfigJsonPath)) {
    Write-Error "Config JSON file not found: $ConfigJsonPath"
    exit 1
}

$rawJson = Get-Content -Raw -Path $ConfigJsonPath -Encoding UTF8
$config = $rawJson | ConvertFrom-Json

$templatePath = $config.templatePath
$outputPath = $config.outputPath

if (!(Test-Path $templatePath)) {
    Write-Error "Template file not found: $templatePath"
    exit 1
}

$outDir = Split-Path -Parent $outputPath
if ($outDir -and !(Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

# Copy template to output path
Copy-Item -Path $templatePath -Destination $outputPath -Force

$zip = [System.IO.Compression.ZipFile]::Open($outputPath, [System.IO.Compression.ZipArchiveMode]::Update)

# 1. Slide text replacements
if ($config.slideReplacements) {
    for ($i = 1; $i -le 15; $i++) {
        $slideKey = "slide$i"
        $replacements = $config.slideReplacements.$slideKey
        if ($replacements) {
            $entry = $zip.GetEntry("ppt/slides/slide$i.xml")
            if ($entry) {
                $stream = $entry.Open()
                $reader = New-Object System.IO.StreamReader($stream, [System.Text.Encoding]::UTF8)
                $xml = $reader.ReadToEnd()
                $reader.Dispose()
                $stream.Dispose()

                foreach ($prop in $replacements.PSObject.Properties) {
                    $search = [regex]::Escape($prop.Name)
                    $replace = [System.Security.SecurityElement]::Escape([string]$prop.Value)
                    $xml = [regex]::Replace($xml, $search, $replace)
                }

                # Also remove the internal watermark instruction if specified
                if ($config.hideInternalInstructions) {
                    $xml = $xml -replace "INTERNE · MASQUER AVANT EXPORT SOURCE À AJOUTER", ""
                    $xml = $xml -replace "SOURCE À AJOUTER", ""
                }

                $entry.Delete()
                $newEntry = $zip.CreateEntry("ppt/slides/slide$i.xml")
                $newStream = $newEntry.Open()
                $writer = New-Object System.IO.StreamWriter($newStream, [System.Text.Encoding]::UTF8)
                $writer.Write($xml)
                $writer.Dispose()
                $newStream.Dispose()
            }
        }
    }
}

# 2. Image replacements (if specified in config.images)
if ($config.images) {
    foreach ($imgProp in $config.images.PSObject.Properties) {
        $targetMedia = $imgProp.Name # e.g. "ppt/media/image.png"
        $sourcePathOrBase64 = [string]$imgProp.Value
        if ($sourcePathOrBase64) {
            $bytes = $null
            if ($sourcePathOrBase64.StartsWith("data:image")) {
                $base64Data = $sourcePathOrBase64 -replace '^data:image/[^;]+;base64,', ''
                $bytes = [System.Convert]::FromBase64String($base64Data)
            } elseif (Test-Path $sourcePathOrBase64) {
                $bytes = [System.IO.File]::ReadAllBytes($sourcePathOrBase64)
            }

            if ($bytes) {
                $entry = $zip.GetEntry($targetMedia)
                if ($entry) { $entry.Delete() }
                $newEntry = $zip.CreateEntry($targetMedia)
                $newStream = $newEntry.Open()
                $newStream.Write($bytes, 0, $bytes.Length)
                $newStream.Dispose()
            }
        }
    }
}

$zip.Dispose()
Write-Output "SUCCESS: PPTX successfully generated at $outputPath"
