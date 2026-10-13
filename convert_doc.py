import os
import subprocess
import fitz

def convert_docx_to_pdf(docx_path, pdf_path):
    docx_path = os.path.abspath(docx_path)
    pdf_path = os.path.abspath(pdf_path)
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    
    ps_script = f"""
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = [Microsoft.Office.Interop.Word.WdAlertLevel]::wdAlertsNone
try {{
    $doc = $word.Documents.Open('{docx_path}')
    $doc.SaveAs([ref]'{pdf_path}', [ref]17)
    $doc.Close()
}} finally {{
    $word.Quit()
}}
"""
    ps_file = os.path.abspath("convert_tmp.ps1")
    with open(ps_file, "w", encoding="utf-8") as f:
        f.write(ps_script)
    
    res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_file], capture_output=True, text=True)
    if os.path.exists(ps_file):
        os.remove(ps_file)
    
    if os.path.exists(pdf_path):
        doc = fitz.open(pdf_path)
        print(f"Successfully converted to PDF: {pdf_path} ({len(doc)} pages)")
        return len(doc)
    else:
        print("Conversion failed. Output:", res.stdout, res.stderr)
        return -1

if __name__ == "__main__":
    convert_docx_to_pdf("PartTime_DevOps_Laboratory_Project_Report.docx", "test_eval.pdf")
