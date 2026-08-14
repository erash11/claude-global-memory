import copy
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC = "/Users/kristinarash/Library/CloudStorage/OneDrive-BaylorUniversity/00_Primary_Storage_Drive/XXXX_Transfer/SoftwareTechDocs/_Archive/2026-08-12/Software_and_Tech_Management_ER_2026-08-12__.docx"
OUT = "/Users/kristinarash/Library/CloudStorage/OneDrive-BaylorUniversity/00_Primary_Storage_Drive/XXXX_Transfer/SoftwareTechDocs/Software_and_Tech_Management_ER_2026-08-14.docx"

GREEN = RGBColor(0x15, 0x47, 0x34)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

d = Document(SRC)

# --- 1. refresh the cover metadata table date -------------------------------
meta = d.tables[0]
for row in meta.rows:
    if row.cells[0].text.strip() == "Date":
        c = row.cells[1]
        c.paragraphs[0].runs[0].text = "August 14, 2026"
        for r in c.paragraphs[0].runs[1:]:
            r.text = ""

# --- 2. one-sentence addition at Phase 1.4 (ITS complementarity) ------------
TARGET = "1.4  The forms are submitted to ITS for technical, security, and integration review. This is the second control point."
ADD = (" The Athletics steps described in this framework feed that review; they do not create a"
       " separate ITS workflow.")
hit = False
for p in d.paragraphs:
    if p.text.strip() == TARGET:
        p.runs[-1].text = p.runs[-1].text + ADD
        hit = True
        break
assert hit, "Phase 1.4 paragraph not found"

# --- 2b. §3 rewrite: remove the "high-level by design" framing ---------------
OLD3 = ("The NCAA Sports Science Institute has published guidance on the Responsible Use of "
        "Performance Technologies in College Athletics. That guidance is high-level by design, "
        "leaving each school to implement it according to its own needs and resources. This "
        "framework is Baylor Athletics' implementation.")
NEW3 = ("The NCAA Sports Science Institute has published guidance on the Responsible Use of "
        "Performance Technologies in College Athletics. That guidance sets the expectations each "
        "institution is to meet and leaves the method of implementation to the institution, "
        "according to its own structure and resources. This framework is Baylor Athletics' "
        "implementation. Appendix A maps each NCAA recommendation to the section of this framework "
        "that carries it.")
hit3 = False
for p in d.paragraphs:
    if "high-level by design" in p.text:
        assert len(p.runs) == 1, "unexpected run split in §3"
        p.runs[0].text = NEW3
        hit3 = True
        break
assert hit3, "§3 paragraph not found"

# --- helpers ---------------------------------------------------------------
def add_para(text="", bold=False, size=10.5, color=None, space_before=6, space_after=6):
    p = d.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    if text:
        r = p.add_run(text)
        r.bold = bold
        r.font.size = Pt(size)
        if color is not None:
            r.font.color.rgb = color
    return p

def h1(text):
    return add_para(text, bold=True, size=14.5, color=GREEN, space_before=18, space_after=8)

def h2(text):
    return add_para(text, bold=True, size=12, color=GREEN, space_before=14, space_after=6)

def shade(cell, hexfill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hexfill)
    tcPr.append(shd)

def set_w(cell, twips):
    tcPr = cell._tc.get_or_add_tcPr()
    for old in tcPr.findall(qn('w:tcW')):
        tcPr.remove(old)
    tcW = OxmlElement('w:tcW')
    tcW.set(qn('w:w'), str(twips))
    tcW.set(qn('w:type'), 'dxa')
    tcPr.append(tcW)

def fill_cell(cell, lines, bold=False, color=None):
    cell.text = ""
    first = True
    for line in lines:
        p = cell.paragraphs[0] if first else cell.add_paragraph()
        first = False
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(line)
        r.bold = bold
        r.font.size = Pt(9.5)
        if color is not None:
            r.font.color.rgb = color

def repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement('w:tblHeader')
    el.set(qn('w:val'), 'true')
    trPr.append(el)

# --- 3. Appendix A ---------------------------------------------------------
h1("Appendix A — NCAA Performance Technologies Recommendations Crosswalk")

add_para(
    "The NCAA Sport Science Institute's consensus guidance on the responsible use of performance "
    "technologies in college athletics is organized around five recommendations. The table below carries "
    "each recommendation, the NCAA strategy, the corresponding Baylor action step, and the section of this "
    "framework where it is addressed. Entries marked “planned for Version 1” identify work that is "
    "scoped and scheduled for the next revision of this document."
)

COLW = [1850, 3050, 3050, 2850]  # = 10800 twips = 540 pt usable width
HEAD = ["Recommendation", "NCAA Strategy", "Baylor Action Step", "Framework Reference"]

ROWS = [
    (
        "1. Policy",
        ["Create a written plan. Build it with a multidisciplinary team (student-athletes, sports medicine, "
         "coaches, admin, legal, IT). Review it regularly."],
        ["Form a MDT (Multi-disciplinary Team) or a Performance Technology Working Group, draft the plan, "
         "and present it to S-A Services Staff for input."],
        ["§1.1  Policy statement — the written-plan requirement",
         "§1.2  Reason for the framework",
         "§5  Roles and responsibilities — review functions spanning sports medicine, compliance, legal, "
         "ITS, procurement, and Student-Athlete Representatives",
         "§8  Phase 1.7 — standing review cadence with ITS",
         "Standing Performance Technology Working Group and the framework’s own review cycle: planned for Version 1."],
    ),
    (
        "2. Education",
        ["Train everyone at least once a year. Tailor content by audience. Cover limitations, data privacy, "
         "informed consent, and departmental policies."],
        ["Add a performance technology module to existing compliance sessions and new student-athletes’ "
         "onboarding. Different content for coaches, Athletic Medicine, Athletics Performance, and "
         "student-athletes, etc."],
        ["§1.1  Policy statement — routine education as a governing requirement",
         "§5  Coaches, Staff, and Users — required training",
         "§5  Student-Athlete Representatives — feedback on education",
         "A dedicated Education and Training section, carrying annual cadence and audience-specific content: "
         "planned for Version 1."],
    ),
    (
        "3. Data Management",
        ["Establish who owns the data, where it lives, who can see it, and what it can be used for. Plan for "
         "transfer student-athletes."],
        ["Run a full technology inventory across all sports. Work with legal and IT to establish ownership, "
         "access, and transfer protocols. Develop a data rights/release consent template."],
        ["§1.1  Policy statement — authorized purposes; access, retention, and disposal",
         "§2.4  Definitions — Restricted / Protected Data; Medical Decision-Making Data; Approved Use Case; "
         "Student-Athlete Notice",
         "§4  Intended outcomes — department-wide technology inventory",
         "§5  ITS / Information Security — access, authentication, storage, transmission",
         "§5  Office of General Counsel / Privacy — consent, data rights, disclosure",
         "§5  Procurement / Contracting — ownership, permitted use, retention, deletion, portability",
         "§6  Level 3 Comprehensive Review — external data sharing; third-party processing",
         "Transfer student-athlete data protocol and the data rights / release consent template: planned for Version 1."],
    ),
    (
        "4. Tech Selection",
        ["Evaluate quality (accuracy, reliability, validity) before you buy. Use evidence-based frameworks. "
         "Decisions should be made by a cross-functional group."],
        ["Build a Technology Evaluation Checklist. Route all new purchases through the Working Group (MDT). "
         "Establish a scalable review process with documentation."],
        ["§5  Roles and responsibilities — cross-functional review functions",
         "§6  Levels of review — Level 1 Standard, Level 2 Enhanced, Level 3 Comprehensive",
         "§7  Exceptions — expedited requests clear the same control points",
         "§8  Phase 1.2–1.6 — Technology Idea Form and internal ATH Form; Business Office control point; "
         "ITS control point; Technology Evaluation Scorecard at 1.5; documented decision",
         "Quality criteria (accuracy, reliability, validity) are carried in the Technology Evaluation Scorecard, "
         "maintained as a companion artifact to this framework."],
    ),
    (
        "5. Continuous Improvement",
        ["Collect feedback from student-athletes, coaches, and staff on a regular basis. Student-athlete "
         "feedback is not optional. Use it to update the plan."],
        ["Annual student-athlete survey. The Working Group runs an annual review. Each technology gets a "
         "continuation, modification, or discontinuation decision."],
        ["§8  Phase 3.1–3.4 — review at six months or end of competitive season; utilization measured "
         "against stated intent; diagnostic conversation; outcome of renew, modify or renegotiate, or discontinue",
         "§5  Student-Athlete Representatives — feedback on transparency, education, perceived benefits, "
         "and potential unintended impacts",
         "Annual student-athlete survey and the annual Working Group review of the framework: planned for Version 1."],
    ),
]

tbl = d.add_table(rows=1 + len(ROWS), cols=4)
tbl.style = "Table Grid"
tbl.autofit = False

hdr = tbl.rows[0]
repeat_header(hdr)
for i, txt in enumerate(HEAD):
    fill_cell(hdr.cells[i], [txt], bold=True, color=WHITE)
    shade(hdr.cells[i], "154734")
    set_w(hdr.cells[i], COLW[i])

for ri, (rec, strat, action, ref) in enumerate(ROWS, start=1):
    row = tbl.rows[ri]
    fill_cell(row.cells[0], [rec], bold=True)
    fill_cell(row.cells[1], strat)
    fill_cell(row.cells[2], action)
    fill_cell(row.cells[3], ref)
    for ci in range(4):
        set_w(row.cells[ci], COLW[ci])

# --- 4. A.1 foundational concepts ------------------------------------------
h2("A.1  Foundational concepts")
add_para(
    "Two foundational concepts in the NCAA guidance sit alongside the five recommendations. The breadth of "
    "the NCAA definition of performance technology, which reaches cameras, surveys, and applications and not "
    "only wearables, is carried in the §2.1 scope statement and the §2.4 definition of Athlete Performance "
    "Technology. Student-athlete rights, informed consent, and the potential for unintended impacts, including "
    "effects on mental health and body image, are reflected in the §2.4 Student-Athlete Notice, the §5 Office "
    "of General Counsel / Privacy and Health & Wellness / Sports Medicine review functions, and the §5 "
    "Student-Athlete Representatives feedback role. Explicit treatment of unintended impacts within the "
    "education content and the annual student-athlete survey is planned for Version 1."
)

h2("A.2  Relationship to institutional workflow")
add_para(
    "This framework is an Athletics-side overlay, as stated in §2.3. It routes technology decisions into the "
    "existing Baylor governance channels rather than around them. The Athletics intake and control points "
    "described in §8 are intended to complement institutional review rather than to operate as a separate workflow."
)

d.save(OUT)
print("WROTE", OUT)
print("paragraphs:", len(d.paragraphs), "tables:", len(d.tables))
