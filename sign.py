import os,sys,re
import pytesseract
from PIL import Image

def recogNumber( name ):
    img = Image.open(name) #type: Image.Image
    txt = recogNumberOfImage( img )
    print("num:%s of %s" %(txt,name) )
    return txt

def recogNumberOfImage( img ):
    box = (0,0,100,50)
    img = img.crop(box)
    txt = pytesseract.image_to_string(img)
    print("num:%s of image" %(txt) )
    return txt


def convert2Black(name):
    img_file = Image.open(name)
    img_file = img_file.convert('1') # convert image to black and white
    img_file.save(name)



def blackNoise(image):
    t2val={}

    # G: Integer 图像二值化阀值
    # N: Integer 降噪率 0 <N <8
    # Z: Integer 降噪次数
    G = 170
    Z=2
    N=4
    for y in range(0, image.size[1]):
        for x in range(0, image.size[0]):
            g = image.getpixel((x, y))
            if g > G :
                t2val[(x, y)] = 1
            else:
                t2val[(x, y)] = 0

    for i in range(0, Z):
        t2val[(0, 0)] = 1
        t2val[(image.size[0] - 1, image.size[1] - 1)] = 1

        for x in range(1, image.size[0] - 1):
            for y in range(1, image.size[1] - 1):
                nearDots = 0
                L = t2val[(x, y)]
                if L == t2val[(x - 1, y - 1)]:
                    nearDots += 1
                if L == t2val[(x - 1, y)]:
                    nearDots += 1
                if L == t2val[(x - 1, y + 1)]:
                    nearDots += 1
                if L == t2val[(x, y - 1)]:
                    nearDots += 1
                if L == t2val[(x, y + 1)]:
                    nearDots += 1
                if L == t2val[(x + 1, y - 1)]:
                    nearDots += 1
                if L == t2val[(x + 1, y)]:
                    nearDots += 1
                if L == t2val[(x + 1, y + 1)]:
                    nearDots += 1

                if nearDots < N:
                    t2val[(x, y)] = 1

    img = Image.new("1", image.size)
    draw = ImageDraw.Draw(img)

    for x in range(0, image.size[0]):
        for y in range(0, image.size[1]):
            draw.point((x, y), t2val[(x, y)])


    return img

def convert_Image(img, standard=127.5):

    image = img.convert('L')

    '''
    【二值化】
    根据阈值 standard , 将所有像素都置为 0(黑色) 或 255(白色), 便于接下来的分割
    '''
    pixels = image.load()
    for x in range(image.width):
        for y in range(image.height):
            if pixels[x, y] > standard:
                pixels[x, y] = 255
            else:
                pixels[x, y] = 0
    return image

def blackWhiteImage(name):
    # 新建Image对象 *.jpg
    img = Image.open(name)
    # 进行置灰处理
    img = img.convert('L')
    # 这个是二值化阈值
    threshold = 150
    table = []

    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    # 通过表格转换成二进制图片，1的作用是白色，不然就全部黑色了
    image = img.point(table, "1")
    return img

    # 下面是识别图片中的字
    # img.show()
    # result = pytesseract.image_to_text( img ) #lang="chs_sim"
    # print(result)
    # return result

def blackPNG(name):
    s = os.path.split(name)
    path = s[0]
    fns = s[1].split('.')
    basename = fns[0]
    img_file = Image.open(name)
    img_file = img_file.convert('1')  # convert image to black and white
    fn = os.path.join(path , basename )+".png"
    img_file.save(fn,"PNG")
    return fn




def transPNG(name):
    s = os.path.split(name)
    realpath = s[0]
    fn = s[1].split('.')
    basename = fn[0]
    ext = fn[-1]
    img = Image.open(name)
    img = img.convert("RGBA")
    datas = img.getdata()
    newData = list()
    for item in datas:
        if item[0] >200 and item[1] > 200 and item[2] > 200:
            newData.append(( item[0], item[1], item[2], 0))
        else:
            newData.append(item)
    
    img.putdata(newData)
    print( os.path.join(realpath,basename+"_trans.png") )
    img.save(os.path.join(realpath,basename+"_trans.png"),"PNG")

def transparent_back( name):
    s = os.path.split(name)
    fn = s[1].split('.')
    basename = fn[0]
    ext = fn[-1]
    img = Image.open(name)
    img = img.convert('RGBA')
    L, H = img.size
    color_0 = img.getpixel((0,0))
    for h in range(H):
        for l in range(L):
            dot = (l,h)
            color_1 = img.getpixel(dot)
            if color_1 == color_0:
                color_1 = color_1[:-1] + (0,)
                img.putpixel(dot,color_1)
    img.save(basename+"_trans.png","PNG")
    

def catchSign( name):
    img = Image.open(name)
    w,h = img.size
    print('Original image info: %sx%s, %s, %s' % (w, h, img.format, img.mode))
    s = os.path.split(name)
    realpath = s[0]
    fn = s[1].split('.')
    basename = fn[0]
    ext = fn[-1]
    top=116
    left = 29
    width =352
    height = 263
    box = (left,top,width,height)
    txt = os.path.join(realpath,basename +"_sign.png")
    img.crop(box).save(txt)
    # transparent_back(basename +"_sign.png")
    transPNG(txt)

numre =    re.compile(r"^\d+$")

def splitImage(src, rownum, colnum, dstpath):
    # 1024像素的毫米尺寸就是：1024/300*25.4  300dpi
    img = Image.open(src)
    w, h = img.size
    
    if rownum <= h and colnum <= w:
        print('Original image info: %sx%s, %s, %s' % (w, h, img.format, img.mode))
        print('开始处理图片切割, 请稍候...')

        s = os.path.split(src)
        realpath = s[0]
        if dstpath == '':
            dstpath = realpath
        fn = s[1].split('.')
        basename = fn[0]
        ext = fn[-1]
        top = 24
        left = 32.5
        num = 0
        outname=''
        rowheight = (h-24-66.1 )// rownum
        colwidth = (w-32.5-39.4) // colnum
        # rowheight = 380
        # colwidth = 410
        print("Width:%s Height:%s" % ( colwidth ,rowheight ))
        for r in range(rownum):
            for c in range(colnum):
                
                box = (left+c * colwidth, top+r * rowheight, (c + 1) * colwidth, (r + 1) * rowheight)
                print(box)
                print(os.path.join(realpath, basename + '_' + str(num) + '.' + ext))
                print("")
                
                img1 = img.crop(box)
                txt = recogNumberOfImage(img1)
                if ( numre.match(txt)):
                    outname=os.path.join( realpath, txt+"_"+basename + '_' + str(num) + '.' + ext )
                    img1.save(outname )
                    catchSign(outname)
                    num = num + 1

        print('图片切割完毕，共生成 %s 张小图片。' % num)
    else:
        print('不合法的行列切割参数！')

def inview():
    src = input('请输入图片文件路径：')
    if os.path.isfile(src):
        dstpath = input('请输入图片输出目录（不输入路径则表示使用源图片所在目录）：')
        if (dstpath == '') or os.path.exists(dstpath):
            row = int(input('请输入切割行数：'))
            col = int(input('请输入切割列数：'))
            if row > 0 and col > 0:
                splitImage(src, row, col, dstpath)
            else:
                print('无效的行列切割参数！')
        else:
            print('图片输出目录 %s 不存在！' % dstpath)
    else:
        print('图片文件 %s 不存在！' % src)

def testSign():
    # convert2Black("sign.jpg")
    splitImage("sign.jpg", 6, 4, '')

appPath = ""
patt =  re.compile(r"(.+?)\.tif$")
def processImg( filepath ):
    global appPath , imgPath
    print(filepath)
    imgPath = filepath
    if imgPath=="":
        appPath = os.path.split(os.path.realpath(__file__))[0]+"/"
        imgPath = appPath +"signimg/"

    path =  os.path.realpath(imgPath);
    filelist = ''
    try:
        filelist = os.listdir(imgPath)
    except:
        print("can not find the path [系统找不到指定的路径] %s" % ( imgPath ))
        return

    for filename in filelist:
        # filepath = os.path.join(path, filename)
        print(filename)
        pathfile =  os.path.join(path, filename)
        if os.path.isdir( pathfile):
            processImg(pathfile)
        else:
            if( patt.match(filename) ):
                pathfile = blackPNG(pathfile)
                splitImage(pathfile, 6, 4, '')



if(__name__=='__main__'):
    processImg('')
