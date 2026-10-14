"""Generate the initial synthetic demonstration documents."""
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas

folder = Path(__file__).resolve().parents[1] / "sample_data" / "initial"
folder.mkdir(parents=True, exist_ok=True)
(folder / "buyer_message.txt").write_text("Product: Football jersey\nCategory: Sportswear\nQuantity: 500\nUnit: pieces\nColor: navy blue\nMaterial: polyester\nPrinting: sublimation\nDeadline: 2026-11-20\n", encoding="utf-8")
(folder / "quantities.csv").write_text("size,quantity\nS,100\nM,150\nL,150\nXL,100\n", encoding="utf-8")
pdf = Canvas(str(folder / "tech_pack.pdf"), invariant=True)
text = pdf.beginText(72, 770)
text.setFont("Helvetica", 12)
text.textLines("SYNTHETIC TECHNICAL SPECIFICATION\nProduct: Football jersey\nQuantity: 450\nUnit: pieces\nColor: royal blue\nMaterial: polyester\nPrinting: sublimation\nDeadline: 2026-11-20")
pdf.drawText(text)
pdf.showPage()
pdf.save()
