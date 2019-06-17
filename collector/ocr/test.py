
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
import cv2

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

def create_box(pdf_path):
    path="C:/temp/box/"
    images = convert_from_path(pdf_path)
    for index, img in enumerate(images):
        image_path=path+"r"+str(index)+".png"
        img.save(image_path)
        image = cv2.imread(image_path)
        box = pytesseract.image_to_data(image)
        for line in box.split("\n"):
            # print(line)
            if "left" in line:
                continue
            args = line.split("\t")
            if int(args[3]) != 0:
                continue
            cv2.rectangle(image, (int(args[6]), int(args[7])),
                          (int(args[6]) + int(args[8]), int(args[7]) + int(args[9])), (255, 0, 0))
        cv2.imwrite(image_path, image)

if __name__ == "__main__":
    create_box("C:/pdfs/dynamic/1a2dd1fa5d0511e9a9ca00ac37466cf9.pdf")
    # # print("a".isalpha())
    # main('C:/temp/page_0.png', 'C:/temp')
    # # for path in ocr_paths:
    # #     print("===========",path)
    # #     # print(pytesseract.image_to_string(path))
    # #     print("+++++++++",get_abs(pytesseract.image_to_string(path)))
    # # print(pytesseract.image_to_string("C:/temp/page_0.png"))
    # box=pytesseract.image_to_data("C:/temp/page_0.png")
    # image=cv2.imread("C:/temp/page_0.png")
    #
    # print(type(box))
    # block_dict={}
    # for line in box.split("\n"):
    #     # print(line)
    #     if "left" in line:
    #         continue
    #     args=line.split("\t")
    #     if int(args[3])!=0:
    #         continue
    #
    #     # block_num=args[2]
    #     # num1=int(args[6])
    #     # num2=int(args[6])+int(args[8])
    #     # num3=int(args[7]
    #     # num4=args[2]
    #     cv2.rectangle(image,(int(args[6]),int(args[7])),(int(args[6])+int(args[8]),int(args[7])+int(args[9])),(255, 0, 0))
    #     # print(args.__len__())
    #
    # # cv2.imshow("Text Detection", image)
    # #
    # # cv2.waitKey(0)
    # cv2.imwrite("C:/temp/r1.png",image)
