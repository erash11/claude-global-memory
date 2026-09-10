"""Bring the Request Workflow handout and Executive Summary into line with the
08-14 framework: sync step 1.4, and drop the 'high-level by design' framing."""

from docx import Document

D = ("/Users/kristinarash/Library/CloudStorage/OneDrive-BaylorUniversity/"
     "00_Primary_Storage_Drive/XXXX_Transfer/SoftwareTechDocs/")

ADD_14 = (" The Athletics steps described here feed that review; they do not create a"
          " separate ITS workflow.")

NEW_NCAA_ES = ("The NCAA Sports Science Institute has published guidance on the responsible use of "
               "performance technologies. That guidance sets the expectations each institution is to "
               "meet and leaves the method of implementation to the institution. This framework is "
               "Baylor Athletics' implementation, and Appendix A of the framework maps each NCAA "
               "recommendation to the section that carries it.")


def set_date(doc, value="August 14, 2026"):
    for t in doc.tables:
        for row in t.rows:
            if row.cells[0].text.strip() == "Date":
                c = row.cells[1]
                if c.paragraphs[0].runs:
                    c.paragraphs[0].runs[0].text = value
                    for r in c.paragraphs[0].runs[1:]:
                        r.text = ""
                    return True
    return False


# --- Request Workflow handout ----------------------------------------------
wf_in = D + "Software_and_Tech_Management_WORKFLOW_ER_2026-08-12.docx"
wf_out = D + "Software_and_Tech_Management_WORKFLOW_ER_2026-08-14.docx"
d = Document(wf_in)
hit = False
for p in d.paragraphs:
    if p.text.strip().startswith("1.4  The forms are submitted to ITS"):
        assert len(p.runs) == 1, "unexpected run split in workflow 1.4"
        assert "separate ITS workflow" not in p.text, "already patched"
        p.runs[0].text = p.runs[0].text + ADD_14
        hit = True
        break
assert hit, "workflow step 1.4 not found"
print("workflow: 1.4 synced | date row updated:", set_date(d))
d.save(wf_out)
print("WROTE", wf_out)

# --- Executive Summary ------------------------------------------------------
es_in = D + "Software_and_Tech_Management_EXEC_SUMMARY_ER_2026-08-12.docx"
es_out = D + "Software_and_Tech_Management_EXEC_SUMMARY_ER_2026-08-14.docx"
d = Document(es_in)
hit = False
for p in d.paragraphs:
    if "high-level by design" in p.text:
        assert len(p.runs) == 1, "unexpected run split in exec summary NCAA bullet"
        p.runs[0].text = NEW_NCAA_ES
        hit = True
        break
assert hit, "exec summary NCAA bullet not found"
print("exec summary: NCAA framing updated | date row updated:", set_date(d))
d.save(es_out)
print("WROTE", es_out)
