param(
    [string]$DocPath,
    [string]$PdfPath
)

$Word = New-Object -ComObject Word.Application
$Word.Visible = $false
try {
    $Doc = $Word.Documents.Open((Resolve-Path $DocPath).Path)
    Write-Host "Document opened successfully: $($Doc.Name)"
    $Pages = $Doc.ComputeStatistics([Microsoft.Office.Interop.Word.WdStatistic]::wdStatisticPages)
    Write-Host "Total Pages: $Pages"
    if ($PdfPath) {
        $PdfFullPath = [System.IO.Path]::GetFullPath($PdfPath)
        $Doc.SaveAs([ref]$PdfFullPath, [ref]17) # 17 = wdFormatPDF
        Write-Host "PDF exported to: $PdfFullPath"
    }
    $Doc.Close([ref]$false)
}
finally {
    $Word.Quit([ref]$false)
}
