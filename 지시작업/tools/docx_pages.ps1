# 워드 문서를 PDF 로 내보내 쪽 나눔을 눈으로 확인 — Word COM, 바쁘다고 거절하면 다시 시도
param([string]$Path, [string]$Pdf)

function Retry([scriptblock]$Block) {
    for ($k = 0; $k -lt 20; $k++) {
        try { return & $Block } catch { Start-Sleep -Milliseconds 500 }
    }
    throw "Word 응답 없음"
}

$w = Retry { New-Object -ComObject Word.Application }
try {
    Retry { $w.Visible = $false } | Out-Null
    $d = Retry { $w.Documents.Open($Path, $false, $true) }
    Retry { $d.Repaginate() } | Out-Null
    "pages=" + (Retry { $d.ComputeStatistics(2) })
    Retry { $d.ExportAsFixedFormat($Pdf, 17) } | Out-Null
    Retry { $d.Close($false) } | Out-Null
} finally {
    Retry { $w.Quit() } | Out-Null
}
