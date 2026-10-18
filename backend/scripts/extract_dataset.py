"""Extract Appendix A JSON from the assignment PDF into data/mock_gds_response.json."""
import json, re, sys
from pypdf import PdfReader
pdf, out = sys.argv[1], sys.argv[2]
text = "\n".join(p.extract_text() for p in PdfReader(pdf).pages)
text = re.sub(r"RightBus Intern Assignment\W+Page \d+", "", text)
text = text[text.index('{\n"status"'):]
# booking tokens were wrapped across lines by the PDF; rejoin them
text = re.sub(r'"booking_token": "(.*?)"', lambda m: '"booking_token": "%s"' % re.sub(r"\s+", "", m.group(1)), text, flags=re.S)
data, _ = json.JSONDecoder().raw_decode(text)
json.dump(data, open(out, "w"), indent=2, ensure_ascii=False)
print("trips:", len(data["trips"]), [t["trip_id"] for t in data["trips"]])
