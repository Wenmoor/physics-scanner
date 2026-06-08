import latex2mathml.converter
import mathml2omml
from docx.oxml import parse_xml
from docx.text.paragraph import Paragraph

M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def _latex_to_omml_inner(latex: str) -> str:
    mathml = latex2mathml.converter.convert(latex)
    return mathml2omml.convert(mathml)


def append_inline_math(paragraph: Paragraph, latex: str) -> None:
    omml = _latex_to_omml_inner(latex)
    xml = f'<m:oMath xmlns:m="{M_NS}">{omml}</m:oMath>'
    paragraph._element.append(parse_xml(xml))


def append_display_math(paragraph: Paragraph, latex: str) -> None:
    omml = _latex_to_omml_inner(latex)
    xml = (
        f'<m:oMathPara xmlns:m="{M_NS}">'
        f"<m:oMath>{omml}</m:oMath>"
        f"</m:oMathPara>"
    )
    paragraph._element.append(parse_xml(xml))
