
#
# import sys
# import PyPDF2
# import PythonMagick
#
# pdffilename = "C:/temp/oRxeC5q6BgOl.pdf"
# pdf_im = PyPDF2.PdfFileReader(open(pdffilename, "rb"))
# npage = pdf_im.getNumPages()
# print('Converting %d pages.' % npage)
# for p in range(npage):
#  im = PythonMagick.Image(pdffilename + '[' + str(p) +']')
#  im.density('300')
#  #im.read(pdffilename + '[' + str(p) +']')
#  im.write('file_out-' + str(p)+ '.png')
#  #print pdffilename + '[' + str(p) +']','file_out-' + str(p)+ '.png'



# # from wand.image import Image
# from PythonMagick import Image
#
# image_pdf = Image("C:/temp/oRxeC5q6BgOl.pdf")
# image_pdf.write("C:/temp/a")
# print(image_pdf.type)
# image_jpeg = image_pdf.convert('jpeg')


from pdf2image import convert_from_path
import tempfile
import PIL.Image as Image
import pytesseract

ocr_paths=[]

def main(filename, outputDir):
    print('filename=', filename)
    print('outputDir=', outputDir)
    with tempfile.TemporaryDirectory() as path:
        images = convert_from_path(filename)
        for index, img in enumerate(images):
            if index >2:
                break
            image_path='%s/page_%s.png' % (outputDir, index)
            ocr_paths.append(image_path)
            img.save(image_path)

def get_abs(text):
    print(text)
    abs_num=text.lower().find("abstract")
    if abs_num!=-1:
        keywords_num=text.lower().find("keywords")
        if keywords_num!=-1:
            return abs_clear(text[abs_num+8:keywords_num])
        else:
            # print(text)
            abs=""
            for section in get_sections(text[abs_num+8:]):
                if section.__len__()>500:
                    abs=section
                    break
                else:
                    abs+=section+"\n"
                    if abs.__len__()>500:
                        break
            return abs_clear(abs)
    else:
        for section in get_sections(text):

            if section.__len__()>500:
                num=section.rfind(".")
                if num >500:
                    return abs_clear(section[:num+1])

def get_sections(text):
    return text.split("\n\n")

def abs_clear(abs):
    abs=abs.strip()
    if abs[0] == ":":
        abs = abs[1:]
    print("last char:",abs[-1])
    if abs[-1] !="." and abs[-1] !="。":
        abs=abs+"."
    return abs

if __name__ == "__main__":
    print("a".isalpha())
    # main('C:/pdfs/jnav/3ab746ae5cbe11e987f500ac37466cf9.pdf', 'C:/temp')
    # for path in ocr_paths:
    #     print("===========",path)
    #     # print(pytesseract.image_to_string(path))
    #     print("+++++++++",get_abs(pytesseract.image_to_string(path,lang="jpn")))

