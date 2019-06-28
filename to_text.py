import sys
from pathlib import Path

import pdfminer.high_level
import pdfminer.layout
import pdfminer.settings

pdfminer.settings.STRICT = False


def extract_text(pdf_file, outfile,
                 no_laparams=False, all_texts=None, detect_vertical=None,  # LAParams
                 word_margin=None, char_margin=None, line_margin=None, boxes_flow=None,  # LAParams
                 output_type='text', codec='utf-8', strip_control=False,
                 maxpages=0, page_numbers=None, password="", scale=1.0, rotation=0,
                 layoutmode='normal', output_dir=None, debug=False,
                 disable_caching=False, **other):
    if not pdf_file:
        raise ValueError("Must provide file to work upon!")

    # If any LAParams group arguments were passed, create an LAParams object and
    # populate with given args. Otherwise, set it to None.
    if not no_laparams:
        laparams = pdfminer.layout.LAParams()
        for param in ("all_texts", "detect_vertical", "word_margin", "char_margin", "line_margin", "boxes_flow"):
            paramv = locals().get(param, None)
            if paramv is not None:
                setattr(laparams, param, paramv)
    else:
        laparams = None

    with open(outfile, "wb") as outfp:
        with open(pdf_file, "rb") as fp:
            pdfminer.high_level.extract_text_to_fp(fp, **locals())


if __name__ == '__main__':
    print(sys.argv)
    source_dir = Path(sys.argv[1]).resolve()
    dest_dir = Path(sys.argv[2]).resolve()
    for pdf_file in sorted(source_dir.glob('*.pdf')):
        txt_file = dest_dir.joinpath(pdf_file.name).with_suffix('.txt')
        print(pdf_file)
        print(txt_file)
        if txt_file.exists():
            print("Already exists. Skipping...")
        else:
            print("Extracting...")
            extract_text(pdf_file=pdf_file, outfile=txt_file)
