from __future__ import annotations

import datetime as dt
import re
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape


SOURCE_MD = Path("presentation/powerpoint-ready-deck.md")
OUTPUT_PPTX = Path("presentation/certAIn-Project-Intelligence-Capstone.pptx")


def parse_slides(markdown_text: str) -> list[tuple[str, list[str]]]:
    slides: list[tuple[str, list[str]]] = []
    current_title: str | None = None
    current_body: list[str] = []

    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip()
        heading_match = re.match(r"^##\s+Slide\s+\d+\s+-\s+(.*)$", line)
        if heading_match:
            if current_title is not None:
                slides.append((current_title, current_body))
            current_title = heading_match.group(1).strip()
            current_body = []
            continue

        if current_title is None:
            continue

        stripped = line.strip()
        if stripped:
            current_body.append(stripped)

    if current_title is not None:
        slides.append((current_title, current_body))

    return slides


def paragraph_xml(text: str, size: int = 1800, bold: bool = False) -> str:
    # Keep markdown bullets readable in the slide by converting them to plain text bullets.
    clean = text
    if clean.startswith("- "):
        clean = f"• {clean[2:]}"
    bold_attr = ' b="1"' if bold else ""
    return (
        "<a:p>"
        f"<a:r><a:rPr lang=\"en-US\" sz=\"{size}\"{bold_attr}/>"
        f"<a:t>{escape(clean)}</a:t></a:r>"
        "<a:endParaRPr lang=\"en-US\"/>"
        "</a:p>"
    )


def build_slide_xml(title: str, body_lines: list[str]) -> str:
    title_paragraph = paragraph_xml(title, size=3600, bold=True)
    body_paragraphs = "".join(paragraph_xml(line, size=1800) for line in body_lines[:14])
    if not body_paragraphs:
        body_paragraphs = paragraph_xml(" ", size=1800)

    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<p:sld xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\" "
        "xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\" "
        "xmlns:p=\"http://schemas.openxmlformats.org/presentationml/2006/main\">"
        "<p:cSld>"
        "<p:spTree>"
        "<p:nvGrpSpPr><p:cNvPr id=\"1\" name=\"\"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>"
        "<p:grpSpPr><a:xfrm><a:off x=\"0\" y=\"0\"/><a:ext cx=\"0\" cy=\"0\"/>"
        "<a:chOff x=\"0\" y=\"0\"/><a:chExt cx=\"0\" cy=\"0\"/></a:xfrm></p:grpSpPr>"
        "<p:sp>"
        "<p:nvSpPr><p:cNvPr id=\"2\" name=\"Title\"/><p:cNvSpPr txBox=\"1\"/><p:nvPr/></p:nvSpPr>"
        "<p:spPr><a:xfrm><a:off x=\"457200\" y=\"228600\"/><a:ext cx=\"8229600\" cy=\"914400\"/></a:xfrm>"
        "<a:prstGeom prst=\"rect\"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr>"
        f"<p:txBody><a:bodyPr wrap=\"square\"/><a:lstStyle/>{title_paragraph}</p:txBody>"
        "</p:sp>"
        "<p:sp>"
        "<p:nvSpPr><p:cNvPr id=\"3\" name=\"Content\"/><p:cNvSpPr txBox=\"1\"/><p:nvPr/></p:nvSpPr>"
        "<p:spPr><a:xfrm><a:off x=\"457200\" y=\"1257300\"/><a:ext cx=\"8229600\" cy=\"4114800\"/></a:xfrm>"
        "<a:prstGeom prst=\"rect\"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr>"
        f"<p:txBody><a:bodyPr wrap=\"square\"/><a:lstStyle/>{body_paragraphs}</p:txBody>"
        "</p:sp>"
        "</p:spTree>"
        "</p:cSld>"
        "<p:clrMapOvr>"
        "<a:overrideClrMapping bg1=\"lt1\" tx1=\"dk1\" bg2=\"lt2\" tx2=\"dk2\" "
        "accent1=\"accent1\" accent2=\"accent2\" accent3=\"accent3\" accent4=\"accent4\" "
        "accent5=\"accent5\" accent6=\"accent6\" hlink=\"hlink\" folHlink=\"folHlink\"/>"
        "</p:clrMapOvr>"
        "</p:sld>"
    )


def build_presentation_xml(slide_count: int) -> str:
    slide_ids = "".join(
        f"<p:sldId id=\"{256 + idx}\" r:id=\"rId{idx + 1}\"/>" for idx in range(slide_count)
    )
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<p:presentation xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\" "
        "xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\" "
        "xmlns:p=\"http://schemas.openxmlformats.org/presentationml/2006/main\">"
        f"<p:sldIdLst>{slide_ids}</p:sldIdLst>"
        "<p:sldSz cx=\"9144000\" cy=\"5143500\" type=\"screen16x9\"/>"
        "<p:notesSz cx=\"6858000\" cy=\"9144000\"/>"
        "<p:defaultTextStyle/>"
        "</p:presentation>"
    )


def build_presentation_rels_xml(slide_count: int) -> str:
    relationships = "".join(
        (
            f"<Relationship Id=\"rId{idx + 1}\" "
            "Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide\" "
            f"Target=\"slides/slide{idx + 1}.xml\"/>"
        )
        for idx in range(slide_count)
    )
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
        f"{relationships}"
        "</Relationships>"
    )


def build_content_types_xml(slide_count: int) -> str:
    slide_overrides = "".join(
        (
            f"<Override PartName=\"/ppt/slides/slide{idx + 1}.xml\" "
            "ContentType=\"application/vnd.openxmlformats-officedocument.presentationml.slide+xml\"/>"
        )
        for idx in range(slide_count)
    )
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">"
        "<Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>"
        "<Default Extension=\"xml\" ContentType=\"application/xml\"/>"
        "<Override PartName=\"/ppt/presentation.xml\" "
        "ContentType=\"application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml\"/>"
        f"{slide_overrides}"
        "<Override PartName=\"/docProps/core.xml\" "
        "ContentType=\"application/vnd.openxmlformats-package.core-properties+xml\"/>"
        "<Override PartName=\"/docProps/app.xml\" "
        "ContentType=\"application/vnd.openxmlformats-officedocument.extended-properties+xml\"/>"
        "</Types>"
    )


def build_root_rels_xml() -> str:
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
        "<Relationship Id=\"rId1\" "
        "Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" "
        "Target=\"ppt/presentation.xml\"/>"
        "<Relationship Id=\"rId2\" "
        "Type=\"http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties\" "
        "Target=\"docProps/core.xml\"/>"
        "<Relationship Id=\"rId3\" "
        "Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties\" "
        "Target=\"docProps/app.xml\"/>"
        "</Relationships>"
    )


def build_core_xml() -> str:
    now = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<cp:coreProperties xmlns:cp=\"http://schemas.openxmlformats.org/package/2006/metadata/core-properties\" "
        "xmlns:dc=\"http://purl.org/dc/elements/1.1/\" "
        "xmlns:dcterms=\"http://purl.org/dc/terms/\" "
        "xmlns:dcmitype=\"http://purl.org/dc/dcmitype/\" "
        "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">"
        "<dc:title>certAIn Project Intelligence Capstone</dc:title>"
        "<dc:creator>Capstone Team</dc:creator>"
        "<cp:lastModifiedBy>Codex</cp:lastModifiedBy>"
        f"<dcterms:created xsi:type=\"dcterms:W3CDTF\">{now}</dcterms:created>"
        f"<dcterms:modified xsi:type=\"dcterms:W3CDTF\">{now}</dcterms:modified>"
        "</cp:coreProperties>"
    )


def build_app_xml(slide_count: int) -> str:
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Properties xmlns=\"http://schemas.openxmlformats.org/officeDocument/2006/extended-properties\" "
        "xmlns:vt=\"http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes\">"
        "<Application>Microsoft PowerPoint</Application>"
        "<PresentationFormat>On-screen Show (16:9)</PresentationFormat>"
        f"<Slides>{slide_count}</Slides>"
        "<Notes>0</Notes><HiddenSlides>0</HiddenSlides><MMClips>0</MMClips>"
        "<ScaleCrop>false</ScaleCrop>"
        "<HeadingPairs><vt:vector size=\"2\" baseType=\"variant\">"
        "<vt:variant><vt:lpstr>Theme</vt:lpstr></vt:variant>"
        "<vt:variant><vt:i4>1</vt:i4></vt:variant>"
        "</vt:vector></HeadingPairs>"
        "<TitlesOfParts><vt:vector size=\"1\" baseType=\"lpstr\">"
        "<vt:lpstr>Default Theme</vt:lpstr>"
        "</vt:vector></TitlesOfParts>"
        "<Company></Company><LinksUpToDate>false</LinksUpToDate><SharedDoc>false</SharedDoc>"
        "<HyperlinksChanged>false</HyperlinksChanged><AppVersion>16.0000</AppVersion>"
        "</Properties>"
    )


def write_pptx(slides: list[tuple[str, list[str]]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", build_content_types_xml(len(slides)))
        zf.writestr("_rels/.rels", build_root_rels_xml())
        zf.writestr("docProps/core.xml", build_core_xml())
        zf.writestr("docProps/app.xml", build_app_xml(len(slides)))
        zf.writestr("ppt/presentation.xml", build_presentation_xml(len(slides)))
        zf.writestr("ppt/_rels/presentation.xml.rels", build_presentation_rels_xml(len(slides)))

        for idx, (title, body_lines) in enumerate(slides, start=1):
            zf.writestr(f"ppt/slides/slide{idx}.xml", build_slide_xml(title, body_lines))


def main() -> None:
    if not SOURCE_MD.exists():
        raise FileNotFoundError(f"Missing source deck markdown: {SOURCE_MD}")

    slides = parse_slides(SOURCE_MD.read_text(encoding="utf-8"))
    if not slides:
        raise RuntimeError("No slides parsed from markdown.")

    write_pptx(slides, OUTPUT_PPTX)
    print(f"Generated: {OUTPUT_PPTX} ({len(slides)} slides)")


if __name__ == "__main__":
    main()
